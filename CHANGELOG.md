## `TODO`

The pack is considered feature-complete.
No other features planned (but I have nothing against improvements: feel free to [Pull Request](../../pulls)).

To do some fancy stuff with dictionaries, specialized node packs are recommended instead.

# v1.1.1

- Shorten tooltip for `safe_format` toggle.

# v1.1.0

- `✨New feature` Safe-formatting mode for `String Formatter`:
  - When an invalid pattern included in the formatted template - instead of throwing an error, leaves this part of the template as-is. Useful for templates with curly braces in them intended to stay: JSON/CSS.
  - The entire implementation of `String Formatter` node is fully reworked because of it.

# v1.0.4

- All the secondary dict-related nodes are moved to a subcategory.
- Default node name shortened: `Format-Dict` → just `Dict`.
- New node: `Extract String from Dict` - to be actually self-sufficient for the common use cases.

# v1.0.3

- [fix] Nodes made compatible with built-in preview nodes.
- Some internal refactoring/cleanup.

# v1.0.2

- New node: `Validate Format-Dict`

# v1.0.1

- ❗ Recursive formatting.
- Tiny tweaks to tooltips/descriptions.

# v1.0.0

The minimally-complete version.

New node:
- `Add ANY to Format-Dict (Advanced)`

The Format-Dict data type name changed from `STR_DICT` to just `DICT` - for potential compatibility with other nodes.

# v0.0.1

MVP nodes:
- `Add String to Format-Dict`
- `Format-Dict from Text`
- `Format-Dict Preview`
- `String Formatter`
