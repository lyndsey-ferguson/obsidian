
function getFileContents(path) {
  const file = app.vault.getFileByPath(path);
  return app.vault.cachedRead(file);
}

/*
    Call this from your markdown with templater

    <% tp.user.getRandomRuleOfLife("path/to/markdown.md") %>

    Example:

    <% tp.user.getCalloutsInMarkdownFile('TestFixtures/FakeGetMarkdownFilesTesting/FakeDirectory/French Pulldogs.md') %>
*/

function getCalloutsInMarkdownFile(f) {
  return getFileContents(f).then(value => {
    const lines = value.split(/\r?\n/);

    let callouts = [];
    let isParsingCallout = false;
    const regex = /^>\[!(quote|important|note)\]/
    
    let callout = "";
    for (const line of lines) {
      if (!isParsingCallout && line.match(regex)) {
        isParsingCallout = true
        callout = line.trimEnd();
      } else if (isParsingCallout && line.startsWith('>')) {
        callout = callout + '\n' + line.trimEnd();
      } else {
        if (callout !== "") {
          callouts.push(callout);
          callout = '';
        }
        isParsingCallout = false;
      }
    }

    return callouts;
  });
}

module.exports = getCalloutsInMarkdownFile;