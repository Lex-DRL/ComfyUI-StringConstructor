# encoding: utf-8
"""Code for the dict-validator node."""

from inspect import cleandoc as _cleandoc

from comfy_api.latest import io as _io

from .__meta import (
	category as _category,
	pack_id_suffix as _pack_id
)
from .__typing import _A, _U, _O, _t, T as _T, FormatDict as _FormatDict
from ._dict import _verify_input_dict
from ._io_custom import (
	_BaseNode,
	_DICT_INPUT_OPTIONAL, _DICT_OUTPUT,
	_schema_old_name
)
from .docstring_formatter import format_docstring as _format_docstring

# ----------------------------------------------------------

class ValidateKeys(_BaseNode):
	"""
	Verify the dict to have string-formatting-compatible keys. No need to add it before "String Formatter" node,
	but it might be handy to verify the dict in the very beginning of the graph - right after the keys are set.
	"""
	_schema = _io.Schema(
		node_id=f'ValidateKeys{_pack_id}',
		display_name='Validate Dict',
		category=_category,
		description=_format_docstring(_cleandoc(__doc__)),
		inputs=[_DICT_INPUT_OPTIONAL],
		outputs=[_DICT_OUTPUT],
		# hidden=[_io.Hidden.unique_id],
		is_output_node=True,
	)

	@classmethod
	def execute(cls, dict: _O[_FormatDict] = None) -> _io.NodeOutput:
		# try:
		# 	_verify_input_dict(dict, error_if_none=True)
		# except Exception:
		# 	_show_text_on_node('❌', unique_id)
		# 	raise
		# 	return (Null, )
		# _show_text_on_node('✅', unique_id)
		_verify_input_dict(dict, error_if_none=True)
		return _io.NodeOutput(dict)

# ==========================================================
# Deprecated node with old ID (for backwards compatibility)

class ValidateKeysOld1(ValidateKeys):
	_schema = _schema_old_name(
		ValidateKeys._schema,
		'StringConstructorValidateKeys'
	)
