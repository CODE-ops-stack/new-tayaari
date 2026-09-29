import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Replace submitAnswerWithConfidence completely
submit_func = '''    fun submitAnswerWithConfidence(confidence: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        val optionId = currentState.pendingOptionId ?: return
        
        val question = currentState.currentQuestion as? MCQQuestion ?: return
        val isCorrect = question.correctAnswerId == optionId
        
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
        
        timerJob?.cancel()

        // Trap Analytics: if incorrect, log the trap
        val associatedTrap = question.distractorDissections.find { it.optionId == optionId }?.trapType
        if (!isAbstain) {
            viewModelScope.launch { localRepository.logRevisionAttempt(question.id, isCorrect, associatedTrap) }
        }
        val timeSpent = if (question is MCQQuestion) (question.timeLimitSeconds - (_uiState.value.timeRemaining)) else 0
        viewModelScope.launch { localRepository.logQuestionAttempt(question.id, isCorrect, confidence, timeSpent, associatedTrap) }

        if (!isCorrect && !isAbstain) {
            val dissection = question.distractorDissections.find { it.optionId == optionId }
            if (dissection != null) {
                viewModelScope.launch {
                    val trapType = dissection.trapType
                    var trapEntity = localRepository.getTrap(trapType)
                    if (trapEntity == null) {
                        trapEntity = com.example.database.TrapAnalyticsEntity(trapType = trapType, frequency = 0, failedQuestionsJson = "[]")
                    }
                    
                    val currentQuestions = try {
                        val arr = org.json.JSONArray(trapEntity.failedQuestionsJson)
                        val list = mutableListOf<org.json.JSONObject>()
                        for (i in 0 until arr.length()) list.add(arr.getJSONObject(i))
                        list
                    } catch (e: Exception) { mutableListOf() }
                    
                    val newFailedObj = org.json.JSONObject().apply {
                        put("questionText", question.questionText)
                        put("correctExplanation", question.correctExplanation)
                        put("dissection", dissection.dissection)
                    }
                    currentQuestions.add(newFailedObj)
                    
                    val updatedJson = org.json.JSONArray(currentQuestions).toString()
                    val updatedEntity = trapEntity.copy(
                        frequency = trapEntity.frequency + 1,
                        failedQuestionsJson = updatedJson
                    )
                    localRepository.insertTrap(updatedEntity)
                }
            }
        }
    }'''

content = re.sub(r'    fun submitAnswerWithConfidence\(confidence: String\) \{.*?(?=    fun toggleBookmark\(\))', submit_func + '\n\n', content, flags=re.DOTALL)

# Replace skipQuestion completely
skip_func = '''    fun skipQuestion() {
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
    
content = re.sub(r'    fun skipQuestion\(\) \{.*?\n        generateNextQuestion\(\)\n    \}', skip_func, content, flags=re.DOTALL)

# Modify startTimer to also record skipped if it times out
timer_func = '''    private fun startTimer() {
        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            while (_uiState.value.timeRemaining > 0 && _uiState.value.selectedOptionId == null) {
                delay(1000L)
                _uiState.update { it.copy(timeRemaining = it.timeRemaining - 1) }
            }
            if (_uiState.value.timeRemaining <= 0 && _uiState.value.selectedOptionId == null) {
                // Timer expired without answer -> record as unanswered/skipped
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
            }
        }
    }'''
    
content = re.sub(r'    private fun startTimer\(\) \{.*?(?=    fun toggleOptionCrossedOut)', timer_func + '\n\n', content, flags=re.DOTALL)

# Ensure computeScore removes unsafe fallbacks
compute_score_safe = '''    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {
        if (profile == null) error("Missing blueprint configuration")
        
        var score = java.math.BigDecimal.ZERO
        val positive = profile.positiveMarks
        val negative = profile.negativeMarks
        val unansweredPen = profile.unansweredPenalty
        
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
    }'''
    
content = re.sub(r'    private fun computeScore.*?return score\n    \}', compute_score_safe, content, flags=re.DOTALL)

# Fix marks lost report fallbacks
marks_lost_safe = '''    private fun computeMarksLostAnalysis(): List<String> {
        val currentState = _uiState.value
        val report = mutableListOf<String>()
        var incorrectCount = 0
        var skippedCount = 0
        
        val profile = currentProfile ?: return listOf("Error: Missing blueprint configuration")
        
        for (q in questionsQueue) {
            val mcq = q as? MCQQuestion ?: continue
            val ans = currentState.userAnswers[q.id]
            if (ans != null) {
                val option = mcq.options.find { it.id == ans }
                if (ans != mcq.correctAnswerId && option?.role != com.example.model.OptionRole.ABSTAIN) {
                    incorrectCount++
                }
            } else if (currentState.skippedQuestions.contains(q.id)) {
                skippedCount++
            }
        }
        
        val neg = profile.negativeMarks
        val unans = profile.unansweredPenalty
        
        if (incorrectCount > 0) {
            val lostToNeg = java.math.BigDecimal(incorrectCount).multiply(neg)
            report.add("Lost " + lostToNeg.toPlainString() + " marks due to " + incorrectCount + " incorrect answers.")
        }
        if (skippedCount > 0 && unans > java.math.BigDecimal.ZERO) {
            val lostToSkip = java.math.BigDecimal(skippedCount).multiply(unans)
            report.add("Lost " + lostToSkip.toPlainString() + " marks due to " + skippedCount + " unanswered/skipped questions.")
        }
        
        if (report.isEmpty()) {
            report.add("Perfect score or no penalties applied!")
        }
        
        return report
    }'''

content = re.sub(r'    private fun computeMarksLostAnalysis.*?return report\n    \}', marks_lost_safe, content, flags=re.DOTALL)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
