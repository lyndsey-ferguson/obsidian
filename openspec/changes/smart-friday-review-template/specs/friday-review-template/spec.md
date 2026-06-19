## ADDED Requirements

### Requirement: Template renders weekly section unconditionally
The Friday Review Template SHALL always include the Weekly Review section regardless of the date it is invoked.

#### Scenario: Weekly section always present
- **WHEN** the template is applied on any Friday
- **THEN** the rendered note contains the Weekly Review heading and all weekly checklist items and reflection questions

### Requirement: Template renders monthly section when Friday is closest to month-end
The Friday Review Template SHALL include the Monthly Review section when the current date falls within 3 calendar days of the last day of any month.

#### Scenario: Month ends on Wednesday — review runs Friday
- **WHEN** the template is applied on a Friday that is 2 days after the last day of the month
- **THEN** the rendered note includes the Monthly Review section

#### Scenario: Month ends on Saturday — review runs Friday
- **WHEN** the template is applied on a Friday that is 1 day before the last day of the month
- **THEN** the rendered note includes the Monthly Review section

#### Scenario: Mid-month Friday — no monthly section
- **WHEN** the template is applied on a Friday that is more than 3 days from any month-end
- **THEN** the rendered note does NOT include the Monthly Review section

### Requirement: Template renders quarterly section when Friday is closest to quarter-end
The Friday Review Template SHALL include the Quarterly Review section when the current Friday is the closest Friday to the last day of a quarter (Mar 31, Jun 30, Sep 30, Dec 31), using the same ±3-day rule.

#### Scenario: Quarter ends on a Thursday — review runs next Friday
- **WHEN** the template is applied on a Friday that is 1 day after the last day of a quarter
- **THEN** the rendered note includes both Monthly and Quarterly Review sections

#### Scenario: Non-quarter-end month-boundary Friday
- **WHEN** the template is applied on the closest Friday to a month-end that is not a quarter-end
- **THEN** the rendered note includes Monthly but NOT Quarterly Review section

### Requirement: Template renders yearly section when Friday is closest to year-end
The Friday Review Template SHALL include the Yearly Review section when the current Friday is the closest Friday to December 31, using the same ±3-day rule.

#### Scenario: Year ends on Wednesday — review runs first Friday of new year
- **WHEN** December 31 is a Wednesday and the template is applied on January 2 (Friday)
- **THEN** the rendered note includes Weekly, Monthly, Quarterly, and Yearly Review sections

#### Scenario: Non-year-end quarter Friday
- **WHEN** the template is applied on the closest Friday to March 31
- **THEN** the rendered note includes Monthly and Quarterly sections but NOT Yearly

### Requirement: Template auto-names the note
The Friday Review Template SHALL rename the newly created note using ISO week number and period suffixes.

#### Scenario: Weekly-only Friday naming
- **WHEN** only the weekly review is triggered
- **THEN** the note is named in the format `YYYY-WNN Review` (e.g., `2026-W25 Review`)

#### Scenario: Weekly + Monthly naming
- **WHEN** weekly and monthly reviews are triggered
- **THEN** the note is named `YYYY-WNN MNN Review` (e.g., `2026-W25 M06 Review`)

#### Scenario: Weekly + Monthly + Quarterly naming
- **WHEN** weekly, monthly, and quarterly reviews are triggered
- **THEN** the note is named `YYYY-WNN MNN QN Review` (e.g., `2026-W25 M06 Q2 Review`)

#### Scenario: All four reviews naming
- **WHEN** all four reviews are triggered
- **THEN** the note is named `YYYY-WNN MNN QN YYYY Review` (e.g., `2026-W52 M12 Q4 Y2026 Review`)

### Requirement: Template uses only mobile-compatible APIs
The Friday Review Template SHALL use only Templater's `tp.*` API and the bundled `moment.js` library — no `require()`, `child_process`, Node.js built-ins, or DataviewJS.

#### Scenario: Template renders on Obsidian iOS
- **WHEN** the template is applied in Obsidian on an iPhone
- **THEN** the note is created and all sections render correctly without errors
