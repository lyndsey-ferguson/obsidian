## ADDED Requirements

### Requirement: Ribbon button creates a new note from the Friday Review Template
The Commander ribbon button SHALL invoke Templater's "Create new note from template" command targeting specifically the Friday Review Template, resulting in a new note with the correct sections for the current date.

#### Scenario: User taps ribbon button on Mac
- **WHEN** the user clicks the Friday Review ribbon icon in the Obsidian sidebar on macOS
- **THEN** a new note is created, the Friday Review Template is applied, and the note opens with the correct review sections

#### Scenario: User taps ribbon button on iPhone
- **WHEN** the user taps the Friday Review ribbon icon in the Obsidian mobile toolbar on iOS
- **THEN** a new note is created, the Friday Review Template is applied, and the note opens with the correct review sections

### Requirement: Ribbon button is visible on both desktop and mobile
The Commander ribbon button SHALL be configured to appear on both desktop and mobile Obsidian interfaces.

#### Scenario: Button visible on desktop sidebar
- **WHEN** the user opens Obsidian on macOS
- **THEN** the Friday Review icon is visible in the left ribbon

#### Scenario: Button visible on mobile toolbar
- **WHEN** the user opens Obsidian on iOS
- **THEN** the Friday Review icon is accessible in the mobile toolbar/ribbon area

### Requirement: DataviewJS buttons removed from existing review templates
The four existing review templates SHALL have their `dataviewjs` code blocks removed, since those blocks are non-functional on iOS and are superseded by the Commander ribbon button.

#### Scenario: Weekly Review Template has no DataviewJS block
- **WHEN** `Weekly Review Template.md` is opened in Obsidian
- **THEN** no DataviewJS code block is rendered and no Mac-only button appears

#### Scenario: Monthly, Quarter, Year Review Templates have no DataviewJS blocks
- **WHEN** any of `Monthly Review Template.md`, `Quarter Review Template.md`, or `Year Review Template.md` is opened
- **THEN** no DataviewJS code block is present in those files
