# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorDictPreview` node.
"""

import typing as _t

from pprint import pformat as _pformat

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


def preview_str_dict(input_dict: dict, unique_id: str = None):
	if not unique_id:
		return (input_dict, )
	status_text = _preview_message(input_dict)
	_show_text_on_node(status_text, unique_id)
	return (input_dict, )
