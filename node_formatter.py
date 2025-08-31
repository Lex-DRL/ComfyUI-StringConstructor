# encoding: utf-8
"""
Code for ``StringConstructorFormatter`` node.
"""

import typing as _t

from dataclasses import dataclass as _dataclass, field as _field
from inspect import cleandoc as _cleandoc
import re as _re
import sys as _sys

from frozendict import deepfreeze as _deepfreeze

from comfy.comfy_types.node_typing import IO as _IO

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_common import _show_text_on_node, _verify_input_dict


_RECURSION_LIMIT = max(int(_sys.getrecursionlimit()), 1)  # You can externally monkey-patch it... but if it blows up, your fault 🤷🏻‍♂️single

__dataclass_slots_args = dict() if _sys.version_info < (3, 10) else dict(slots=True)

_re_formatting_keyword_match = _re.compile(  # Pre-compiled regex match to extract ``{keyword}`` patterns
	r'(?P<prefix>.*?)'
	r'(?P<open_brackets>\{+)'
	r'(?P<inside_brackets>[^{}]+)'
	r'(?P<closed_brackets>\}+)'
	r'(?P<suffix>[^{}].*)?$',
	# flags=_re.DOTALL | _re.IGNORECASE,
	flags = _re.DOTALL,  # We need dot to match new lines, too
).match


@_dataclass(**__dataclass_slots_args)
class _Formatter:
	"""
	A callable (function-like) class, which does the actual formatting, while respecting all the options.

	It's made as a class to split the formatting into two stages:
	- First, the instance is properly initialized with the shared arguments (the methods to call are conditionally assigned depending on options);
	- Then, the actual instance is treated as a function - it needs to be called with the formatted string as the only argument.

	It's done this way to avoid extra conditions in the loop + to organize the convoluted mess of intertwined functions
	into a more readable code.
	"""
	format_dict: _t.Optional[_t.Dict[str, _t.Any]] = None

	recursive: bool = False
	safe: bool = True

	show_status: bool = True
	unique_node_id: str = None

	__format_single: _t.Callable[[str], str] = _field(init=False, repr=False, compare=False, default=lambda x: x)
	_format: _t.Callable[[str], str] = _field(init=False, repr=False, compare=False, default=lambda x: x)

	def __post_init__(self):  # called by dataclass init
		if self.format_dict is None:
			self.format_dict = dict()

		format_dict = self.format_dict
		_verify_input_dict(format_dict)
		self.__format_single = self.__format_single_safe if self.safe else self.__format_single_unsafe

		if format_dict:
			self._format = self.__format_recursive if self.recursive else self.__format_single
		else:
			self._format = self.__dummy_return_intact

	@staticmethod
	def __dummy_return_intact(template: str) -> str:
		return template

	def __format_single_unsafe(self, template: str):
		return template.format_map(self.format_dict)

	def __format_single_safe_parts_gen(self, template: str) -> _t.Generator[str, None, None]:
		"""
		EAFP: https://docs.python.org/3/glossary.html#term-EAFP

		Instead of pre-escaping the whole template
		(which would require basically re-implementing the entire format-parsing logic),
		let's extract individual formatted pieces, actually try formatting them one by one,
		and return anything that cannot be formatted as-is - without any processing at all.

		This generator returns such pieces - formatted or intact.
		"""
		format_dict = self.format_dict
		to_piece_template = '{{{}}}'.format

		suffix: str = template
		while suffix:
			match = _re_formatting_keyword_match(suffix)
			if not match:
				break

			prefix = match.group('prefix')
			open_brackets = match.group('open_brackets')
			inside_brackets = match.group('inside_brackets')
			closed_brackets = match.group('closed_brackets')
			suffix = match.group('suffix')

			if prefix:
				yield prefix

			piece_template = to_piece_template(inside_brackets)
			# noinspection PyBroadException
			try:
				formatted_piece = piece_template.format_map(format_dict)
			except Exception:
				# If, for ANY reason, we're unable to format the piece, return the template piece intact:
				yield open_brackets
				yield inside_brackets
				yield closed_brackets
				continue

			# The key is found. Treat the piece as the actual formatting pattern.
			# Formatting "eats" one set of brackets either way:
			open_brackets = open_brackets[:-1]
			closed_brackets = closed_brackets[:-1]

			# Now, even though we've succeeded, the template might've been pre-escaped.
			if open_brackets and closed_brackets:
				# The keyword is already pre-escaped. Return it intact:
				formatted_piece = inside_brackets

			yield open_brackets
			yield formatted_piece
			yield closed_brackets

		if suffix:
			yield suffix

	def __format_single_safe(self, template: str) -> str:
		"""
		Format the pattern (single iteration of formatting) in the safe mode.
		Safe mode preserves any unknown ``{text patterns}`` inside curly brackets if they cannot be formatted.
		Correctly handles any formatting patterns natively supported by python
		(even the most fancy ones, involving ':', '!', attribute or index access, etc.).

		Useful when JSON/CSS-like code is in the formatted template.
		"""
		return ''.join(self.__format_single_safe_parts_gen(template))

	def __format_recursive(self, template: str) -> str:
		"""
		It's not actually recursive - because, you know, any recursion could be turned into iteration,
		and good boys do that. 😊
		"""
		assert isinstance(_RECURSION_LIMIT, int) and _RECURSION_LIMIT > 0

		format_single_func = self.__format_single

		prev: str = ''
		new: str = template
		for i in range(_RECURSION_LIMIT):
			if prev == new:
				return new
			prev = new
			new = format_single_func(new)

		msg = (
			f"Recursion limit ({_RECURSION_LIMIT}) reached on attempt to format a string: {template!r}\n"
			f"Last two formatting attempts:\n{prev!r}\n{new!r}"
		)
		if self.show_status and self.unique_node_id:
			_show_text_on_node(msg, self.unique_node_id)
		raise RecursionError(msg)
		# noinspection PyUnreachableCode
		return ''  # just to be extra-safe, if RecursionError is treated as warning

	def __call__(self, template: str) -> str:
		if not isinstance(template, str):
			raise TypeError(f"Not a string: {template!r}")

		out_text = self._format(template) if template else ''
		if self.show_status and self.unique_node_id:
			_show_text_on_node(out_text, self.unique_node_id)
		return out_text

# --------------------------------------

_input_types = _deepfreeze({
	'required': {
		'template': (_IO.STRING, {'multiline': True, 'tooltip': (
			"Type the text template. "
			"To reference named substrings from format-dictionary, use this syntax: {substring_name}. For example:\n\n"
			"score_9, score_8_up, score_7_up, {char1_short}, standing next to {char2_short},\n"
			"{char1_long}\n{char2_long}"
		)}),
		'recursive_format': (_IO.BOOLEAN, {'default': False, 'label_on': '❗ yes', 'label_off': 'no', 'tooltip': (
			"Do recursive format - i.e., allow the chunks from the dictionary to reference other chunks."
		)}),
		'safe_format': (_IO.BOOLEAN, {'default': True, 'label_on': 'yes', 'label_off': 'no', 'tooltip': (
			"If template contains an invalid {text pattern} which can't be formatted - leave it as-is "
			"(instead of throwing an error).\n"
			"Safe mode is recommended for templates with JSON, CSS, or other literal curly brackets."
		)}),
		'show_status': (_IO.BOOLEAN, {'default': True, 'label_on': 'formatted string', 'label_off': 'no', 'tooltip': (
			"Show the final string constructed from the text-template and format-dictionary?"
		)}),
	},
	'optional': {
		'dict': _DataTypes.input_dict(tooltip=(  # It's not actually optional, but is here since there's no dict-widget
			"The dictionary to take named sub-strings from. It could be left unconnected, if the pattern doesn't reference "
			"any sub-strings - then, this node acts exactly the same as a regular string-primitive node."
		)),
	},
	'hidden': {
		'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	},
})


class StringConstructorFormatter:
	"""
	Construct the formatted string from template and format-dictionary.
	"""
	NODE_NAME = 'StringConstructorFormatter'
	CATEGORY = _meta.category
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	OUTPUT_NODE = True

	FUNCTION = 'main'
	RETURN_TYPES = (_IO.STRING, )
	RETURN_NAMES = ('string', )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	@staticmethod
	def main(
		template: str,
		recursive_format: bool = False,
		safe_format: bool = True,
		show_status: bool = False,
		dict: _t.Dict[str, _t.Any] = None,  #actually, required - but it's here to keep the declared params order
		unique_id: str = None
	) -> _t.Tuple[str]:
		formatter = _Formatter(
			format_dict=dict,
			recursive=recursive_format, safe=safe_format,
			show_status=show_status, unique_node_id=unique_id,
		)
		out_text = formatter(template)
		return (out_text, )
