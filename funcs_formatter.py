# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorFormatter` node.
"""

import typing as _t

import sys as _sys

from .funcs_common import _show_text_on_node, _verify_input_dict


_RECURSION_LIMIT = max(int(_sys.getrecursionlimit()), 10)  # You can externally monkey-patch it... but if it blows up, your fault 🤷🏻‍♂️


def _recursive_format(template: str, format_dict: _t.Dict[str, _t.Any], show: bool = True, unique_id: str = None) -> str:
	"""
	It's not actually recursive - because, you know, any recursion could be turned into iteration,
	and good boys do that. 😊
	"""
	assert isinstance(_RECURSION_LIMIT, int) and _RECURSION_LIMIT > 0

	prev: str = ''
	new: str = template
	for i in range(_RECURSION_LIMIT):
		if prev == new:
			break
		prev = new
		new = new.format_map(format_dict)
	if prev == new:
		return new

	msg = (
		f"Recursion limit ({_RECURSION_LIMIT}) reached on attempt to format a string: {template!r}\n"
		f"Last two formatting attempts:\n{prev!r}\n{new!r}"
	)
	if show and unique_id:
		_show_text_on_node(msg, unique_id)
	raise RecursionError(msg)
	# noinspection PyUnreachableCode
	return ''  # just to be safe


def formatter(
	template: str, recursive: bool = False, format_dict: _t.Dict[str, _t.Any] = None,
	show: bool = True, unique_id: str = None
) -> _t.Tuple[str]:
	format_dict = _verify_input_dict(format_dict)
	if not isinstance(template, str):
		raise TypeError(f"Not a string: {template!r}")

	out_text = (
		_recursive_format(template, format_dict, show, unique_id)
		if recursive
		else template.format_map(format_dict)
	)
	if show and unique_id:
		_show_text_on_node(out_text, unique_id)
	return (out_text, )
