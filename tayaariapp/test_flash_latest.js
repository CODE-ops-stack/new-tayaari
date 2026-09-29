const { GoogleGenerativeAI } = require("@google/generative-ai");
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
async function run() {
  const model = genAI.getGenerativeModel({ model: "gemini-flash-latest", generationConfig: { responseMimeType: "application/json", maxOutputTokens: 8192 } });
  const prompt = "Write a JSON object containing a difficult UPSC-level multiple choice question about Indian Rivers, with 4 options and correct answer. Do not include markdown tags.";
  const result = await model.generateContent(prompt);
  console.log(result.response.text());
}
run();
