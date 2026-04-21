# encoding: utf-8
"""
The main class which actually does all the job for Formatter-node.
"""

from dataclasses import dataclass as _dataclass, field as _field
import re as _re
import sys as _sys

from .__typing import _A, _U, _O, _t, T as _T, FormatDict as _FormatDict
from ._dict import _verify_input_dict


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
class Formatter:
	"""
	A callable (function-like) class, which does the actual formatting, while respecting all the options.

	It's made as a class to split the formatting into two stages:
	- First, the instance is properly initialized with the shared arguments (the methods to call are conditionally assigned depending on options);
	- Then, the actual instance is treated as a function - it needs to be called with the formatted string as the only argument.

	It's done this way to avoid extra conditions in the loop + to organize the convoluted mess of intertwined functions
	into a more readable code.
	"""
	format_dict: _O[_FormatDict] = None

	recursive: bool = False
	safe: bool = True

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
		if prev == new:
			return new

		for i in range(_RECURSION_LIMIT):
			prev = new
			new = format_single_func(new)
			if prev == new:
				return new

		msg = (
			f"Recursion limit ({_RECURSION_LIMIT}) reached on attempt to format a string: {template!r}\n"
			f"Last two formatting attempts:\n{prev!r}\n{new!r}"
		)
		raise RecursionError(msg)
		# noinspection PyUnreachableCode
		return ''  # just to be extra-safe, if RecursionError is treated as warning

	def __call__(self, template: str) -> str:
		if not isinstance(template, str):
			raise TypeError(f"Not a string: {template!r}")
		return self._format(template) if template else ''
