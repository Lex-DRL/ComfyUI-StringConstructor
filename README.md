> "Do one thing and do it well." _— Peter H. Salus / Doug McIlroy, [core Unix principle](https://en.wikipedia.org/wiki/Unix_philosophy)_

> "Simple is better than complex." _— Zen of Python_

# `String Constructor` (aka Text-Formatting) nodes

There's a plenty of string-formatting nodes for ComfyUI. But this node pack takes a different approach:
- First, you prepare a dictionary of named sub-strings (chunks of text).
- Then, right before `CLIP Text Encode`, you construct a final prompt from these parts, using python's [string formatting syntax](https://docs.python.org/3/library/string.html#format-examples)... **Don't panic!** You don't need to be a programmer to simply compose a prompt from pieces. Besides, examples are below.
- Unlike many other _(giant uber-mega)_ node packs, this one strictly adheres to the modularity paradigm: it's minimal and self-sufficient.

[🔄 Updates ChangeLog](CHANGELOG.md)
