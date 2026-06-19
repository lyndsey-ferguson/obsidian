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
const targetPath = dailyFolder + '/' + title + '.md';
const existingFile = app.vault.getAbstractFileByPath(targetPath);
if (existingFile) {
    const tempFile = app.workspace.getActiveFile();
    await app.workspace.getLeaf(false).openFile(existingFile);
    if (tempFile) await app.vault.delete(tempFile);
    return;
}
await tp.file.move(dailyFolder + '/' + title);
-%>
<% tp.file.include("[[Weekly Review Template]]") %>
<%* if (isMonthly) { -%>

<% tp.file.include("[[Monthly Review Template]]") %>
<%* } -%>
<%* if (isQuarterly) { -%>

<% tp.file.include("[[Quarter Review Template]]") %>
<%* } -%>
<%* if (isYearly) { -%>

<% tp.file.include("[[Year Review Template]]") %>
<%* } -%>
