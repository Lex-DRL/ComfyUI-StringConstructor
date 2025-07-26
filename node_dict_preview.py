# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc

from frozendict import deepfreeze as _deepfreeze

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_dict_preview import preview_str_dict as _preview_str_dict


# A tiny optimization by reusing the same immutable dict:
_input_types = _deepfreeze({
	'required': {
		'dict': _DataTypes.input_dict(tooltip="A Format-Dictionary."),
	},
	# 'optional': {},
	'hidden': {
		'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	},
})


class StringConstructorDictPreview:
	"""
	Show the contents of a Format-Dict.
	"""
	NODE_NAME = 'StringConstructorDictPreview'
	CATEGORY = _meta.category
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	OUTPUT_NODE = True

	FUNCTION = 'main'
	RETURN_TYPES = (str(_DataTypes.DICT), )
	RETURN_NAMES = (_DataTypes.DICT.lower(), )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	def main(
		self, dict: _t.Dict[str, _t.Any],
		unique_id: str = None,
	):
		return _preview_str_dict(dict, unique_id=unique_id)
