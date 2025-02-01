const getCalloutsInMarkdownFile = require('../getCalloutsInMarkdownFile');

test('Expect a box of chocolates', async () => {
  const callouts = await getCalloutsInMarkdownFile('./TestFixtures/FakeGetMarkdownFilesTesting/FakeDirectory/French Pulldogs.md');
  expect(callouts).toContain('>[!quote]\n>Life is like a box of chocolates, you never know what you will get.')
  expect(callouts).toContain('>[!quote]\n>An animal is man in peace.\n>>[!important]\n>>This is a lesson few learn.');
});
