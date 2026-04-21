# encoding: utf-8
"""Code for the main node."""

from inspect import cleandoc as _cleandoc

from comfy_api.latest import io as _io, ui as _ui

from .__meta import (
	category as _category,
	pack_id_suffix as _pack_id
)
from .__typing import _A, _U, _O, _t, T as _T, FormatDict as _FormatDict
from ._formatter_class import Formatter as _Formatter
from ._io_custom import (
	_BaseNode,
	_DICT_INPUT_OPTIONAL,
	_input_override, _schema_old_name
)
from .docstring_formatter import format_docstring as _format_docstring

# ----------------------------------------------------------

class StringFormatter(_BaseNode):
	"""
	Construct the formatted string from template and format-dictionary.
	"""
	_schema = _io.Schema(
		node_id=f'StringFormatter{_pack_id}',
		display_name='String Formatter',
		category=_category,
		description=_format_docstring(_cleandoc(__doc__)),
		inputs=[
			_io.String.Input(
				'template',
				tooltip=(
					"Type the text template. "
					"To reference named substrings from format-dictionary, use this syntax: {substring_name}. For example:\n\n"
					"score_9, score_8_up, score_7_up, {char1_short}, standing next to {char2_short},\n"
					"{char1_long}\n{char2_long}"
				),
				multiline=True,
			),
			_io.Boolean.Input(
				'recursive_format',
				tooltip=(
					"Do recursive format - i.e., allow the chunks from the dictionary to reference other chunks."
				),
				default=False,
				label_on='❗ yes',
				label_off='no',
			),
			_io.Boolean.Input(
				'safe_format',
				tooltip=(
					"If template contains an invalid {text pattern} which can't be formatted - leave it as-is "
					"(instead of throwing an error).\n"
					"Safe mode is recommended for templates with JSON, CSS, or other literal curly brackets."
				),
				default=True,
				label_on='yes',
				label_off='no',
			),
			_io.Boolean.Input(
				'show_status',
				tooltip=(
					"Show the final string constructed from the text-template and format-dictionary?"
				),
				default=True,
				label_on='formatted string',
				label_off='no',
			),

			_input_override(
				_DICT_INPUT_OPTIONAL,
				tooltip=(
					"The dictionary to take named sub-strings from. It could be left unconnected, if the pattern doesn't reference "
					"any sub-strings - then, this node acts exactly the same as a regular string-primitive node."
				),
			),
		],
		outputs=[_io.String.Output('string')],
		# hidden=[_io.Hidden.unique_id],
		is_output_node=True,
	)

	@classmethod
	def execute(cls,
		template: str,
		recursive_format: bool = False,
		safe_format: bool = True,
		show_status: bool = False,
		dict: _O[_FormatDict] = None,
	) -> _io.NodeOutput:
		formatter = _Formatter(
			format_dict=dict, recursive=recursive_format, safe=safe_format,
		)
		string = formatter(template)
		return _io.NodeOutput(
			string,
			ui=_ui.PreviewText(string) if show_status else None
		)

# ==========================================================
# Deprecated node with old ID (for backwards compatibility)

class StringFormatterOld1(StringFormatter):
	_schema = _schema_old_name(
		StringFormatter._schema,
		'StringConstructorFormatter'
	)
