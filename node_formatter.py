# encoding: utf-8
"""
Code for ``StringConstructorFormatter`` node.
"""

import typing as _t

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


def _safe_format(template: str, format_dict: _t.Dict[str, _t.Any]) -> str:
	"""
	Safe format that only replaces variables that exist in the dictionary.
	Leaves other curly brackets untouched.
	"""
	if not format_dict:
		return template
	
	# Create pattern that matches {key} only for keys that exist in format_dict
	pattern = r'\{(' + '|'.join(_re.escape(key) for key in format_dict.keys()) + r')\}'
	
	def replace_func(match):
		key = match.group(1)
		return str(format_dict[key])
	
	return _re.sub(pattern, replace_func, template)


def _escape_unknown_brackets(template: str, format_dict: _t.Dict[str, _t.Any]) -> str:
	"""
	Escape curly brackets that aren't format variables, then use normal format.
	This approach preserves the original behavior for known variables.
	"""
	if not format_dict:
		# If no format dict, escape all curly brackets
		return template.replace('{', '{{').replace('}', '}}')
	
	# Find all {word} patterns
	pattern = r'\{([^{}]*)\}'
	known_keys = set(format_dict.keys())
	
	def escape_func(match):
		key = match.group(1)
		if key in known_keys:
			return match.group(0)  # Keep as is for formatting
		else:
			return '{{' + key + '}}'  # Escape unknown
	
	escaped_template = _re.sub(pattern, escape_func, template)
	return escaped_template.format_map(format_dict)


def _recursive_format_safe(
	template: str, format_dict: _t.Dict[str, _t.Any],
	show: bool = True, unique_id: str = None, use_safe_mode: bool = True
) -> str:
	"""
	Safe recursive format that won't break on unknown curly brackets.

	It's not actually recursive - because, you know, any recursion could be turned into iteration,
	and good boys do that. 😊
	"""
	assert isinstance(_RECURSION_LIMIT, int) and _RECURSION_LIMIT > 0

	prev: str = ''
	new: str = template
	for i in range(_RECURSION_LIMIT):
		if prev == new:
			break
		prev = new
		
		if use_safe_mode:
			new = _safe_format(new, format_dict)
		else:
			# Use the escape approach for compatibility with original behavior
			new = _escape_unknown_brackets(new, format_dict)
	
	if prev == new:
		return new

	msg = (
		f"Recursion limit ({_RECURSION_LIMIT}) reached on attempt to format a string: {template!r}\n"
		f"Last two formatting attempts:\n{prev!r}\n{new!r}"
	)
	if show and unique_id:
		_show_text_on_node(msg, unique_id)
	raise RecursionError(msg)
	# noinspection PyUnreachableCode
	return ''  # just to be safe

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
		'safe_mode': (_IO.BOOLEAN, {'default': True, 'label_on': 'safe', 'label_off': 'escape', 'tooltip': (
			"Safe mode: Only format known variables, leave unknown {brackets} as-is.\n"
			"Escape mode: Escape unknown {brackets} to {{brackets}} then format normally.\n"
			"Safe mode is recommended for templates with JSON, CSS, or other literal curly brackets."
		)}),
		'show_status': (_IO.BOOLEAN, {'default': True, 'label_on': 'formatted string', 'label_off': 'no', 'tooltip': (
			"Show the final string constructed from the text-template and format-dictionary?"
		)}),
	},
	'optional': {
		'dict': _DataTypes.input_dict(tooltip=(
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
		safe_mode: bool = True,
		show_status: bool = False,
		dict: _t.Dict[str, _t.Any] = None,
		unique_id: str = None
	) -> _t.Tuple[str]:
		if dict is None:
			dict = {}
		_verify_input_dict(dict)
		if not isinstance(template, str):
			raise TypeError(f"Not a string: {template!r}")

		if recursive_format:
			out_text = _recursive_format_safe(template, dict, show_status, unique_id, safe_mode)
		else:
			if safe_mode:
				out_text = _safe_format(template, dict)
			else:
				out_text = _escape_unknown_brackets(template, dict)
		
		if show_status and unique_id:
			_show_text_on_node(out_text, unique_id)
		return (out_text, )
