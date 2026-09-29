with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "r") as f:
    content = f.read()

import re

# We will modify the mapping to extract options and clean up the text
new_mapping = """        // Convert DB questions to MCQQuestion (ExamQuestion)
        for (q in dbQuestions) {
            var rawText = q.questionText
            val optionsList = mutableListOf<Option>()
            var correctAns = q.correctAnswer ?: "opt_a"
            var explanation = q.explanation ?: ""
            
            // Try to extract Correct Answer line
            val caRegex = Regex("Correct Answer: Option ([a-d])", RegexOption.IGNORE_CASE)
            val caMatch = caRegex.find(rawText)
            if (caMatch != null) {
                correctAns = "opt_${caMatch.groupValues[1].lowercase()}"
                rawText = rawText.replace(caRegex, "").trim()
            }
            
            // Try to extract options (a), (b), (c), (d)
            val optRegex = Regex("\\\\(([a-d])\\\\)\\\\s+(.*?)(?=\\\\n\\\\([a-d]\\\\)|$)", RegexOption.DOT_MATCHES_ALL or RegexOption.IGNORE_CASE)
            val matches = optRegex.findAll(rawText)
            
            if (matches.count() > 0) {
                for (match in matches) {
                    val optLetter = match.groupValues[1].lowercase()
                    val optText = match.groupValues[2].trim()
                    optionsList.add(Option("opt_$optLetter", optText))
                    rawText = rawText.replace(match.value, "")
                }
            } else {
                optionsList.add(Option("opt_a", "Option A"))
                optionsList.add(Option("opt_b", "Option B"))
                optionsList.add(Option("opt_c", "Option C"))
                optionsList.add(Option("opt_d", "Option D"))
            }
            
            rawText = rawText.trim()
            
            selectedQuestions.add(
                MCQQuestion(
                    id = q.id.toString(),
                    chapterCode = q.source ?: "DB-Real-PYQ",
                    questionText = rawText,
                    questionFormatType = q.format,
                    timeLimitSeconds = 90,
                    options = optionsList,
                    correctAnswerId = correctAns,
                    correctExplanation = explanation,
                    distractorDissections = emptyList()
                )
            )
        }"""

content = re.sub(r'        // Convert DB questions to MCQQuestion \(ExamQuestion\).*?        }        // 2\. If short', new_mapping + "\n\n        // 2. If short", content, flags=re.DOTALL)

with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "w") as f:
    f.write(content)
