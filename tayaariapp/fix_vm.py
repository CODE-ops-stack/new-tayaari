import os

path = 'c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/java/com/example/viewmodel/PracticeViewModel.kt'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('fun submitAnswerWithConfidence(confidence: String) {', 'fun submitAnswer(optionId: String) {\n        onOptionPending(optionId)\n        val confidence = "Certain"')

jump_to_question = '''
    fun jumpToQuestion(index: Int) {
        if (index in 0 until _uiState.value.allQuestions.size) {
            val newQ = _uiState.value.allQuestions[index]
            _uiState.update { 
                it.copy(
                    currentQuestion = newQ,
                    questionNumber = index + 1,
                    selectedOptionId = it.userAnswers[newQ.id],
                    pendingOptionId = null,
                    detectedConfusionPair = null,
                    crossedOutOptionIds = emptySet()
                )
            }
            updateBookmarkStatus()
        }
    }

    fun toggleBookmark() {'''

text = text.replace('fun toggleBookmark() {', jump_to_question)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed PracticeViewModel.kt')
