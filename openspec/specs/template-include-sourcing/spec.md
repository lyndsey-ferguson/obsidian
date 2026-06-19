## Requirements

### Requirement: Friday Review Template sources weekly content from Weekly Review Template file
The Friday Review Template SHALL use `tp.file.include("[[Weekly Review Template]]")` to render the weekly section body, rather than containing the content inline.

#### Scenario: Weekly section content matches the template file
- **WHEN** the Friday Review Template is applied
- **THEN** the weekly section content is identical to the current contents of `Weekly Review Template.md`

#### Scenario: Edit to Weekly Review Template is reflected in next Friday review
- **WHEN** `Weekly Review Template.md` is edited (e.g., a new checklist item added)
- **THEN** the next note created from the Friday Review Template includes the updated content without any change to the Friday Review Template itself

### Requirement: Friday Review Template sources monthly content from Monthly Review Template file
The Friday Review Template SHALL use `tp.file.include("[[Monthly Review Template]]")` to render the monthly section body when `isMonthly` is true.

#### Scenario: Monthly section content matches the template file
- **WHEN** the Friday Review Template is applied on a monthly Friday
- **THEN** the monthly section content is identical to the current contents of `Monthly Review Template.md`

### Requirement: Friday Review Template sources quarterly content from Quarter Review Template file
The Friday Review Template SHALL use `tp.file.include("[[Quarter Review Template]]")` to render the quarterly section body when `isQuarterly` is true.

#### Scenario: Quarterly section content matches the template file
- **WHEN** the Friday Review Template is applied on a quarterly Friday
- **THEN** the quarterly section content is identical to the current contents of `Quarter Review Template.md`

### Requirement: Friday Review Template sources yearly content from Year Review Template file
The Friday Review Template SHALL use `tp.file.include("[[Year Review Template]]")` to render the yearly section body when `isYearly` is true.

#### Scenario: Yearly section content matches the template file
- **WHEN** the Friday Review Template is applied on a yearly Friday
- **THEN** the yearly section content is identical to the current contents of `Year Review Template.md`

### Requirement: Conditional section logic is unchanged
The Friday Review Template SHALL preserve all existing conditional rendering logic — weekly always included, monthly/quarterly/yearly gated on the ±3-day rule — regardless of whether content is hardcoded or file-sourced.

#### Scenario: Non-monthly Friday omits monthly section
- **WHEN** the template is applied on a Friday more than 3 days from any month-end
- **THEN** the rendered note contains no monthly section content, consistent with prior behavior
