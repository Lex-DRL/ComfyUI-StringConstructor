# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorDictFromText` node.
"""

import typing as _t

from frozendict import frozendict as _frozendict, deepfreeze as _deepfreeze

from .enums import T as _T
from .funcs_common import _show_text_on_node, _raise_from_errors_dict, _validate_key, _verify_input_dict_into_new


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


def parse_dict_from_text(
	multiline_str: str, strip_lines=True,
	show: bool = True, in_dict: _t.Dict[str, _T] = None, unique_id: str = None
) -> _t.Tuple[_t.Dict[str, _T]]:
	out_dict: _t.Dict[str, _T] = _verify_input_dict_into_new(in_dict)

	errors_dict: _t.Dict[_t.Any, str] = dict()
	new_dict: _t.Dict[str, str] = {
		_k: _v for _k, _v in (
			(_validate_key(k, errors_dict), v)
			for k, v in _parsed_kv_pairs_gen(multiline_str, strip_lines=strip_lines)
		) if _k is not None
	}
	_raise_from_errors_dict(errors_dict)

	out_dict.update(new_dict)

	if show and unique_id:
		status_text = ','.join(new_dict.keys()) if new_dict else ''
		_show_text_on_node(status_text, unique_id)

	return (_deepfreeze(out_dict), )
