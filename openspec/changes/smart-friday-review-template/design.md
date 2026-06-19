## Context

The vault currently has four separate review templates (Weekly, Monthly, Quarter, Year), each containing a DataviewJS code block that renders a button to launch a Python script via `osascript`. This works on Mac but DataviewJS does not execute on Obsidian iOS, so the buttons are dead on iPhone. The user manually selects the right template combination every Friday.

Templater is already installed and in active use (e.g., `getRandomRuleOfLife` in the Journal Entry Template). moment.js is bundled with Templater and available as `moment()` inside `<%* %>` blocks. No additional runtime dependencies are needed.

## Goals / Non-Goals

**Goals:**
- One template file that auto-selects review sections based on date
- Works identically on macOS and iOS Obsidian
- One-tap invocation via a Commander ribbon button
- Remove Mac-only DataviewJS buttons from all four existing templates
- Date logic is testable in Jest without Obsidian

**Non-Goals:**
- Fully automatic note creation (no launchd/cron — that's Mac-only)
- Changing the review question content
- Replacing the evening-review or daily-digest Python scripts
- Supporting non-Friday invocation (the template is designed for Fridays)

## Decisions

### Decision 1: Single template file over four separate templates

**Chosen:** One `Friday Review Template.md` that conditionally renders sections.

**Alternatives considered:**
- Keep four templates, use Commander to launch all relevant ones → still requires knowing which ones to run; doesn't reduce cognitive load.
- Periodic Notes plugin → enforces strict ISO week naming and folder structure; less flexible for the user's existing vault layout.

**Rationale:** A single file is one command in the palette and one ribbon button. The user never needs to think about which combination to apply.

### Decision 2: Closest-Friday rule (|diff| ≤ 3 days)

**Chosen:** A Friday triggers a period review if it falls within 3 calendar days of the last day of that period (before or after).

**Rationale:** The user confirmed this matches their intent — "if the month ends on Wednesday, the review is 2 days later." The ±3 window means:
- Last day Mon → review is 3 days before (last Friday of that month)
- Last day Tue–Thu → review is 1–3 days after (first Friday of the new period)
- Last day Fri → review is that same day
- Last day Sat/Sun → review is 1–2 days before

The window never overlaps between two consecutive months (shortest month is 28 days; 3 < 28/2), so a Friday will never trigger two monthly reviews.

**Alternative considered:** Always use the last Friday of the month → fails the user's Wednesday example.

### Decision 3: moment.js for date logic, not native JS Date

**Chosen:** `moment()` via Templater's bundled instance.

**Rationale:** Templater exposes `moment` as a global inside `<%* %>` blocks. It handles month/quarter boundaries, ISO weeks, and day-of-week cleanly. Native `Date` arithmetic for "last day of month" and "days to Friday" is error-prone.

**For Jest tests:** The same logic is re-implemented with native JS `Date` (no moment dependency) so tests run without Obsidian or Templater.

### Decision 4: Commander plugin for the ribbon button

**Chosen:** Commander (`phibr0/obsidian-commander`) adds a ribbon icon that fires any Obsidian command, including Templater's per-template command.

**Rationale:** Commander is the standard plugin for this use case, has confirmed iOS support, and requires zero code — it's pure configuration. The alternative (custom CSS + Buttons plugin) is more fragile and requires notes-based setup.

**Prerequisite:** Templater must have "Trigger Templater on new file creation" enabled, and the Friday Review Template must be set as the template for its target folder (or use "Create new note from template" command).

### Decision 5: Dev vault copy in Scripts/

**Chosen:** The template is also saved to `Scripts/Friday Review Template.md` in this repo.

**Rationale:** Keeps the template under version control and testable. The live vault copy in iCloud is the source of truth at runtime; this repo copy is the backup and development reference.

## Risks / Trade-offs

- **Templater mobile limitations** → The `tp.file.rename()` call (to set the note title) works on iOS in Templater ≥ 1.16. If the user is on an older version, the rename silently no-ops and the note keeps its default name. Mitigation: document minimum Templater version; the note content is still correct even if the name isn't auto-set.
- **moment.js API surface** → Templater exposes `moment` as a global, but its exact version depends on the Templater release. The date logic uses only stable moment APIs (`endOf`, `diff`, `isoWeek`, `format`) present since moment 2.x. Risk is minimal.
- **Commander not installed** → Without Commander, the user can still invoke the template via the command palette (`Templater: Create new note from template`). The ribbon button is a convenience layer, not a hard dependency.
- **DataviewJS button removal** → Removing the buttons from the four existing templates is irreversible without git. The dev vault copy will preserve the originals; the live vault edit should be done carefully.

## Migration Plan

1. Install Commander plugin in Obsidian (one-time, manual).
2. Write `Friday Review Template.md` to the vault templates folder.
3. Configure Templater: add the template to "Template folder" if not already set.
4. Configure Commander: add ribbon icon → assign command `Templater: Create new note from template → Friday Review Template`.
5. Edit the four existing templates to remove their `dataviewjs` code blocks.
6. Test on Mac: tap ribbon button → verify correct sections appear for today's date.
7. Test on iPhone: same tap → verify template renders correctly.
8. Optionally remove the four Python review scripts from `~/.claude/scripts/` once satisfied.
