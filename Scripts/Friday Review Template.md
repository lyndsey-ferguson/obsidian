<%*
const today = moment();

function nearEnd(a, b) {
  return Math.abs(a.clone().startOf('day').diff(b.clone().startOf('day'), 'days')) <= 3;
}

const currMonthEnd = today.clone().endOf('month');
const prevMonthEnd = today.clone().subtract(1, 'month').endOf('month');
const isMonthly = nearEnd(today, currMonthEnd) || nearEnd(today, prevMonthEnd);

const currQuarterEnd = today.clone().endOf('quarter');
const prevQuarterEnd = today.clone().subtract(1, 'quarter').endOf('quarter');
const isQuarterly = nearEnd(today, currQuarterEnd) || nearEnd(today, prevQuarterEnd);

const currYearEnd = today.clone().endOf('year');
const prevYearEnd = today.clone().subtract(1, 'year').endOf('year');
const isYearly = nearEnd(today, currYearEnd) || nearEnd(today, prevYearEnd);

// Determine which month, quarter, and year are being reviewed
let reviewMonth = null;
if (isMonthly) {
  reviewMonth = nearEnd(today, currMonthEnd)
    ? today.format('MM')
    : today.clone().subtract(1, 'month').format('MM');
}

let reviewQuarter = null;
if (isQuarterly) {
  const qEnd = nearEnd(today, currQuarterEnd) ? currQuarterEnd : prevQuarterEnd;
  reviewQuarter = Math.floor(qEnd.month() / 3) + 1;
}

let reviewYearStr = null;
if (isYearly) {
  reviewYearStr = nearEnd(today, currYearEnd)
    ? today.format('YYYY')
    : today.clone().subtract(1, 'year').format('YYYY');
}

// Build note title: GGGG-WNN [MNN] [QN] [YYYYY] Review
let title = today.format('GGGG-[W]WW');
if (reviewMonth) title += ` M${reviewMonth}`;
if (reviewQuarter) title += ` Q${reviewQuarter}`;
if (reviewYearStr) title += ` Y${reviewYearStr}`;
title += ' Review';

const dailyFolder = app.internalPlugins.plugins['daily-notes']?.instance?.options?.folder ?? '📓Journal';
await tp.file.move(dailyFolder + '/' + title);
-%>
### Weekly Review

#### Task Creation

- Create tasks for Ana's concerns, interests, or problems expressed this week
- Create tasks to resolve events from last week
- Create tasks to prepare for events in the upcoming week
- Create tasks from last week's incomplete tasks
- Create tasks from last week's journal notes
- Follow up on things waiting for
- Move projects closer to completion
- Attend to issues in environment
- Add major highlights from the past week, month, quarter, or year to current journal

>[!note]
>Quarters start on January 1st, April 1st, July 1st, and October 1st.

#### Reflections

##### What do I need?
##### Work Attitudes check
##### All big rocks for the week completed?
##### What went well?
##### What should be adjusted?
##### What should I stop doing?
##### What should I start doing?

#### After Review

- Categorize tasks in Inbox
- Schedule tasks with definite deadlines
- Review someday list
<%* if (isMonthly) { -%>

#### Monthly Review

#GoalsForMonth

##### Reflections

###### What has improved?

###### What still drains me?

###### What do I want more of?

##### Goals

###### Goals from last month

_Write down the goals you set out for yourself last month. Celebrate the ones you accomplished and make a plan for how to make more progress next month._

###### Goals for next month

_What are the goals you will set out for next month from the Quarter's goals? Do you have atomic habits to accomplish? Do you have the milestones created?_
<%* } -%>
<%* if (isQuarterly) { -%>

#### Quarter Review

#GoalsForQuarter

##### Goals

###### Goals from last quarter

_Write down the goals you set out for yourself last quarter. Celebrate the ones you accomplished and make a plan for how to make more progress next quarter._

###### Goals for next quarter

_What are the goals you will set out for next quarter? Do you have atomic habits to accomplish? Do you have the milestones created?_
<%* } -%>
<%* if (isYearly) { -%>

#### Year Review

##### Goals

###### Goals from last year

_Write down the goals you set out for yourself last year. Celebrate the ones you accomplished and make a plan for how to make more progress next year._

###### Goals for next year

_What are the goals you will set out for next year? Do you have atomic habits to accomplish? Do you have the milestones created?_
<%* } -%>
