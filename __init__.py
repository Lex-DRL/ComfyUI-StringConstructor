# encoding: utf-8
"""
"""

import typing as _t

from .node_dict_from_text import StringConstructorDictFromText

NODE_CLASS_MAPPINGS: _t.Dict[str, type] = {
	'StringConstructorDictFromText': StringConstructorDictFromText,
}
NODE_DISPLAY_NAME_MAPPINGS: _t.Dict[str, str] = {
	'StringConstructorDictFromText': "Format-Dict from Text"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
