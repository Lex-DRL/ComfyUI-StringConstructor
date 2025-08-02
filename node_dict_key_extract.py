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
from .funcs_common import _show_text_on_node, _new_dict_with_updated_key, _T


_input_types = _deepfreeze({
	'required': {
		'name': (_IO.STRING, {'tooltip': (
			"Name (key) of a string to extract from dictionary.\n"
			"If the element with such key isn't a string, it will be turned to one.\n"
			"If no such key exists in the dict, an empty string returned."
		)}),
		'show_status': (_IO.BOOLEAN, {'default': False, 'label_on': 'value', 'label_off': 'no', 'tooltip': (
			"Show the extracted string on the node itself?"
		)}),
	},
	'optional': {
		'dict': _DataTypes.input_dict(tooltip="The dictionary to extract the element from."),
	},
	'hidden': {
		'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	},
})


class StringConstructorDictExtractString:
	"""Extract a single string from the Format-Dict."""
	NODE_NAME = 'StringConstructorDictExtractString'
	CATEGORY = _meta.category_dict
	DESCRIPTION = _format_docstring(_cleandoc(__doc__))

	FUNCTION = 'main'
	RETURN_TYPES = (_IO.STRING, )
	RETURN_NAMES = ('string', )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	@staticmethod
	def main(
		name: str, show_status: bool = False, dict: _t.Dict[str, _T] = None,
		unique_id: str = None,
	) -> _t.Tuple[str]:
		"""Extract a single string from the Format-Dict."""
		# noinspection PyBroadException
		try:
			string: str = dict.get(name, '')
		except Exception:
			string = ''
		if string is None:
			string = ''

		if not isinstance(string, str):
			string = repr(string)

		if show_status and unique_id:
			_show_text_on_node(string, unique_id)

		return (string, )
