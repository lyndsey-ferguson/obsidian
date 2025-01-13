const fs = require('fs');
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

function asyncGetFiles() {
  return new Promise((resolve, reject) => {
    const directoryPath = './'; // Replace with your directory path

    fs.readdir(directoryPath, (err, filePaths) => {
      if (err !== null) {
        reject(err);
      } else {
        let files = [];
        for (let i = 0; i < filePaths.length; i++) {
          let fp = filePaths[i];
          let file = {
            basename: path.basename(fp),
            path: fp,
            extension: path.extname(fp),
          };
          files.push(file); 
        }
        resolve(files);
      }
    }, { recursive: true });
  });
}
async function getFiles() {
  let files = await asyncGetFiles();
  return files;
}

function mockObsidianApp() {
  return {
    vault : {
      getFileByPath : jest.fn(path => path),
      cachedRead: jest.fn(path => localFileRead(path)),
      getFiles: jest.fn(async () => getFiles())
    }
  };
}

global.app = mockObsidianApp();