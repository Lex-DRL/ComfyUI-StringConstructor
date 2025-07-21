# encoding: utf-8
"""
"""

import typing as _t

from .node_dict_from_text import StringConstructorDictFromText
from .node_dict_preview import StringConstructorDictPreview
from .node_formatter import StringConstructorFormatter

NODE_CLASS_MAPPINGS: _t.Dict[str, type] = {
	'StringConstructorDictFromText': StringConstructorDictFromText,
	'StringConstructorDictPreview': StringConstructorDictPreview,
	'StringConstructorFormatter': StringConstructorFormatter,
}
NODE_DISPLAY_NAME_MAPPINGS: _t.Dict[str, str] = {
	'StringConstructorDictFromText': "Format-Dict from Text",
	'StringConstructorDictPreview': "Preview Format-Dict",
	'StringConstructorFormatter': "String Formatter",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
