## ADDED Requirements

### Requirement: Closest-Friday rule determines period review eligibility
The date logic SHALL determine that a given Friday triggers a period review if and only if the absolute difference in calendar days between that Friday and the last day of the period is less than or equal to 3.

#### Scenario: Friday is 3 days before period end
- **WHEN** `|friday - lastDayOfPeriod|` equals 3 (Friday is 3 days before)
- **THEN** the period review IS triggered

#### Scenario: Friday is 3 days after period end
- **WHEN** `|friday - lastDayOfPeriod|` equals 3 (Friday is 3 days after)
- **THEN** the period review IS triggered

#### Scenario: Friday is 4 days from period end
- **WHEN** `|friday - lastDayOfPeriod|` equals 4
- **THEN** the period review is NOT triggered

### Requirement: Monthly period uses last calendar day of each month
The date logic SHALL use the last calendar day of the current and previous month when checking monthly eligibility, to handle Fridays that fall in the new month but are still closest to the prior month-end.

#### Scenario: Friday in new month is closest to prior month-end
- **WHEN** a Friday in January falls within 3 days after December 31
- **THEN** the monthly review IS triggered (checking against December 31)

#### Scenario: Friday is not near any month boundary
- **WHEN** a Friday is more than 3 days from the end of both the current and previous month
- **THEN** the monthly review is NOT triggered

### Requirement: Quarterly period uses quarter-end dates
The date logic SHALL use the quarter-end dates (March 31, June 30, September 30, December 31) when evaluating quarterly eligibility, checking both the current and previous quarter-end.

#### Scenario: Friday near March 31 triggers quarterly
- **WHEN** a Friday falls within 3 days of March 31
- **THEN** the quarterly review IS triggered

#### Scenario: Friday near end of non-quarter month does not trigger quarterly
- **WHEN** a Friday falls within 3 days of February 28/29 (not a quarter-end)
- **THEN** the quarterly review is NOT triggered

### Requirement: Yearly period uses December 31
The date logic SHALL use December 31 of the current and previous year when evaluating yearly eligibility.

#### Scenario: Friday near December 31 triggers yearly
- **WHEN** a Friday falls within 3 days of December 31
- **THEN** the yearly review IS triggered

#### Scenario: Friday in early January beyond 3 days does not trigger yearly
- **WHEN** a Friday in January is more than 3 days after December 31
- **THEN** the yearly review is NOT triggered

### Requirement: Period overlap never occurs
No single Friday SHALL simultaneously satisfy the closest-Friday condition for two different instances of the same period type (e.g., two different month-ends), since all calendar months are at least 28 days long and the window is only ±3 days.

#### Scenario: Single Friday cannot be closest to two month-ends
- **WHEN** any Friday is evaluated against all month-end dates in a year
- **THEN** at most one month-end satisfies the ±3-day condition
