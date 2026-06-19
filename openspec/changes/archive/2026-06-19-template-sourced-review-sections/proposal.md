## Why

The Friday Review Template duplicates the content of `Weekly Review Template.md`, `Monthly Review Template.md`, `Quarter Review Template.md`, and `Year Review Template.md` verbatim. Any edit to a section (adding a question, reordering items) must be made in two places, and the two will silently drift out of sync.

## What Changes

- Replace the hardcoded section bodies in `Friday Review Template.md` with `tp.file.include()` calls that pull content from the individual template files at run time.
- The individual template files (`Weekly Review Template.md`, etc.) become the single source of truth for their section content.
- No behavioral change: the date logic, conditional sections, and note naming are unchanged.

## Capabilities

### New Capabilities

- `template-include-sourcing`: The Friday Review Template SHALL source each review section's content from its corresponding template file using Templater's `tp.file.include()`, so edits to individual templates are automatically reflected in Friday reviews.

### Modified Capabilities

## Impact

- **Files modified**: `Scripts/Friday Review Template.md` — section bodies replaced with `tp.file.include()` calls.
- **Live vault copy updated**: `📌 Permanent Notes/Z Templates/Friday Review Template.md`.
- **No changes** to the four individual template files or the date logic.
- **Requires** Templater's "Template folder location" to be set so `tp.file.include("[[Weekly Review Template]]")` can resolve the file by name.
