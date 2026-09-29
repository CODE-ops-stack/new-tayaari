import re
with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r") as f:
    content = f.read()

bad_part = """    fun generateNextQuestion() {
        if (currentQuestionIndex + 1 < questionsQueue.size) {
            currentQuestionIndex++
            showCurrentQuestion()
        } else {
            // End of test
            _uiState.update { it.copy(isTestFinished = true) }
        }
    } else {
            // End of test or load more
        }
    }"""

good_part = """    fun generateNextQuestion() {
        if (currentQuestionIndex + 1 < questionsQueue.size) {
            currentQuestionIndex++
            showCurrentQuestion()
        } else {
            // End of test
            _uiState.update { it.copy(isTestFinished = true) }
        }
    }"""

content = content.replace(bad_part, good_part)
with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w") as f:
    f.write(content)
