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
from .funcs_common import _show_text_on_node, _new_updated_dict, _T
from .node_dict_add_string import _input_types as _input_types_str


def _return_line_raw(line_raw: str, line_stripped:str) -> str:
	return line_raw


def _return_line_stripped(line_raw: str, line_stripped:str) -> str:
	return line_stripped


def _parsed_kv_pairs_gen(multiline_str: str, strip_lines=True):
	"""
	Given a multiline string, extract keywords (first non-empty line in each chunk)
	and their substrings (all the following non-empty lines).
	"""
	if not multiline_str:
		return
	multiline_str = str(multiline_str)
	if not multiline_str.strip():
		return

	appended_line_f = _return_line_stripped if strip_lines else _return_line_raw
	cur_chunk: _t.List[str] = list()

	def dump_chunk():
		cur_chunk_iter = iter(cur_chunk)  # It's more backwards-compatible than `a, *b = x`
		chunk_key = next(cur_chunk_iter)
		cur_chunk_lines = list(cur_chunk_iter)
		# If there are no actual lines, join() would return an empty string:
		return chunk_key.strip(), '\n'.join(cur_chunk_lines)

	for line in multiline_str.splitlines():
		line_stripped: str = line.strip()
		if line_stripped:
			cur_chunk.append(appended_line_f(line, line_stripped))
			continue

		assert not line_stripped
		if cur_chunk:
			yield dump_chunk()
			cur_chunk = list()

		# We simply skip all the empty lines entirely

	if cur_chunk:
		yield dump_chunk()

# --------------------------------------

_dict = dict

_input_types = _deepfreeze({
	'required': {
		'cleanup': (_IO.BOOLEAN, {'default': True, 'label_on': 'leading/trailing spaces', 'label_off': 'no', 'tooltip': (
			"When enabled, each line in each sub-string is stripped from any spaces at its start and end."
		)}),
		'strings': (_IO.STRING, {'multiline': True, 'tooltip': (
			"Sub-string names followed by their text. Different sub-string chunks are separated by empty lines. Example:\n\n"
			"char1_short\n1boy, blond, short hair\n\n"
			"char1_long\n1boy, smiling, blue eyes, blond, short hair,\nwearing a leather jacket, sitting on a bike"
		)}),
		'show_status': (_IO.BOOLEAN, {'default': False, 'label_on': 'detected names', 'label_off': 'no', 'tooltip': (
			"Show detected string names on the node itself?"
		)}),
	},
	'optional': {
		'dict': _input_types_str['optional']['dict'],
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
	RETURN_TYPES = (str(_DataTypes.DICT), )
	RETURN_NAMES = (_DataTypes.DICT.lower(), )
	# OUTPUT_TOOLTIPS = tuple()

	@classmethod
	def INPUT_TYPES(cls):
		return _input_types

	@staticmethod
	def main(
		cleanup: bool, strings: str, show_status: bool = True,
		dict: _t.Dict[str, _T] = None, unique_id: str = None,
	) -> _t.Tuple[_t.Dict[str, _t.Union[_T, str]]]:
		new_dict = {k: v for k, v in _parsed_kv_pairs_gen(strings, strip_lines=cleanup)}

		if not new_dict:
			if dict is None:
				dict = _dict()
			return (dict, )  # No need to create another dict instance if we add nothing

		out_dict = _new_updated_dict(dict, new_dict)
		# These two ↑↓ must be in this specific order: `_new_updated_dict()` also checks both dicts
		if show_status and unique_id:
			status_text = ','.join(new_dict.keys()) if new_dict else ''
			_show_text_on_node(status_text, unique_id)

		return (out_dict, )
