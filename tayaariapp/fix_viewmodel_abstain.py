import codecs

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Replace submitAnswerWithConfidence logic
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
        
        _uiState.update { 
            val updatedAnswers = it.userAnswers.toMutableMap()
            updatedAnswers[question.id] = optionId
            
            var points = when {
                isCorrect -> currentProfile?.positiveMarks ?: java.math.BigDecimal.ONE
                isAbstain -> java.math.BigDecimal.ZERO
                else -> currentProfile?.negativeMarks?.negate() ?: java.math.BigDecimal("-0.33")
            }
            if (isFatalElimination) points = points.subtract(java.math.BigDecimal("0.5")) // extra penalty for eliminating correct answer
            
            it.copy(
                selectedOptionId = optionId,
                pendingOptionId = null,
                selectedConfidence = confidence,
                currentScore = it.currentScore.add(points),
                userAnswers = updatedAnswers
            ) 
        }
        
        // Trap Analytics: if incorrect, log the trap
        // Log revision attempt
        val associatedTrap = if (isFatalElimination) "Fatal Elimination" else question.distractorDissections.find { it.optionId == optionId }?.trapType
        if (!isAbstain) {
            viewModelScope.launch { localRepository.logRevisionAttempt(question.id, isCorrect, associatedTrap) }
        }
        val timeSpent = if (question is MCQQuestion) (question.timeLimitSeconds - (_uiState.value.timeRemaining)) else 0
        viewModelScope.launch { localRepository.logQuestionAttempt(question.id, isCorrect, confidence, timeSpent, associatedTrap) }

        if (!isCorrect && !isAbstain) {'''

# Find the exact method and replace
content = content.replace('''    fun submitAnswerWithConfidence(confidence: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        val optionId = currentState.pendingOptionId ?: return
        
        val question = currentState.currentQuestion as? MCQQuestion ?: return
        val isCorrect = question.correctAnswerId == optionId
        val crossedOutCorrect = currentState.crossedOutOptionIds.contains(question.correctAnswerId)
        val isFatalElimination = crossedOutCorrect
        
        _uiState.update { 
            val updatedAnswers = it.userAnswers.toMutableMap()
            updatedAnswers[question.id] = optionId
            
            var points = if (isCorrect) (currentProfile?.positiveMarks ?: java.math.BigDecimal.ONE) else (currentProfile?.negativeMarks?.negate() ?: java.math.BigDecimal("-0.33"))
            if (isFatalElimination) points = points.subtract(java.math.BigDecimal("0.5")) // extra penalty for eliminating correct answer
            
            it.copy(
                selectedOptionId = optionId,
                pendingOptionId = null,
                selectedConfidence = confidence,
                currentScore = it.currentScore.add(points),
                userAnswers = updatedAnswers
            ) 
        }
        // Trap Analytics: if incorrect, log the trap
        // Log revision attempt
        val associatedTrap = if (isFatalElimination) "Fatal Elimination" else question.distractorDissections.find { it.optionId == optionId }?.trapType
        viewModelScope.launch { localRepository.logRevisionAttempt(question.id, isCorrect, associatedTrap) }
        val timeSpent = if (question is MCQQuestion) (question.timeLimitSeconds - (_uiState.value.timeRemaining)) else 0
        viewModelScope.launch { localRepository.logQuestionAttempt(question.id, isCorrect, confidence, timeSpent, associatedTrap) }

        if (!isCorrect) {''', submit_replacement)

# Now skipQuestion
skip_replacement = '''    fun skipQuestion() {
        val unansweredPenalty = currentProfile?.unansweredPenalty ?: java.math.BigDecimal.ZERO
        if (unansweredPenalty > java.math.BigDecimal.ZERO) {
            _uiState.update { 
                it.copy(
                    currentScore = it.currentScore.subtract(unansweredPenalty)
                ) 
            }
        }
        generateNextQuestion()
    }'''

content = content.replace('''    fun skipQuestion() {
        generateNextQuestion()
    }''', skip_replacement)

# Also when timer runs out, it does skipQuestion, so this penalty will apply there automatically.

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
