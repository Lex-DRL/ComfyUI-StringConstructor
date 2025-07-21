# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorDictString` node.
"""

import typing as _t

from frozendict import deepfreeze as _deepfreeze

from .enums import T as _T
from .funcs_common import _raise_from_errors_dict, _validate_key, _verify_input_dict

def set_dict_string(
	name: str, value: str, strip_lines=True, in_dict: _t.Dict[str, _T] = None,
	# unique_id: str = None,
):
	"""Update/append a string to the dict."""
	out_dict: _t.Dict[str, _T] = _verify_input_dict(in_dict)
	errors_dict: _t.Dict[_t.Any, str] = dict()
	name = _validate_key(name, errors_dict)
	_raise_from_errors_dict(errors_dict)
	value = str(value)
	if strip_lines:
		value = '\n'.join(
			x.strip() for x in value.splitlines()
		)
	new_dict: _t.Dict[str, str] = {name: value}
	out_dict.update(new_dict)
	return (_deepfreeze(out_dict),)
