async function getMarkdownFiles() {
  return app.vault.getMarkdownFiles();
}

async function getFileContents(file) {
  return await app.vault.cachedRead(file);
}

async function getCalloutsFromFile(file) {
  const content = await getFileContents(file);
  if (!content) return [];

  const lines = content.split(/\r?\n/);
  const callouts = [];

  let isParsingCallout = false;
  let calloutBuffer = "";
  const calloutRegex = /^>\s*\[!(\w+)\]/; // Matches any Obsidian callout type

  for (const line of lines) {
    if (!isParsingCallout && calloutRegex.test(line)) {
      isParsingCallout = true;
      calloutBuffer = line.trimEnd();
    } else if (isParsingCallout && line.startsWith('>')) {
      calloutBuffer += '\n' + line.trimEnd();
    } else {
      if (calloutBuffer) {
        callouts.push(calloutBuffer);
        calloutBuffer = '';
      }
      isParsingCallout = false;
    }
  }

  if (calloutBuffer) {
    callouts.push(calloutBuffer);
  }

  return callouts;
}

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

async function saveCalloutsJSON(data) {
  const jsonFile = "callouts.json";
  const file = app.vault.getAbstractFileByPath(jsonFile);
  const jsonString = JSON.stringify(data, null, 2);

  if (file) {
    await app.vault.modify(file, jsonString);
  } else {
    await app.vault.create(jsonFile, jsonString);
  }
}

async function updateCalloutsJSON() {
  let data = await loadCalloutsJSON();
  const lastGenerated = data.last_generated ? new Date(data.last_generated) : new Date(0);
  const files = await getMarkdownFiles();
  let updated = false;

  for (const file of files) {
    const fileModifiedTime = new Date(file.stat.mtime); // Get file modification time

    if (fileModifiedTime > lastGenerated) {
      const callouts = await getCalloutsFromFile(file);
      const existingEntry = data.file_callouts.find(entry => entry.filepath === file.path);

      if (!existingEntry) {
        data.file_callouts.push({ filepath: file.path, callouts });
      } else {
        existingEntry.callouts = callouts;
      }
      updated = true;
    }
  }

  if (updated) {
    data.last_generated = new Date().toISOString();
    await saveCalloutsJSON(data);
    console.log("Callouts JSON updated!");
  } else {
    console.log("No updates needed for callouts JSON.");
  }
}



module.exports = updateCalloutsJSON;