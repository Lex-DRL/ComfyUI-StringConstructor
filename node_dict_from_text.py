# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc

from frozendict import frozendict as _frozendict, deepfreeze as _deepfreeze

from comfy.comfy_types.node_typing import IO as _IO

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_dict_from_text import parse_dict_from_text as _parse_dict_from_text
from .node_dict_add_string import _input_types as _input_types_str


# A tiny optimization by reusing the same immutable dict:
_input_types = _deepfreeze({
	'required': {
		'cleanup': (_IO.BOOLEAN, {'default': True, 'label_on': 'leading/trailing spaces', 'label_off': 'no', 'tooltip': (
			"When enabled, each line in each sub-string is stripped from any spaces at its start and end."
		)}),
		'strings': (_IO.STRING, {'multiline': True, 'tooltip': (
			"Sub-string names followed by their text. Different sub-string chunks are separated by empty lines. Example:\n\n"
			"char1_short\n1boy, blond, short hair\n\n"
			"char1_long\n1boy, smiling, blue eyes, blond, short hair,\nsitting on a motorcycle, wearing a leather jacket"
		)}),
		'show_status': (_IO.BOOLEAN, {'default': False, 'label_on': 'found names', 'label_off': 'no', 'tooltip': (
			"Show detected string names on the node itself?"
		)}),
	},
	'optional': {
		'str_dict': _input_types_str['optional']['str_dict'],
	},
	'hidden': {
		'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	},
})


class StringConstructorDictFromText:
	"""
	Build a dict of named sub-strings to be used later in string formatting (text construction).
	"""
	NODE_NAME = 'StringConstructorDictFromText'
	CATEGORY = _meta.category
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	OUTPUT_NODE = True  # Just to show the status message even if not connected to anything

	FUNCTION = 'main'
	RETURN_TYPES = (_DataTypes.STR_DICT, )
	RETURN_NAMES = (_DataTypes.STR_DICT.lower(), )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	def main(
		self, cleanup: bool, strings: str, show_status: bool,
		str_dict: _t.Dict[str, _t.Any] = None,
		unique_id: str = None,
	):
		return _parse_dict_from_text(strings, strip_lines=cleanup, show=show_status, in_dict=str_dict, unique_id=unique_id)
