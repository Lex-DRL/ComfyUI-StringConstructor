# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc

from frozendict import deepfreeze as _deepfreeze

from comfy.comfy_types.node_typing import IO as _IO

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_formatter import formatter as _formatter


# A tiny optimization by reusing the same immutable dict:
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

	def main(
		self, template: str, recursive_format: bool, show_status: bool,
		dict: _t.Dict[str, _t.Any] = None,
		unique_id: str = None,
	):
		return _formatter(template, recursive_format, dict, show=show_status, unique_id=unique_id)
