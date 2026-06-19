## Context

`Friday Review Template.md` currently contains the full markdown bodies of all four review sections (weekly, monthly, quarterly, yearly) copied verbatim from the individual template files. Templater provides a `tp.file.include("[[Note Name]]")` function that reads another vault file at execution time and inlines its content. The individual template files are plain markdown (no Templater syntax) and already exist in the templates folder.

## Goals / Non-Goals

**Goals:**
- Each review section in the Friday Review Template is sourced live from its individual template file
- Editing `Weekly Review Template.md` (or any other) is immediately reflected in Friday reviews with no other change needed
- The conditional logic and note naming are completely unchanged

**Non-Goals:**
- Changing the content of any individual template file
- Changing the date logic or section-selection behavior
- Supporting template files that themselves contain Templater syntax (not needed today)

## Decisions

### Decision 1: Use `tp.file.include()` over `app.vault.cachedRead()`

**Chosen:** `tp.file.include("[[Weekly Review Template]]")`

**Alternatives considered:**
- `app.vault.cachedRead(app.vault.getAbstractFileByPath(...))` — works but requires knowing the full vault path, is async, and requires appending output via `tR +=`.
- Manual copy-paste on each template edit — status quo; error-prone.

**Rationale:** `tp.file.include()` is the idiomatic Templater API for this use case. It is synchronous in the template output context and requires no path management.

### Decision 2: Wiki-link name (not file path) for include argument

**Chosen:** `tp.file.include("[[Weekly Review Template]]")` — bare name, no folder prefix.

**Rationale:** Obsidian resolves wiki-links by filename across the whole vault. The bare name survives folder reorganization and matches how Obsidian users naturally reference files. A full path is only needed if two files share the same name, which is not the case here.

### Decision 3: Keep includes inside the existing conditional blocks

**Chosen:** Wrap `tp.file.include()` inside the existing `<%* if (isMonthly) { -%>` blocks unchanged.

**Rationale:** The conditional logic is already correct and tested. Only the hardcoded body needs replacing — no restructuring needed.

## Risks / Trade-offs

- **Template file renamed or deleted** → `tp.file.include()` produces an empty string silently. Mitigation: template file names are stable and version-controlled in `Scripts/`.
- **Template file gains Templater syntax** → nested `tp.*` calls inside an included file are not evaluated (Templater only processes the root template). Not a current need; would require a different approach if it ever becomes one.

## Migration Plan

1. Replace hardcoded section bodies in `Scripts/Friday Review Template.md` with `tp.file.include()` calls.
2. Copy updated template to live vault.
3. Test: invoke template, verify all sections render with content from the individual files.
