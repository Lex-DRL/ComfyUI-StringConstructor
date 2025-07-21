# encoding: utf-8
"""
Code shared between various `funcs_*` modules.
"""

import typing as _t

import re as _re

from server import PromptServer as _PromptServer

from .enums import T as _T


def _show_text_on_node(text: str = None, unique_id: str = None):
	if not text:
		# TODO: Planned for the future - currently, there's no point removing the text since it's box is shown anyway
		# An odd workaround since `send_progress_text()` doesn't want to update text when '' passed
		text = '<span></span>'
	# print(f"{unique_id} text: {text!r}")

	# Snatched from: https://github.com/comfyanonymous/ComfyUI/blob/27870ec3c30e56be9707d89a120eb7f0e2836be1/comfy_extras/nodes_images.py#L581-L582
	_PromptServer.instance.send_progress_text(text, unique_id)


_re_valid_key_match = _re.compile("[a-zA-Z_][a-zA-Z_0-9]*$").match
_re_starting_digits_match = _re.compile("[0-9]+").match


def _validate_key(key: str, errors_dict: _t.Dict[_t.Any, str]) -> _t.Union[str, None]:
	"""Verify that the given string can be a key. Otherwise, append a message to `errors_dict`."""
	if not isinstance(key, str):
		errors_dict[key] = f"Not a valid key (string name): {key!r}"
		return None
	key = str(key).strip()
	if not key:
		errors_dict[key] = f"Key (string name) can't be empty. Got: {key!r}"
		return None
	if not _re_valid_key_match(key):
		if _re_starting_digits_match(key):
			errors_dict[key] = f"Key (string name) can't start with a digit. Got: {key!r}"
		else:
			errors_dict[key] = f"Key (string name) must contain only numbers, latin letters and underscores. Got: {key!r}"
		return None
	return key


def _raise_from_errors_dict(
	errors_dict: _t.Dict[_t.Any, str],
	single_error_format: str = '{}',
	multi_errors_format: str = "Invalid keys (string names):\n{}",
):
	if not errors_dict:
		return

	if len(errors_dict) == 1:
		msg = single_error_format.format(next(iter(errors_dict.values())))
	else:
		msg = multi_errors_format.format('\n'.join(repr(x) for x in errors_dict.keys()))
	raise KeyError(msg)


def _verify_input_dict(input_dict: _t.Dict[str, _T] = None) -> _t.Dict[str, _T]:
	"""
	Verify input dict to have only valid keys. Raises errors if invalid ones found.
	Always returns a new dict instance (shallow copy if non-empty dict passed).
	"""
	if input_dict is None:
		return dict()
	if not isinstance(input_dict, dict):
		raise TypeError(f"Input-dict isn't a dict. Got: {input_dict!r}")

	errors_dict: _t.Dict[_t.Any, str] = dict()
	for key in input_dict.keys():
		_validate_key(key, errors_dict)

	_raise_from_errors_dict(
		errors_dict,
		"Invalid input-dict:\n{}", "Invalid keys (string names) in input-dict:\n{}"
	)
	return dict(input_dict)
