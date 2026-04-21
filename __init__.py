# encoding: utf-8
"""
"""

from comfy_api.latest import ComfyExtension as _ComfyExtension, io as _io

from ._formatter_class import Formatter
from .node_formatter import *
from .node_validate import *

class StringConstructorExtension(_ComfyExtension):
	async def get_node_list(self) -> list[type[_io.ComfyNode]]:
		return [
			StringFormatter, StringFormatterOld1,
			ValidateKeys, ValidateKeysOld1,
		]

async def comfy_entrypoint() -> _ComfyExtension:
	return StringConstructorExtension()
