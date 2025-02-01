const path = require('path');

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

function tfileFromPath(filepath) {
  return {
    basename: path.basename(filepath),
    extension: path.extname(filepath),
    path: filepath
  }
}
function mockObsidianApp() {
  return {
    vault : {
      getFileByPath : jest.fn(filepath => tfileFromPath(filepath)),
      cachedRead: jest.fn(tfile => localFileRead(tfile.path))
    }
  };
}

global.app = mockObsidianApp();