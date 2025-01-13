const {
    getAllFilesWithCalloutsWithGivenTypes
} = require('../getRandomCountOfCalloutsWithGivenTypes');

beforeAll(() => {
  jest.spyOn(global.Math, 'random').mockReturnValue(0.123456789);
});

test('Expect files with callouts to be found', async () => {
  const expected = ['TestFixtures/FakeRulesOfLife.md'];
  const calloutTypes = ['memory', 'quote', 'thought', 'note'];
  const actualFiles = await getAllFilesWithCalloutsWithGivenTypes(calloutTypes);
  let actualFilePaths = []
  for (let i = 0; i < actualFiles.length; i++) {
    const file = actualFiles[i];
    actualFilePaths.push(file.path);
  }
  expect(actualFilePaths).toContainEqual(expected);
});

afterAll(() => {
  jest.restoreAllMocks();
});
