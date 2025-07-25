# encoding: utf-8
"""
"""

import typing as _t

from .node_dict_add_any import StringConstructorDictAddAny
from .node_dict_add_string import StringConstructorDictAddString
from .node_dict_from_text import StringConstructorDictFromText
from .node_dict_preview import StringConstructorDictPreview
from .node_formatter import StringConstructorFormatter
from .node_validate_keys import StringConstructorValidateKeys

NODE_CLASS_MAPPINGS: _t.Dict[str, type] = {
	'StringConstructorDictAddAny': StringConstructorDictAddAny,
	'StringConstructorDictAddString': StringConstructorDictAddString,
	'StringConstructorDictFromText': StringConstructorDictFromText,
	'StringConstructorDictPreview': StringConstructorDictPreview,
	'StringConstructorFormatter': StringConstructorFormatter,
	'StringConstructorValidateKeys': StringConstructorValidateKeys,
}
NODE_DISPLAY_NAME_MAPPINGS: _t.Dict[str, str] = {
	'StringConstructorDictAddAny': "Add ANY to Format-Dict (Advanced)",
	'StringConstructorDictAddString': "Add String to Format-Dict",
	'StringConstructorDictFromText': "Format-Dict from Text",
	'StringConstructorDictPreview': "Preview Format-Dict",
	'StringConstructorFormatter': "String Formatter",
	'StringConstructorValidateKeys': "Validate Format-Dict",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
