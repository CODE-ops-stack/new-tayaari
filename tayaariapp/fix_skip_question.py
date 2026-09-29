import codecs

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

skip_target = '''    fun skipQuestion() {
        generateNextQuestion()
    }'''

skip_replacement = '''    fun skipQuestion() {
        val currentState = _uiState.value
        val question = currentState.currentQuestion ?: return
        
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
        generateNextQuestion()
    }'''

content = content.replace(skip_target, skip_replacement)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
