# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorFormatter` node.
"""

import typing as _t

from .enums import T as _T
from .funcs_common import _show_text_on_node, _verify_input_dict


def formatter(template: str, format_dict: _t.Dict[str, _T] = None, show: bool = True, unique_id: str = None) -> _t.Tuple[str]:
	format_dict = _verify_input_dict(format_dict)
	if not isinstance(template, str):
		raise TypeError(f"Not a string: {template!r}")
	out_text = template.format_map(format_dict)

	if show and unique_id:
		_show_text_on_node(out_text, unique_id)

	return (out_text, )
