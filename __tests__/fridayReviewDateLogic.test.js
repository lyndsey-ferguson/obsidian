const { checkMonthly, checkQuarterly, checkYearly, isNearPeriodEnd, lastDayOfMonth } = require('../lib/fridayReviewDateLogic');

describe('isNearPeriodEnd — core ±3-day rule', () => {
  test('triggers when date is exactly 3 days before period end', () => {
    const date = new Date(2026, 0, 28); // Jan 28
    const periodEnd = new Date(2026, 0, 31); // Jan 31
    expect(isNearPeriodEnd(date, periodEnd)).toBe(true);
  });

  test('triggers when date is exactly 3 days after period end', () => {
    const date = new Date(2026, 1, 3); // Feb 3
    const periodEnd = new Date(2026, 0, 31); // Jan 31
    expect(isNearPeriodEnd(date, periodEnd)).toBe(true);
  });

  test('does not trigger when date is 4 days before period end', () => {
    const date = new Date(2026, 0, 27); // Jan 27
    const periodEnd = new Date(2026, 0, 31); // Jan 31
    expect(isNearPeriodEnd(date, periodEnd)).toBe(false);
  });

  test('does not trigger when date is 4 days after period end', () => {
    const date = new Date(2026, 1, 4); // Feb 4
    const periodEnd = new Date(2026, 0, 31); // Jan 31
    expect(isNearPeriodEnd(date, periodEnd)).toBe(false);
  });
});

describe('checkMonthly', () => {
  test('triggers for date in new month within 3 days of prior month-end (Jan 2 near Dec 31)', () => {
    expect(checkMonthly(new Date(2026, 0, 2))).toBe(true);
  });

  test('triggers for date 3 days before current month-end', () => {
    expect(checkMonthly(new Date(2026, 0, 28))).toBe(true); // Jan 28, Jan 31 is 3 days away
  });

  test('triggers on month-end itself', () => {
    expect(checkMonthly(new Date(2026, 0, 31))).toBe(true); // Jan 31
  });

  test('triggers for date 1 day before month-end (month ends Saturday, Friday is 1 day before)', () => {
    expect(checkMonthly(new Date(2026, 0, 30))).toBe(true); // Jan 30
  });

  test('does not trigger when more than 3 days from any month-end', () => {
    expect(checkMonthly(new Date(2026, 0, 10))).toBe(false);
  });

  test('triggers for date 2 days after month-end (month ends Wednesday, Friday is 2 days later)', () => {
    expect(checkMonthly(new Date(2026, 2, 2))).toBe(true); // Mar 2, 2 days after Feb 28
  });
});

describe('checkQuarterly', () => {
  test('triggers for date near March 31 (Q1 end), 3 days before', () => {
    expect(checkQuarterly(new Date(2026, 2, 28))).toBe(true);
  });

  test('triggers for date near June 30 (Q2 end), 1 day after', () => {
    expect(checkQuarterly(new Date(2026, 6, 1))).toBe(true);
  });

  test('triggers for date near September 30 (Q3 end)', () => {
    expect(checkQuarterly(new Date(2026, 8, 27))).toBe(true);
  });

  test('triggers for date near December 31 (Q4 end) from prior year', () => {
    expect(checkQuarterly(new Date(2026, 0, 2))).toBe(true);
  });

  test('does not trigger for date near February 28/29 (not a quarter-end)', () => {
    expect(checkQuarterly(new Date(2026, 1, 27))).toBe(false);
  });

  test('does not trigger for mid-quarter date', () => {
    expect(checkQuarterly(new Date(2026, 1, 15))).toBe(false);
  });
});

describe('checkYearly', () => {
  test('triggers for date 3 days before December 31', () => {
    expect(checkYearly(new Date(2025, 11, 28))).toBe(true);
  });

  test('triggers for date 2 days after December 31 (in new year)', () => {
    expect(checkYearly(new Date(2026, 0, 2))).toBe(true);
  });

  test('triggers on December 31 itself', () => {
    expect(checkYearly(new Date(2025, 11, 31))).toBe(true);
  });

  test('does not trigger for date more than 3 days from December 31', () => {
    expect(checkYearly(new Date(2026, 0, 5))).toBe(false);
  });

  test('does not trigger for date more than 3 days before December 31', () => {
    expect(checkYearly(new Date(2025, 11, 27))).toBe(false);
  });
});

describe('period overlap impossibility', () => {
  test('no date is within 3 days of two different month-ends', () => {
    const year = 2025;
    const allMonthEnds = [
      lastDayOfMonth(year - 1, 11),
      ...Array.from({ length: 12 }, (_, m) => lastDayOfMonth(year, m)),
      lastDayOfMonth(year + 1, 0),
    ];

    const start = new Date(year, 0, 1);
    const end = new Date(year, 11, 31);
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const nearCount = allMonthEnds.filter(me => isNearPeriodEnd(d, me)).length;
      expect(nearCount).toBeLessThanOrEqual(1);
    }
  });
});
