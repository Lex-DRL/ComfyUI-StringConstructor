> "Do one thing and do it well." _— Peter H. Salus / Doug McIlroy, [core Unix principle](https://en.wikipedia.org/wiki/Unix_philosophy)_

> "Simple is better than complex." _— Zen of Python_

# `String Constructor` (Text-Formatting) nodes

There's already a plenty of string-formatting nodes for ComfyUI. But this node pack takes a different approach:
- First, you prepare a dictionary of named sub-strings (chunks of text).
- Then, right before `CLIP Text Encode`, you construct a final prompt from these parts, using python's [string formatting syntax](https://docs.python.org/3/library/string.html#format-examples)... **Don't panic!** You don't need to be a programmer - just look below for a quick introduction.
- Unlike many other _(giant uber-mega)_ node packs, this one strictly adheres to the modular philosophy: it's minimal and self-sufficient.

[🔄 Updates ChangeLog](CHANGELOG.md)

![image](img/screenshot1.png)

## Syntax

For those who are unfamiliar with python's string formatting, the rules are very simple:
- You need to name (set tags/**keys** for) your sub-strings the same way python variables are named: only ASCII letters, digits and underscore are allowed + the name can't start with a digit. So:
  - ✅ `valid_name`, `other_valid_name`, `YetAnother_ValidName`, `name3`.
  - ❌ `wrong name with spaces`, `wrong-name.with:punctuation`, `3name`.
- Then, you simply put your `{substring_name}` inside curly braces (no spaces between) in the formatting template - and voila! This pattern will be replaced with the actual sub-string.

> [!NOTE]
> For advanced users:
> Internally, a built-in `str.format()` is called with keyword arguments from `str_dict`, which is literally just a dict... though, an immutable one.
> So any formatting patterns are available (like `{float_value:.3f}`). However, currently there are no nodes to append non-string values (planned, TODO).
