const fs = require('fs');
const pdf = require('pdf-parse');

const file = "/app/applet/source-material/oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf";

async function analyze() {
    console.log("File:", file.split('/').pop());
    try {
        let dataBuffer = fs.readFileSync(file);
        let data = await pdf(dataBuffer, { max: 10 });
        console.log("Pages:", data.numpages);
        console.log("Content snippet:", data.text.replace(/\n/g, ' ').substring(0, 500).trim());
    } catch (err) {
        console.log("Error:", err.message);
    }
}

analyze();
