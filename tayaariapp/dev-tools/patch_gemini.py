with open("app/src/main/java/com/example/repository/GeminiRepository.kt", "r") as f:
    content = f.read()

content = content.replace(
    "                chapterCode = \"AI-Generated-Concept\", // Using chapterCode to hold source for now, or you can add it to MCQQuestion\n                questionText = jsonObject.getString(\"questionText\"),",
    "                chapterCode = \"AI-Generated-Concept\",\n                questionText = jsonObject.getString(\"questionText\"),\n                questionFormatType = format,"
)

content = content.replace(
    "            chapterCode = \"AI-Generated-Concept\",\n            questionText = \"Which of the following statements about the Earth's interior is correct?\",",
    "            chapterCode = \"AI-Generated-Concept\",\n            questionText = \"Which of the following statements about the Earth's interior is correct?\",\n            questionFormatType = \"Statement-based\","
)

with open("app/src/main/java/com/example/repository/GeminiRepository.kt", "w") as f:
    f.write(content)
