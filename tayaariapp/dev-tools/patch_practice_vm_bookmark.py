with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r") as f:
    content = f.read()

import re

if "import kotlinx.coroutines.flow.first" not in content:
    content = content.replace("import kotlinx.coroutines.flow.update", "import kotlinx.coroutines.flow.update\nimport kotlinx.coroutines.flow.first")

old_show = """    private fun showCurrentQuestion() {
        if (currentQuestionIndex >= 0 && currentQuestionIndex < questionsQueue.size) {
            val q = questionsQueue[currentQuestionIndex]
            _uiState.update { state ->
                state.copy(
                    currentQuestion = q,
                    timeRemaining = if (q is MCQQuestion) q.timeLimitSeconds else 90,
                    selectedOptionId = null,
                    isBookmarked = false,
                    questionNumber = currentQuestionIndex + 1,
                    isLoading = false,
                    totalQuestionsInSet = questionsQueue.size,
                    allQuestions = questionsQueue.toList()
                )
            }
            startTimer()
        }
    }"""

new_show = """    private fun showCurrentQuestion() {
        if (currentQuestionIndex >= 0 && currentQuestionIndex < questionsQueue.size) {
            val q = questionsQueue[currentQuestionIndex]
            viewModelScope.launch {
                val isMarked = localRepository.isBookmarked(q.id).first()
                _uiState.update { state ->
                    state.copy(
                        currentQuestion = q,
                        timeRemaining = if (q is MCQQuestion) q.timeLimitSeconds else 90,
                        selectedOptionId = null,
                        isBookmarked = isMarked,
                        questionNumber = currentQuestionIndex + 1,
                        isLoading = false,
                        totalQuestionsInSet = questionsQueue.size,
                        allQuestions = questionsQueue.toList()
                    )
                }
                startTimer()
            }
        }
    }"""

content = content.replace(old_show, new_show)

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w") as f:
    f.write(content)
