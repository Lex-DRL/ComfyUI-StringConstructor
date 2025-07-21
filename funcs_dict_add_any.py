# encoding: utf-8
"""
The actual code (MVC pattern) for `StringConstructorDictAddAny` node.
"""

import typing as _t

from frozendict import deepfreeze as _deepfreeze

from .funcs_common import _raise_from_errors_dict, _validate_key, _verify_input_dict


def set_dict_any_type_item(
	name: str, value: _t.Any = None, in_dict: _t.Dict[str, _t.Any] = None,
	# unique_id: str = None,
) -> _t.Tuple[_t.Dict[str, _t.Any]]:
	"""Update/append an item of any type to the dict."""
	out_dict: _t.Dict[str, _t.Any] = _verify_input_dict(in_dict)
	if value is None:
		return (_deepfreeze(in_dict), )  # No need to create another dict instance if it's already frozen

	errors_dict: _t.Dict[_t.Any, str] = dict()
	name = _validate_key(name, errors_dict)
	_raise_from_errors_dict(errors_dict)
	new_dict: _t.Dict[str, _t.Any] = {name: value}
	out_dict.update(new_dict)
	return (_deepfreeze(out_dict), )
