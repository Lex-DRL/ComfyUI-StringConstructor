# encoding: utf-8
"""
"""

import typing as _t

from inspect import cleandoc as _cleandoc

from frozendict import deepfreeze as _deepfreeze

from . import _meta
from .docstring_formatter import format_docstring as _format_docstring
from .enums import DataTypes as _DataTypes
from .funcs_common import _verify_input_dict, _show_text_on_node, _T


_input_types = _deepfreeze({
	'required': {
		'dict': _DataTypes.input_dict(),
	},
	# 'optional': {},
	# 'hidden': {
	# 	'unique_id': 'UNIQUE_ID',  # used for text display at the bottom of the node
	# },
})


class StringConstructorValidateKeys:
	"""
	Verify the dict to have string-formatting-compatible keys. No need to add it before "String Formatter" node,
	but it might be handy to verify the dict right after it's created.
	"""
	NODE_NAME = 'StringConstructorValidateKeys'
	CATEGORY = _meta.category_dict
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
		dict: _t.Dict[str, _T],
		# unique_id: str = None,
	) -> _t.Tuple[_t.Dict[str, _T]]:
		# try:
		# 	_verify_input_dict(dict, error_if_none=True)
		# except Exception:
		# 	_show_text_on_node('❌', unique_id)
		# 	raise
		# 	return (Null, )
		# _show_text_on_node('✅', unique_id)
		_verify_input_dict(dict, error_if_none=True)
		return (dict, )
