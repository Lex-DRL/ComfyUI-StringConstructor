# encoding: utf-8
"""
"""

from dataclasses import fields as __dataclass_fields

from comfy_api.latest import io as _io

from .__meta import category_old as _category_old
from .__typing import _t, T as _T


_DICT = _io.Custom("DICT")
_DICT_INPUT_OPTIONAL = _DICT.Input(
	'dict',
	optional=True,
	tooltip="An (optional) Format-Dictionary to work with."
)
_DICT_OUTPUT = _DICT.Output(
	'DICT',
	display_name='dict'
)

_T_Input = _t.TypeVar('T_Input', bound=_io.Input)


def __dataclass_fields_dict(obj) -> _t.Dict[str, _t.Any]:
	"""Return all the field values from a dataclass - as dict. No deep-copy."""
	field_names = (field.name for field in __dataclass_fields(obj))
	return {
		attr: getattr(obj, attr)
		for attr in field_names
	}


def _dataclass_override(obj: _T, **overrides) -> _T:
	"""Copy a dataclass instance with optional overrides."""
	obj_dict = __dataclass_fields_dict(obj)
	obj_dict.update(overrides)
	obj_type = type(obj)
	return obj_type(**obj_dict)


def _input_override(input_obj: _T_Input, **overrides) -> _T_Input:
	"""Copy an ``io.Input`` instance with optional overrides."""
	new_id = input_obj.id
	if 'id' in overrides:
		new_id = overrides.pop('id')

	input_args = input_obj.as_dict()
	if 'id' in input_args:
		del input_args['id']
	input_args.update(overrides)

	input_type: _t.Type[_T_Input] = type(input_obj)
	return input_type(new_id, **input_args)


def _schema_old_name(schema: _io.Schema, node_id: str, **overrides):
	"""Build a deprecated schema for old node-ID."""
	schema_dict = __dataclass_fields_dict(schema)
	if 'node_id' in schema_dict:
		del schema_dict['node_id']
	name_old = schema_dict.pop('display_name')

	schema_dict.update(dict(
		category=_category_old,
		display_name=f"{name_old} [OLD]",
		is_deprecated=True,
		is_dev_only=True,
	))
	schema_dict.update(overrides)
	return _io.Schema(node_id, **schema_dict)


# noinspection PyAbstractClass
class _BaseNode(_io.ComfyNode):
	"""Shared base class for all the nodes in pack.
	Stores schema in internal class attribute.
	"""
	_schema: _io.Schema = None

	@classmethod
	def define_schema(cls) -> _io.Schema:
		return cls._schema
