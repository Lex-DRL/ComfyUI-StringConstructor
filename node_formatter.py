# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc
import sys as _sys

from frozendict import deepfreeze as _deepfreeze

from comfy.comfy_types.node_typing import IO as _IO

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_common import _show_text_on_node, _verify_input_dict
# from .funcs_formatter import formatter as _formatter


_RECURSION_LIMIT = max(int(_sys.getrecursionlimit()), 1)  # You can externally monkey-patch it... but if it blows up, your fault 🤷🏻‍♂️


def _recursive_format(template: str, format_dict: _t.Dict[str, _t.Any], show: bool = True, unique_id: str = None) -> str:
	"""
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
		new = new.format_map(format_dict)
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

_dict = dict

_input_types = _deepfreeze({
	'required': {
		'template': (_IO.STRING, {'multiline': True, 'tooltip': (
			"Type the text template. "
			"To reference named substrings from format-dictionary, use this syntax: {substring_name}. For example:\n\n"
			"score_9, score_8_up, score_7_up, {char1_short}, standing next to {char2_short},\n"
			"{char1_long}\n{char2_long}"
		)}),
		'recursive_format': (_IO.BOOLEAN, {'default': False, 'label_on': '❗ yes', 'label_off': 'no', 'tooltip': (
			"Do recursive format - i.e., allow the chunks from the dictionary to reference other chunks - which in turn "
			"lets you do really crazy stuff like building entire HIERARCHIES of sub-prompts, all linked to the same "
			"wording typed in one place.\n\n"
			"The exclamation mark reminds you that with great power comes great responsibility!\n"
			"You can end up with chunks cross-referencing each other in a loop. In such case, the node will just error out "
			"and won't let you crash the entire ComfyUI - but still, it's your responsibility to prevent "
			"such looping dictionaries."
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
		template: str, recursive_format: bool = False, show_status: bool = False, dict: _t.Dict[str, _t.Any] = None,
		unique_id: str = None
	) -> _t.Tuple[str]:
		if dict is None:
			dict = _dict()
		_verify_input_dict(dict)
		if not isinstance(template, str):
			raise TypeError(f"Not a string: {template!r}")

		out_text = (
			_recursive_format(template, dict, show_status, unique_id)
			if recursive_format
			else template.format_map(dict)
		)
		if show_status and unique_id:
			_show_text_on_node(out_text, unique_id)
		return (out_text, )
