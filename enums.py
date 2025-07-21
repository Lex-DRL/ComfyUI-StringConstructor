# encoding: utf-8
"""
Internal enums.
"""

import typing as _t

try:
	from enum import StrEnum as _StrEnum
except ImportError:
	from comfy.comfy_types.node_typing import StrEnum as _StrEnum


T = _t.TypeVar('T')


class __BaseEnum(_StrEnum):
	@classmethod
	def all_values(cls) -> _t.Tuple[str, ...]:
		return tuple(x.value for x in cls)


class DataTypes(__BaseEnum):
	"""Additional data-types defined byt the node pack."""
	DICT = 'DICT'

	@staticmethod
	def __custom_input_type_dict(_dict_args: _t.Tuple[_t.Dict[str, T], ...], kwargs: _t.Dict[str, T]) -> _t.Dict[str, T]:
		res_dict: _t.Dict[str, _t.Any] = {"forceInput": True}
		for d in _dict_args:
			if d is not None:
				res_dict.update(d)
		res_dict.update(kwargs)
		return res_dict

	@classmethod
	def input_dict(cls, *_dicts: _t.Dict[str, T], **kwargs: T) -> _t.Tuple[_t.Union['DataTypes', str], _t.Dict[str, T]]:
		return cls.DICT, cls.__custom_input_type_dict(_dicts, kwargs)
