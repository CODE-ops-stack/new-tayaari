const fs = require('fs');
const pdf = require('pdf-parse');

let dataBuffer = fs.readFileSync('source-material/question.pdf');

pdf(dataBuffer).then(function(data) {
    fs.writeFileSync('source-material/question_extracted.txt', data.text);
    console.log("Extracted " + data.numpages + " pages to question_extracted.txt");
});
