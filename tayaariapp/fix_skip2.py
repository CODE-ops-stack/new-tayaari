import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

skip_replacement = '''    fun skipQuestion() {
        val currentState = _uiState.value
        val question = currentState.currentQuestion
        if (question != null) {
            _uiState.update { state ->
                val updatedSkipped = state.skippedQuestions.toMutableSet()
                if (!state.userAnswers.containsKey(question.id)) {
                    updatedSkipped.add(question.id)
                }
                val newScore = computeScore(state.userAnswers, updatedSkipped, questionsQueue, currentProfile)
                state.copy(
                    skippedQuestions = updatedSkipped,
                    currentScore = newScore
                )
            }
        }
        generateNextQuestion()
    }'''

content = re.sub(r'    fun skipQuestion\(\) \{.*?\n        generateNextQuestion\(\)\n    \}', skip_replacement, content, flags=re.DOTALL)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
