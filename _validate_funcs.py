# encoding: utf-8
"""
Shared code to verify the input dict.
"""

import re as _re

from frozendict import frozendict as _frozendict

try:
	from enum import StrEnum as _StrEnum
except ImportError:
	from comfy.comfy_types.node_typing import StrEnum as _StrEnum

from .__typing import _t, T as _T, _A, _O, _U, DictMap as _DictMap


_re_valid_key_match = _re.compile("[a-zA-Z_][a-zA-Z_0-9]*$", flags=_re.IGNORECASE).match
_re_starting_digits_match = _re.compile("[0-9]+").match


class _KeyErrorType(_StrEnum):
	"""If a dictionary key fails as an argument for ``str.format()``, this is the specific reason."""
	NOT_STRING = 'Not {a_}string{s}{val}'
	EMPTY = 'Empty string{s}{val}'
	STARTS_WITH_DIGIT = 'String{s} start{inv_s} with digit{val}'
	INVALID_NAME = 'Wrong name{s} (must contain only numbers, latin letters and underscores){val}'

	@classmethod
	def all_items(cls) -> _t.Tuple['_KeyErrorType', ...]:
		# noinspection PyTypeChecker
		return tuple(x for x in cls)

	@staticmethod
	def check_key(key: _A) -> _O['_KeyErrorType']:
		"""
		Verify that the given item can be a keyword-argument name passed to ``str.format()``.
		The returned value is the type of key error, if the check fails. ``None`` on success.
		"""
		if not isinstance(key, str):
			return _KeyErrorType.NOT_STRING
		if not key:
			return _KeyErrorType.EMPTY
		if not _re_valid_key_match(key):
			if _re_starting_digits_match(key):
				return _KeyErrorType.STARTS_WITH_DIGIT
			return _KeyErrorType.INVALID_NAME
		return None

	@classmethod
	def check_dict_keys(cls, format_dict: _DictMap) -> _t.Dict['_KeyErrorType', list]:
		"""
		Verify all the keys from the input dictionary to match the criteria of proper argument names for ``str.format()``.
		The returned dict contains all the wrong keys, grouped by the error type.
		"""
		wrong_keys_grouped_by_error_type: _t.Dict[_KeyErrorType, list] = dict()
		for key in format_dict.keys():
			error_type = cls.check_key(key)
			if error_type is None:
				continue
			if error_type not in wrong_keys_grouped_by_error_type:
				wrong_keys_grouped_by_error_type[error_type] = list()
			wrong_keys_grouped_by_error_type[error_type].append(key)
		return wrong_keys_grouped_by_error_type

	@classmethod
	def format_all_errors(
		cls,
		wrong_keys_grouped_by_error_type: _t.Dict['_KeyErrorType', _t.Sequence],
		where: str = ''
	) -> _O[str]:
		"""Build error message for all the pre-validated wrong keys."""
		errors_and_is_multi = [
			err_tp.format_error(wrong_keys_grouped_by_error_type[err_tp])
			for err_tp in cls.all_items()
			if err_tp in wrong_keys_grouped_by_error_type
		]
		if not errors_and_is_multi:
			return None

		is_multi_error = len(errors_and_is_multi) > 1
		prefix = "Invalid key{s}{where_sep}{where}".format(
			s='s' if is_multi_error or any(x[1] for x in errors_and_is_multi) else '',
			where_sep=' ' if where else '',
			where=where,
		)

		if not is_multi_error:
			# Single error type
			error_msg = errors_and_is_multi[0][0]
			# We need to turn the fist character to lowercase:
			first_char = error_msg[0].lower()
			error_msg = error_msg[1:]
			error_msg = f"{first_char}{error_msg}"
			return f"{prefix} - {error_msg}"

		# Multiple error types
		seq = '\n\n'.join(x[0] for x in errors_and_is_multi)
		return f"{prefix}:\n\n{seq}"

	def format_error(self, wrong_keys: _t.Sequence) -> _t.Tuple[str, bool]:
		"""
		Build error message for a single ``_KeyErrorType``.
		The second returned value is a boolean: whether multiple wrong keys provided.
		"""
		n = len(wrong_keys)
		if n > 1:
			s = 's'
			a_ = ''
			inv_s = ''
			is_multi = True
			wrong_keys_str = '\n\t'.join(repr(k) for k in wrong_keys)
			wrong_keys_str = f':\n\t{wrong_keys_str}'
		else:
			s = ''
			a_ = 'a '
			inv_s = 's'
			is_multi = False
			if n == 1:
				wrong_keys_str = f': {wrong_keys[0]!r}'
			else:
				wrong_keys_str = ''
		return self.value.format(a_=a_, s=s, inv_s=inv_s, val=wrong_keys_str), is_multi


# ----------------------------------------------------------


def __verify_dict_type(_dict: _O[_DictMap], error_if_none=False) -> _O[_DictMap]:
	"""Ensure that the given input-dict is at least a dict indeed."""
	if _dict is None:
		if error_if_none:
			raise TypeError("No input-dict")
		return None

	# In py3.10, frozendict isn't a dict, but is a `typing.Mapping`.
	# So, this many types to check against:
	if not isinstance(_dict, (dict, _frozendict, _t.Mapping)):
		raise TypeError(f"Input-dict isn't a dict. Got: {_dict!r}")
	return _dict


def _verify_format_dict(format_dict: _DictMap = None, error_if_none=False) -> None:
	"""
	Verify input dict to have only the keys that match the criteria of proper argument names for ``str.format()``.
	Raises error if invalid ones found.
	"""
	format_dict = __verify_dict_type(format_dict, error_if_none=error_if_none)
	if not format_dict:
		return

	wrong_keys_grouped_by_error_type = _KeyErrorType.check_dict_keys(format_dict)
	error_msg = _KeyErrorType.format_all_errors(wrong_keys_grouped_by_error_type, where='in input-dict')
	if not error_msg:
		return
	raise KeyError(error_msg)


def _cleanup_format_dict(format_dict: _DictMap = None, error_if_none=False) -> _t.Dict[str, _A]:
	"""
	Cleanup input dict by keeping only the keys that match the criteria of proper argument names for ``str.format()``.
	Errors are thrown only if the provided dict isn't a dict.
	Otherwise, no error is raised, just all the invalid keys are removed from the resulting dict.
	"""
	format_dict = __verify_dict_type(format_dict, error_if_none=error_if_none)
	if not format_dict:
		return {}

	error_type_detector = _KeyErrorType.check_key
	return {
		str(k): v
		for k, v in format_dict.items()
		if error_type_detector(k) is None
	}
