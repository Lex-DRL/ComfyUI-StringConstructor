# encoding: utf-8
"""
Code shared between various `funcs_*` modules.
"""

import typing as _t

from server import PromptServer as _PromptServer

def _show_text_on_node(text: str = None, unique_id: str = None):
	if not text:
		# TODO: Planned for the future - currently, there's no point removing the text since it's box is shown anyway
		# An odd workaround since `send_progress_text()` doesn't want to update text when '' passed
		text = '<span></span>'
	# print(f"{unique_id} text: {text!r}")

	# Snatched from: https://github.com/comfyanonymous/ComfyUI/blob/27870ec3c30e56be9707d89a120eb7f0e2836be1/comfy_extras/nodes_images.py#L581-L582
	_PromptServer.instance.send_progress_text(text, unique_id)
