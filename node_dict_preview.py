# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc
from pprint import pformat as _pformat

from frozendict import deepfreeze as _deepfreeze

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_common import _show_text_on_node, _verify_input_dict_into_new


def _to_regular_dict_recursive_copy(input_dict: dict = None) -> dict:
	"""
	To simplify preview, turns frozen dicts back to regular ones.
	Copies the dict in process and does so recursively, but not truly deep: if value is another dict,
	it will be processed, too. But dicts within other objects (like lists) won't be found.
	"""
	if not input_dict:
		return dict()
	return {
		k: (_to_regular_dict_recursive_copy(v) if isinstance(v, dict) else v)
		for k, v in input_dict.items()
	}


def _preview_single_entry(key: str, value) -> str:
	if isinstance(value, str):
		return f"{key}:\n{value}"
	value_repr = _pformat(value)
	return f"{key}:\n{value_repr}"


def _preview_message(input_dict: dict = None):
	input_dict = _to_regular_dict_recursive_copy(_verify_input_dict_into_new(input_dict))
	parts: _t.List[str] = [
		_preview_single_entry(k, v) for k, v in input_dict.items()
	]
	return '\n\n'.join(parts)

# --------------------------------------

_dict = dict

_input_types = _deepfreeze({
	'required': {},
	'optional': {
		'dict': _DataTypes.input_dict(tooltip="A Format-Dictionary."),
	},
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

	@staticmethod
	def main(
		dict: _t.Dict[str, _t.Any] = None,
		unique_id: str = None,
	):
		if dict is None:
			dict = _dict()
		if unique_id:
			status_text = _preview_message(dict)
			_show_text_on_node(status_text, unique_id)
		return (dict, )
