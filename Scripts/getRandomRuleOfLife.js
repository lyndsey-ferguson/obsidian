function getFileContents(path) {
    const file = app.vault.getFileByPath(path);
    return app.vault.cachedRead(file);
}

function getRandomRule(rules) {
    const randomRuleIndex = Math.floor(Math.random() * rules.length);
    return rules[randomRuleIndex].trim();
}

/*
    Call this from your markdown with templater

    <% tp.user.getRandomRuleOfLife("path/to/rules-of-life.md") %>

    Example:

    <% tp.user.getRandomRuleOfLife("TestFixtures/FakeRulesOfLife.md") %>
*/
function getRandomRuleOfLife (rulesOfLifeFilePath) {
    return getFileContents(rulesOfLifeFilePath).then(value => {
        const regex = /\d+\.\s*(.*)(:?\n|$)/g; 

        const matches = value.matchAll(regex);
        let rules = [];
        for (const match of matches) {
            rules.push(match[1]);
        }
        const rule = getRandomRule(rules);
        return rule;
    });
}
module.exports = getRandomRuleOfLife;