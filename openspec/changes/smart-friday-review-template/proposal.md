## Why

The existing review templates rely on DataviewJS buttons that only run on Mac — they fail silently on iPhone. On Fridays, the user must manually decide which review types apply (weekly, monthly, quarterly, yearly) and open the right combination of templates. This adds friction and completely breaks the mobile workflow.

## What Changes

- Add a new **Friday Review Template** (Templater `.md`) that auto-detects which review sections to include based on today's date — weekly always, plus monthly/quarterly/yearly when the current Friday falls within 3 days of that period's last day.
- Add a **Commander ribbon button** that triggers the Friday Review Template in one tap, creating the note and inserting the correct sections with no further interaction.
- Remove the DataviewJS button blocks from `Weekly Review Template.md`, `Monthly Review Template.md`, `Quarter Review Template.md`, and `Year Review Template.md` — those buttons are Mac-only and are superseded by the new unified template.
- Add a Jest test file verifying the closest-Friday date logic.

## Capabilities

### New Capabilities

- `friday-review-template`: A single Templater `.md` file using only `tp.*` API and bundled `moment.js`. Checks today's date, determines which period boundaries (month-end, quarter-end, year-end) fall within 3 days, and renders only the relevant review sections. Auto-names the note (e.g. `2026-W25 Review`, `2026-W25 M06 Review`, `2026-W25 M06 Q2 Review`, `2026-W25 M06 Q4 Y2026 Review`).
- `closest-friday-date-logic`: The rule — a Friday F triggers a period review if `|F − lastDayOfPeriod| ≤ 3 days`. Covers monthly (last day of each month), quarterly (Mar 31, Jun 30, Sep 30, Dec 31), and yearly (Dec 31). Implemented in moment.js inside the template; tested independently in Jest.
- `commander-ribbon-button`: Setup instructions for adding a Commander plugin ribbon icon that fires the Templater "Create new note from Friday Review Template" command. Works on iOS and macOS.

### Modified Capabilities

- None — review question content is unchanged; only the delivery mechanism changes (Mac-only buttons → cross-platform Templater template).

## Impact

- **Files modified**: `Weekly Review Template.md`, `Monthly Review Template.md`, `Quarter Review Template.md`, `Year Review Template.md` in the live Obsidian vault — DataviewJS blocks removed.
- **Files added**: `Friday Review Template.md` in the vault templates folder and in `Scripts/` (dev vault copy). `Scripts/__tests__/fridayReviewDateLogic.test.js`.
- **Plugins required**: Templater (already installed), Commander (new — free, open source, iOS-compatible).
- **No breaking changes** to existing note content or vault structure.
