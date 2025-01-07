const getRandomRuleOfLife = require('../getRandomRuleOfLife');

beforeAll(() => {
  jest.spyOn(global.Math, 'random').mockReturnValue(0.123456789);
});

test('Expect \'random\' rule of life to be exercise', async () => {
  await expect(
    getRandomRuleOfLife('./TestFixtures/FakeRulesOfLife.md')
  ).resolves.toBe('Exercise.');
});

afterAll(() => {
  jest.restoreAllMocks();
});
