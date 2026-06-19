function daysDiff(date1, date2) {
  const d1 = new Date(date1.getFullYear(), date1.getMonth(), date1.getDate());
  const d2 = new Date(date2.getFullYear(), date2.getMonth(), date2.getDate());
  return Math.round(Math.abs(d1 - d2) / (1000 * 60 * 60 * 24));
}

function lastDayOfMonth(year, month) {
  return new Date(year, month + 1, 0);
}

function isNearPeriodEnd(date, periodEnd) {
  return daysDiff(date, periodEnd) <= 3;
}

function checkMonthly(date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const currEnd = lastDayOfMonth(year, month);
  const prevEnd = lastDayOfMonth(month === 0 ? year - 1 : year, month === 0 ? 11 : month - 1);
  return isNearPeriodEnd(date, currEnd) || isNearPeriodEnd(date, prevEnd);
}

const QUARTER_END_MONTHS = [2, 5, 8, 11]; // Mar, Jun, Sep, Dec (0-indexed)

function checkQuarterly(date) {
  const year = date.getFullYear();
  return QUARTER_END_MONTHS.some(m => isNearPeriodEnd(date, lastDayOfMonth(year, m))) ||
         isNearPeriodEnd(date, lastDayOfMonth(year - 1, 11));
}

function checkYearly(date) {
  const year = date.getFullYear();
  return isNearPeriodEnd(date, new Date(year, 11, 31)) ||
         isNearPeriodEnd(date, new Date(year - 1, 11, 31));
}

module.exports = { checkMonthly, checkQuarterly, checkYearly, isNearPeriodEnd, daysDiff, lastDayOfMonth };
