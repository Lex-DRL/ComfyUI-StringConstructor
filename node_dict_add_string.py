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
from .funcs_dict_add_string import set_dict_string as _set_dict_string


# A tiny optimization by reusing the same immutable dict:
_input_types = _deepfreeze({
	'required': {
		'name': (_IO.STRING, {'tooltip': (
			"Name of the substring inserted into the dict. "
			"It must comprise only of latin letters, digits and underscores + it can't start with a digit."
		)}),
		'cleanup': (_IO.BOOLEAN, {'default': True, 'label_on': 'leading/trailing spaces', 'label_off': 'no', 'tooltip': (
			"When enabled, each line in the sub-string is stripped from any spaces at its start and end."
		)}),
		'string': (_IO.STRING, {'multiline': True, 'tooltip': "The actual sub-string to add into the dict."}),
	},
	'optional': {
		'str_dict': _DataTypes.input_str_dict(tooltip="An optional Format-Dictionary to extend/update."),
	},
	# 'hidden': {
	# 	'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	# },
})


class StringConstructorDictAddString:
	"""Add/update a string to the Format-Dict."""
	NODE_NAME = 'StringConstructorDictAddString'
	CATEGORY = _meta.category
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	FUNCTION = 'main'
	RETURN_TYPES = (_DataTypes.STR_DICT, )
	RETURN_NAMES = (_DataTypes.STR_DICT.lower(), )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	def main(
		self, name: str, cleanup: bool, string: str,
		str_dict: _t.Dict[str, _t.Any] = None,
		# unique_id: str = None,
	):
		return _set_dict_string(name, string, strip_lines=cleanup, in_dict=str_dict)
