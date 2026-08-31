test('Test getMarkdownFiles()', async () => {
  const markdownFiles = await app.vault.getMarkdownFiles();
  const rulesOfLifeFile = markdownFiles.find(f => f.basename === "FakeRulesOfLife.md");

  expect(rulesOfLifeFile).not.toBeNull();
});