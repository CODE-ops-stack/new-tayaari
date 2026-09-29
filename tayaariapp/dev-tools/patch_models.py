with open("app/src/main/java/com/example/model/TestModels.kt", "r") as f:
    content = f.read()

import re

# Update ExamQuestion
content = content.replace(
    "    val questionText: String\n}",
    "    val questionText: String\n    val questionFormatType: String\n}"
)

# Update TestUiState
new_ui_state = """data class TestUiState(
    val currentTestMode: TestMode? = null,
    val currentQuestion: ExamQuestion? = null,
    val timeRemaining: Int = 0,
    val isBookmarked: Boolean = false,
    val selectedOptionId: String? = null,
    val userTypedAnswer: String = "",
    val questionNumber: Int = 1,
    val currentScore: Int = 0,
    val totalQuestionsInSet: Int = 10,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isTestFinished: Boolean = false,
    val userAnswers: Map<String, String> = emptyMap(),
    val allQuestions: List<ExamQuestion> = emptyList()
)"""

content = re.sub(r'data class TestUiState\(.*?\)', new_ui_state, content, flags=re.DOTALL)

with open("app/src/main/java/com/example/model/TestModels.kt", "w") as f:
    f.write(content)
