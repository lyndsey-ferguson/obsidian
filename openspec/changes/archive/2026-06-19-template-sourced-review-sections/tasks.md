## 1. Update Friday Review Template

- [x] 1.1 Replace the hardcoded weekly section body in `Scripts/Friday Review Template.md` with `<% tp.file.include("[[Weekly Review Template]]") %>`
- [x] 1.2 Replace the hardcoded monthly section body (inside the `isMonthly` block) with `<% tp.file.include("[[Monthly Review Template]]") %>`
- [x] 1.3 Replace the hardcoded quarterly section body (inside the `isQuarterly` block) with `<% tp.file.include("[[Quarter Review Template]]") %>`
- [x] 1.4 Replace the hardcoded yearly section body (inside the `isYearly` block) with `<% tp.file.include("[[Year Review Template]]") %>`

## 2. Deploy

- [x] 2.1 Copy updated `Scripts/Friday Review Template.md` to the live vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Lyndsey/📌 Permanent Notes/Z Templates/Friday Review Template.md`

## 3. Verify

- [x] 3.1 In the test vault, invoke the template and confirm all sections render with content matching the individual template files
- [x] 3.2 Edit one line in `Weekly Review Template.md` in the test vault, invoke the template again, confirm the change appears in the rendered note
- [x] 3.3 Revert the test edit to `Weekly Review Template.md`
