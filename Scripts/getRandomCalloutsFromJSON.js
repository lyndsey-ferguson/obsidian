
async function loadCalloutsJSON() {
  const jsonFile = "callouts.json";
  const file = app.vault.getAbstractFileByPath(jsonFile);
  if (!file) return { last_generated: null, file_callouts: [] };

  const content = await app.vault.read(file);
  try {
    return JSON.parse(content);
  } catch (error) {
    console.error("Error parsing JSON file:", error);
    return { last_generated: null, file_callouts: [] };
  }
}

async function getRandomCalloutsFromJSON() {
  const data = await loadCalloutsJSON();
  let allCallouts = data.file_callouts.flatMap(entry => entry.callouts);

  if (allCallouts.length === 0) return [];

  // Shuffle and pick 3 random callouts
  const shuffled = allCallouts.sort(() => 0.5 - Math.random());
  console.log(shuffled.slice(0, 3));
  return shuffled.slice(0, 3);
}
module.exports = getRandomCalloutsFromJSON;