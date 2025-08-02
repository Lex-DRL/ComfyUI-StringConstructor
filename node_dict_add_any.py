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
from .funcs_common import _new_dict_with_updated_key
from .node_dict_add_string import _input_types as _input_types_str


_dict = dict

# A tiny optimization by reusing the same immutable dict:
_input_types = _deepfreeze({
	'required': {
		'name': (_IO.STRING, {'tooltip': (
			"Name of the non-string item inserted into the dict. "
			"It must comprise only of latin letters, digits and underscores + it can't start with a digit."
		)}),
	},
	'optional': {
		'dict': _input_types_str['optional']['dict'],
		'value': (_IO.ANY, {"forceInput": True, 'tooltip': "The actual non-string item to add into the dict."}),
	},
	# 'hidden': {
	# 	'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	# },
})


class StringConstructorDictAddAny:
	"""Add/update a non-string item to the Format-Dict - to do some advanced formatting."""
	NODE_NAME = 'StringConstructorDictAddAny'
	CATEGORY = _meta.category_dict
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	FUNCTION = 'main'
	RETURN_TYPES = (str(_DataTypes.DICT), )
	RETURN_NAMES = (_DataTypes.DICT.lower(), )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	@staticmethod
	def main(
		name: str, dict: _t.Dict[str, _t.Any] = None, value: _t.Any = None,
		# unique_id: str = None,
	) -> _t.Tuple[_t.Dict[str, _t.Any]]:
		"""Update/append an item of any type to the dict."""
		if value is None:
			if dict is None:
				dict = _dict()
			return (dict, )  # No need to create another dict instance if we add nothing
		return (_new_dict_with_updated_key(dict, name, value), )
