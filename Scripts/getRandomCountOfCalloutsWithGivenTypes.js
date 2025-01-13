
function getAllFilesWithCalloutsWithGivenTypes(calloutTypes) {
    const allFiles = app.vault.getFiles();
    const markdownFiles = allFiles.filter((file) => file.extension === '.md');

    const re = new RegExp(String.raw`>\[!(${calloutTypes.join('|')})`, "g");

    const markdownFilesWithCallouts = markdownFiles.filter((file) => {
        app.vault.cachedRead(file).then(contents => {
            const matches = contents.matchAll(re);
        });
    });
    return markdownFiles;
}

module.exports = { getAllFilesWithCalloutsWithGivenTypes };