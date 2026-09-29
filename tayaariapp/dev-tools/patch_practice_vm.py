with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r") as f:
    content = f.read()

import re

# Update showCurrentQuestion
content = content.replace(
    "                    totalQuestionsInSet = questionsQueue.size\n                )\n            }\n            startTimer()",
    "                    totalQuestionsInSet = questionsQueue.size,\n                    allQuestions = questionsQueue.toList()\n                )\n            }\n            startTimer()"
)

# Update startPractice
content = content.replace(
    "        _uiState.update { it.copy(isLoading = true, questionNumber = 0, currentScore = 0) }",
    "        _uiState.update { it.copy(isLoading = true, questionNumber = 0, currentScore = 0, isTestFinished = false, userAnswers = emptyMap()) }"
)

# Update generateNextQuestion
clean_next = """    fun generateNextQuestion() {
        if (currentQuestionIndex + 1 < questionsQueue.size) {
            currentQuestionIndex++
            showCurrentQuestion()
        } else {
            // End of test
            _uiState.update { it.copy(isTestFinished = true) }
        }
    }"""
content = re.sub(r'    fun generateNextQuestion\(\) \{.*?    \}', clean_next, content, flags=re.DOTALL)

# Update onOptionSelected
old_option_selected = """    fun onOptionSelected(optionId: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        
        val question = currentState.currentQuestion as? MCQQuestion
        val isCorrect = question?.correctAnswerId == optionId
        
        _uiState.update { 
            it.copy(
                selectedOptionId = optionId,
                currentScore = if (isCorrect) it.currentScore + 1 else it.currentScore
            ) 
        }"""
        
new_option_selected = """    fun onOptionSelected(optionId: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        
        val question = currentState.currentQuestion as? MCQQuestion ?: return
        val isCorrect = question.correctAnswerId == optionId
        
        _uiState.update { 
            val updatedAnswers = it.userAnswers.toMutableMap()
            updatedAnswers[question.id] = optionId
            it.copy(
                selectedOptionId = optionId,
                currentScore = if (isCorrect) it.currentScore + 1 else it.currentScore,
                userAnswers = updatedAnswers
            ) 
        }"""

content = content.replace(old_option_selected, new_option_selected)

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w") as f:
    f.write(content)
