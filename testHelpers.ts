const path = require('path');
const glob = require('glob');

function tfileFromPath(filepath) {
  return {
    basename: path.basename(filepath),
    extension: path.extname(filepath),
    path: filepath
  }
}

function localFileRead(path) {
  return new Promise((resolve, reject) => {
      const fs = require('fs');

      fs.readFile(path, 'utf8', (err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(data);
        }
      });
  });
}

async function localGetMarkdownFiles() {
  const filepaths = await glob.glob('**/*.md', { ignore: 'node_modules/**' });
  return filepaths.map((filepath) => tfileFromPath(filepath))
}

function mockObsidianApp() {
  return {
    vault : {
      getFileByPath : jest.fn(filepath => tfileFromPath(filepath)),
      cachedRead: jest.fn(tfile => localFileRead(tfile.path)),
      getMarkdownFiles: jest.fn(() => localGetMarkdownFiles())
    }
  };
}

global.app = mockObsidianApp();