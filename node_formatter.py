# encoding: utf-8
"""
Code for ``StringConstructorFormatter`` node.
"""

import typing as _t

from dataclasses import dataclass as _dataclass
from inspect import cleandoc as _cleandoc
import re as _re
import sys as _sys

from frozendict import deepfreeze as _deepfreeze

from comfy.comfy_types.node_typing import IO as _IO

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_common import _show_text_on_node, _verify_input_dict


_RECURSION_LIMIT = max(int(_sys.getrecursionlimit()), 1)  # You can externally monkey-patch it... but if it blows up, your fault 🤷🏻‍♂️

def _n_brackets_after_escape_for_existing_key(n_brackets: int):
	"""
	Calculate the updated number of braces before/after the pattern.
	Keeps the innermost set of brackets as-is for formatting,
	but doubles all the leading/trailing brackets to escape them.
	"""
	n_extra = max(n_brackets - 1, 0)
	return n_extra * 2 + 1


def _rebuild_parsed_keyword(n_opening_brackets: int, inside_brackets: str, n_closing_brackets: int) -> str:
	# According to "Beautiful/ideomatic python" lecture, string formatting is faster than other forms of concatenation
	return '{}{}{}'.format(
		'{' * n_opening_brackets,
		inside_brackets,
		'}' * n_closing_brackets
	)


_re_formatting_keyword_sub = _re.compile(  # Pre-compiled regex-sub func to find and replace {keyword} patterns
	r'(\{+)([^{}]*)(\}+)'
	# TODO: Takes leading/trailing braces into account, but not nested ones. Maybe implement some day,
	#  but it would require true parsing - with stack of braces, nested parts iterator, etc.
).sub


@_dataclass
class _Formatter:
	"""
	A callable (function-like) class, which does the actual formatting, while respecting all the options.

	It's made as a class to split the formatting into two stages:
	- First, the instance is properly initialized with the shared arguments (all the method overrides are made depending on options);
	- Then, the actual instance is treated as a function - it needs to be called with the formatted string as the only argument.

	It's done this way to avoid extra conditions in the loop + to organize all the setup work in one place.
	"""
	format_dict: _t.Optional[_t.Dict[str, _t.Any]] = None

	recursive: bool = False
	safe: bool = True

	show_status: bool = True
	unique_node_id: str = None

	def __post_init__(self):  # called by dataclass init
		if self.format_dict is None:
			self.format_dict = dict()

		format_dict = self.format_dict
		_verify_input_dict(format_dict)
		if not format_dict:
			self.__escape_match = self.__escape_match_no_keys

		# No need to override _escape_for_safe_format().
		# Instead, recursive method defines local function, and simple method just checks self.safe mode in-place.

		self._format = self.__format_recursive if self.recursive else self.__format_simple

	# @staticmethod
	# def __dummy_return_intact(template: str) -> str:
	# 	return template

	def __escape_match(self, match: _re.Match[str]) -> str:
		opening_brackets, inside_brackets, closing_brackets = match.groups()
		if inside_brackets.strip() in self.format_dict:
			n_opening = _n_brackets_after_escape_for_existing_key(len(opening_brackets))
			n_closing = _n_brackets_after_escape_for_existing_key(len(closing_brackets))
			return _rebuild_parsed_keyword(n_opening, inside_brackets, n_closing)
		else:
			return _rebuild_parsed_keyword(len(opening_brackets) * 2, inside_brackets, len(closing_brackets) * 2)

	@staticmethod
	def __escape_match_no_keys(match: _re.Match[str]) -> str:
		opening_brackets, inside_brackets, closing_brackets = match.groups()
		return _rebuild_parsed_keyword(len(opening_brackets) * 2, inside_brackets, len(closing_brackets) * 2)

	def _escape_for_safe_format(self, template: str) -> str:
		"""
		Method to be called in safe mode - on template, before the actual format.

		Safe mode only replaces variables that exist in the dictionary. Leaves other curly brackets untouched.
		"""
		return _re_formatting_keyword_sub(self.__escape_match, template)

	def __format_simple(self, template: str) -> str:
		if self.safe:
			template = self._escape_for_safe_format(template)
		return template.format_map(self.format_dict)

	def __format_recursive(self, template: str) -> str:
		"""
		It's not actually recursive - because, you know, any recursion could be turned into iteration,
		and good boys do that. 😊
		"""
		assert isinstance(_RECURSION_LIMIT, int) and _RECURSION_LIMIT > 0

		# Cache before loop - to avoid even 'dot' operator
		escape_func = self._escape_for_safe_format
		format_dict: _t.Dict[str, _t.Any] = self.format_dict

		# The following two funcs defined here instead of method overrides - to simplify their local scope:

		def format_single_with_escape(_template: str):
			_template = escape_func(_template)
			return _template.format_map(format_dict)

		def format_single_no_escape(_template: str):
			return _template.format_map(format_dict)

		format_single_func = format_single_with_escape if self.safe else format_single_no_escape

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

	@staticmethod
	def _format(template: str) -> str:
		raise NotImplementedError("This method should always be overridden after initialization.")

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
			"{char1_long}\n{char2_long}\n\n"
			"Curly brackets that don't match dictionary keys will be handled according to the sanitization mode."
		)}),
		'recursive_format': (_IO.BOOLEAN, {'default': False, 'label_on': '❗ yes', 'label_off': 'no', 'tooltip': (
			"Do recursive format - i.e., allow the chunks from the dictionary to reference other chunks."
		)}),
		'safe_format': (_IO.BOOLEAN, {'default': True, 'label_on': 'yes', 'label_off': 'no', 'tooltip': (
			"Safe mode: If a specific {keyword} doesn't exist in the dict, leave it as-is.\n"
			"On: missing {keywords} preserved intact.\n"
			"Off: missing {keywords} raise an error.\n\n"
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
