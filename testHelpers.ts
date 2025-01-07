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

function mockObsidianApp() {
  return {
    vault : {
      getFileByPath : jest.fn(path => path),
      cachedRead: jest.fn(path => localFileRead(path)) 
    }
  };
}

global.app = mockObsidianApp();