## 1. Date Logic & Tests

- [x] 1.1 Write `Scripts/__tests__/fridayReviewDateLogic.test.js` with Jest tests covering all scenarios in the `closest-friday-date-logic` spec (±3-day rule for monthly, quarterly, yearly; overlap impossibility)
- [x] 1.2 Run `npm test -- --testPathPattern=fridayReviewDateLogic` and confirm all tests pass

## 2. Friday Review Template

- [x] 2.1 Write `Scripts/Friday Review Template.md` — the Templater template with moment.js date logic that sets `isMonthly`, `isQuarterly`, `isYearly` booleans and calls `tp.file.rename()` with the correct title suffix
- [x] 2.2 Include the Weekly Review section (checklist + reflection questions) from the existing `Weekly Review Template.md`, without the DataviewJS block
- [x] 2.3 Add conditional Monthly Review section (wrapped in `<%* if (isMonthly) { -%>` ... `<%* } -%>`) with content from `Monthly Review Template.md`
- [x] 2.4 Add conditional Quarterly Review section with content from `Quarter Review Template.md`
- [x] 2.5 Add conditional Yearly Review section with content from `Year Review Template.md`
- [x] 2.6 Copy `Scripts/Friday Review Template.md` to the live vault templates folder: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📌 Permanent Notes/Z Templates/Friday Review Template.md`

## 3. Remove DataviewJS Buttons from Existing Templates

- [x] 3.1 Remove the `dataviewjs` code block from `Weekly Review Template.md` in the live vault
- [x] 3.2 Remove the `dataviewjs` code block from `Monthly Review Template.md` in the live vault
- [x] 3.3 Remove the `dataviewjs` code block from `Quarter Review Template.md` in the live vault
- [x] 3.4 Remove the `dataviewjs` code block from `Year Review Template.md` in the live vault

## 4. Commander Plugin Setup

- [ ] 4.1 Install the Commander plugin in Obsidian (Settings → Community plugins → Browse → "Commander")
- [ ] 4.2 In Templater settings, confirm "Template folder location" is set to the vault templates folder
- [ ] 4.3 In Commander settings, add a new ribbon command: choose the command `Templater: Create new note from template` → select `Friday Review Template` → assign a calendar/review icon (e.g. 📅)
- [ ] 4.4 Enable the ribbon button for both desktop and mobile in Commander settings

## 5. Verification

- [ ] 5.1 On Mac: click the ribbon button, verify the correct note title and sections appear for today's date
- [ ] 5.2 On iPhone: tap the ribbon button, verify the template renders without errors and sections are correct
- [ ] 5.3 Manually test a "monthly Friday" date by temporarily setting `moment()` to a date within 3 days of a month-end and confirming the Monthly section appears
- [ ] 5.4 Confirm the four existing templates no longer show any DataviewJS blocks on Mac and iPhone
