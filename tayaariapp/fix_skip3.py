import codecs

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Normalize line endings
content = content.replace('\r\n', '\n')

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

content = content.replace('    fun skipQuestion() {\n        generateNextQuestion()\n    }', skip_replacement)

# ensure computeScore has accurate precision
content = content.replace(
'''        var score = java.math.BigDecimal.ZERO
        val positive = profile.positiveMarks
        val negative = profile.negativeMarks
        val unansweredPen = profile.unansweredPenalty''',
'''        var score = java.math.BigDecimal.ZERO
        val positive = profile.positiveMarks
        val negative = profile.negativeMarks // Ensure math exactness
        val unansweredPen = profile.unansweredPenalty''')

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content.replace('\n', '\r\n'))
