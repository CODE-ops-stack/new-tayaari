import codecs

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Replace submitAnswerWithConfidence again to use functional scoring and handle skipped removal
submit_replacement = '''    fun submitAnswerWithConfidence(confidence: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        val optionId = currentState.pendingOptionId ?: return
        
        val question = currentState.currentQuestion as? MCQQuestion ?: return
        val isCorrect = question.correctAnswerId == optionId
        val crossedOutCorrect = currentState.crossedOutOptionIds.contains(question.correctAnswerId)
        val isFatalElimination = crossedOutCorrect
        
        val selectedOption = question.options.find { it.id == optionId }
        val isAbstain = selectedOption?.role == com.example.model.OptionRole.ABSTAIN
        
        _uiState.update { state ->
            val updatedAnswers = state.userAnswers.toMutableMap()
            updatedAnswers[question.id] = optionId
            
            val updatedSkipped = state.skippedQuestions.toMutableSet()
            updatedSkipped.remove(question.id)
            
            val newScore = computeScore(updatedAnswers, updatedSkipped, questionsQueue, currentProfile)
            
            state.copy(
                selectedOptionId = optionId,
                pendingOptionId = null,
                selectedConfidence = confidence,
                currentScore = newScore,
                userAnswers = updatedAnswers,
                skippedQuestions = updatedSkipped
            ) 
        }
        
        val associatedTrap = if (isFatalElimination) "Fatal Elimination" else question.distractorDissections.find { it.optionId == optionId }?.trapType
        if (!isAbstain) {
            viewModelScope.launch { localRepository.logRevisionAttempt(question.id, isCorrect, associatedTrap) }
        }
        val timeSpent = if (question is MCQQuestion) (question.timeLimitSeconds - (_uiState.value.timeRemaining)) else 0
        viewModelScope.launch { localRepository.logQuestionAttempt(question.id, isCorrect, confidence, timeSpent, associatedTrap) }

        if (!isCorrect && !isAbstain) {'''

# Find the current submitAnswerWithConfidence
import re
pattern = re.compile(r'    fun submitAnswerWithConfidence\(confidence: String\) \{.*?\n        if \(\!isCorrect && \!isAbstain\) \{', re.DOTALL)
content = pattern.sub(submit_replacement, content)

# Replace skipQuestion
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
    
pattern_skip = re.compile(r'    fun skipQuestion\(\) \{.*?\n        generateNextQuestion\(\)\n    \}', re.DOTALL)
content = pattern_skip.sub(skip_replacement, content)

# Add computeScore function
compute_score_func = '''
    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {
        var score = java.math.BigDecimal.ZERO
        val positive = profile?.positiveMarks ?: java.math.BigDecimal.ONE
        val negative = profile?.negativeMarks ?: java.math.BigDecimal("0.33")
        val unansweredPen = profile?.unansweredPenalty ?: java.math.BigDecimal.ZERO
        
        for (q in questions) {
            val mcq = q as? MCQQuestion ?: continue
            if (answers.containsKey(q.id)) {
                val ans = answers[q.id]
                val option = mcq.options.find { it.id == ans }
                if (mcq.correctAnswerId == ans) {
                    score = score.add(positive)
                } else if (option?.role == com.example.model.OptionRole.ABSTAIN) {
                    // zero penalty
                } else {
                    score = score.subtract(negative)
                }
            } else if (skipped.contains(q.id)) {
                score = score.subtract(unansweredPen)
            }
        }
        return score
    }
'''
content = content.replace('class PracticeViewModel(', 'class PracticeViewModel(\n' + compute_score_func)

# Also ensure timer auto-skip correctly marks it skipped!
# Actually skipQuestion is called. But startTimer doesn't call skipQuestion, it just advances?
# Let's check startTimer
with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
