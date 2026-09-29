package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.ConfusionEventEntity
import com.example.model.*
import com.example.repository.LocalRepository
import com.example.repository.QuestionSelectionEngine
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.math.BigDecimal
import com.example.model.ExactFraction

class PracticeViewModel(
    private val repository: LocalRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TestUiState())
    val uiState: StateFlow<TestUiState> = _uiState.asStateFlow()

    private var currentTopic: String = ""
    private var currentTier: String = ""
    private var currentFormat: String = ""
    private var currentProfile: ExamBlueprint? = null

    val trapAnalytics = repository.getAllTraps()

    fun startPractice(topicName: String, profile: ExamBlueprint, tier: String, format: String) {
        currentTopic = topicName
        currentTier = tier
        currentFormat = format
        currentProfile = profile
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val engine = QuestionSelectionEngine(repository)
            val questions = engine.getQuestionsForProfile(topicName, profile, 20, format, null)
            _uiState.update {
                it.copy(
                    allQuestions = questions,
                    currentQuestion = questions.firstOrNull(),
                    questionNumber = 1,
                    totalQuestionsInSet = questions.size,
                    selectedOptionId = null,
                    pendingOptionId = null,
                    selectedConfidence = null,
                    detectedConfusionPair = null,
                    isTestFinished = questions.isEmpty(),
                    userAnswers = emptyMap(),
                    crossedOutOptionIds = emptySet(),
                    skippedQuestions = emptySet(),
                    isLoading = false,
                    currentScore = ExactFraction.ZERO
                )
            }
            updateBookmarkStatus()
        }
    }

    private fun updateBookmarkStatus() {
        val q = _uiState.value.currentQuestion
        if (q != null) {
            viewModelScope.launch {
                repository.isBookmarked(q.id).collect { isBookmarked ->
                    _uiState.update { it.copy(isBookmarked = isBookmarked) }
                }
            }
        }
    }

    fun toggleOptionCrossedOut(optionId: String) {
        _uiState.update {
            val updated = it.crossedOutOptionIds.toMutableSet()
            if (updated.contains(optionId)) updated.remove(optionId) else updated.add(optionId)
            it.copy(crossedOutOptionIds = updated)
        }
    }

    fun onOptionPending(optionId: String) {
        _uiState.update { it.copy(pendingOptionId = optionId) }
    }

    fun submitAnswerWithConfidence(confidence: String) {
        val pending = _uiState.value.pendingOptionId ?: return
        val currentQ = _uiState.value.currentQuestion
        val isCorrect = if (currentQ is MCQQuestion) pending == currentQ.correctAnswerId else false

        if (currentQ is MCQQuestion && !isCorrect) {
            viewModelScope.launch {
                val selectedText = currentQ.options.find { it.id == pending }?.text ?: ""
                val initialResult = com.example.repository.ConfusionNetwork.detectConfusion(
                    currentQ.questionText, selectedText
                )
                if (initialResult != null) {
                    val history = repository.getConfusionEventsForPair(initialResult.pair.id)
                    var finalEvidenceLevel = initialResult.evidenceLevel
                    
                    if (finalEvidenceLevel == com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION) {
                        val distinctQuestions = history.map { it.questionId }.toSet()
                        
                        val totalEvidence = if (distinctQuestions.contains(currentQ.id.toString())) {
                            distinctQuestions.size
                        } else {
                            distinctQuestions.size + 1
                        }
                        
                        if (totalEvidence >= 4) {
                            finalEvidenceLevel = com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONFUSION
                        } else if (totalEvidence >= 2) {
                            finalEvidenceLevel = com.example.repository.ConfusionEvidenceLevel.EMERGING_CONFUSION
                        }
                    }
                    
                    val finalResult = initialResult.copy(evidenceLevel = finalEvidenceLevel)
                    
                    repository.logConfusionEvent(
                        pairId = finalResult.pair.id,
                        questionId = currentQ.id,
                        selectedOptionText = selectedText,
                        evidenceLevel = finalEvidenceLevel
                    )
                    
                    _uiState.update { it.copy(detectedConfusionPair = finalResult) }
                }
            }
        }

        _uiState.update {
            val newAnswers = it.userAnswers.toMutableMap()
            newAnswers[currentQ?.id ?: ""] = pending
            
            val newScore = computeScore(newAnswers, it.skippedQuestions, it.allQuestions, currentProfile)
            
            it.copy(
                selectedOptionId = pending,
                selectedConfidence = confidence,
                pendingOptionId = null,
                userAnswers = newAnswers,
                currentScore = newScore
            )
        }

        viewModelScope.launch {
            if (currentQ is MCQQuestion) {
                val distractor = currentQ.distractorDissections?.find { it.optionId == pending }
                repository.logQuestionAttempt(
                    questionId = currentQ.id,
                    outcome = if (isCorrect) AttemptOutcome.CORRECT else AttemptOutcome.INCORRECT,
                    confidence = confidence,
                    timeSpentSeconds = 30,
                    trapFallenInto = distractor?.trapType
                )
                if (distractor != null && distractor.trapType != null && distractor.dissection != null) {
                    repository.incrementTrap(distractor.trapType, currentQ.questionText, distractor.dissection)
                }
            }
        }
    }

    fun skipQuestion() {
        val currentQ = _uiState.value.currentQuestion
        _uiState.update {
            val newSkipped = it.skippedQuestions.toMutableSet()
            newSkipped.add(currentQ?.id ?: "")
            
            val newScore = computeScore(it.userAnswers, newSkipped, it.allQuestions, currentProfile)
            
            it.copy(
                selectedOptionId = "SKIP",
                pendingOptionId = null,
                skippedQuestions = newSkipped,
                currentScore = newScore
            )
        }
        viewModelScope.launch {
            if (currentQ != null) {
                repository.logQuestionAttempt(
                    questionId = currentQ.id,
                    outcome = AttemptOutcome.ABSTAINED,
                    confidence = null,
                    timeSpentSeconds = 10,
                    trapFallenInto = null
                )
            }
        }
    }

    fun startPaperTwin(paper: com.example.repository.GeneratedPaper, profile: ExamBlueprint) {
        currentTopic = "Paper Twin"
        currentTier = "Mixed"
        currentFormat = "Mixed"
        currentProfile = profile
        _uiState.update {
            it.copy(
                allQuestions = paper.questions,
                currentQuestion = paper.questions.firstOrNull(),
                questionNumber = 1,
                totalQuestionsInSet = paper.questions.size,
                selectedOptionId = null,
                pendingOptionId = null,
                selectedConfidence = null,
                detectedConfusionPair = null,
                isTestFinished = paper.questions.isEmpty(),
                isLoading = false
            )
        }
    }

    fun generateNextQuestion() {
        val state = _uiState.value
        val currentIndex = state.questionNumber - 1
        if (currentIndex < state.allQuestions.size - 1) {
            val nextQ = state.allQuestions[currentIndex + 1]
            _uiState.update {
                it.copy(
                    currentQuestion = nextQ,
                    questionNumber = it.questionNumber + 1,
                    selectedOptionId = it.userAnswers[nextQ.id] ?: if (it.skippedQuestions.contains(nextQ.id)) "SKIP" else null,
                    pendingOptionId = null,
                    selectedConfidence = null,
                    detectedConfusionPair = null,
                    crossedOutOptionIds = emptySet()
                )
            }
            updateBookmarkStatus()
        } else {
            _uiState.update { it.copy(isTestFinished = true) }
        }
    }

    fun generatePreviousQuestion() {
        val state = _uiState.value
        val currentIndex = state.questionNumber - 1
        if (currentIndex > 0) {
            val prevQ = state.allQuestions[currentIndex - 1]
            _uiState.update {
                it.copy(
                    currentQuestion = prevQ,
                    questionNumber = it.questionNumber - 1,
                    selectedOptionId = it.userAnswers[prevQ.id] ?: if (it.skippedQuestions.contains(prevQ.id)) "SKIP" else null,
                    pendingOptionId = null,
                    selectedConfidence = null,
                    detectedConfusionPair = null,
                    crossedOutOptionIds = emptySet()
                )
            }
            updateBookmarkStatus()
        }
    }

    fun toggleBookmark() {
        val q = _uiState.value.currentQuestion ?: return
        val currentlyBookmarked = _uiState.value.isBookmarked
        viewModelScope.launch {
            if (currentlyBookmarked) {
                repository.removeBookmark(q.id)
            } else {
                repository.addBookmark(q)
            }
            _uiState.update { it.copy(isBookmarked = !currentlyBookmarked) }
        }
    }

    fun restartPractice() {
        _uiState.update {
            it.copy(
                currentQuestion = it.allQuestions.firstOrNull(),
                questionNumber = 1,
                selectedOptionId = null,
                pendingOptionId = null,
                selectedConfidence = null,
                detectedConfusionPair = null,
                isTestFinished = false,
                userAnswers = emptyMap(),
                crossedOutOptionIds = emptySet(),
                skippedQuestions = emptySet(),
                currentScore = ExactFraction.ZERO
            )
        }
        updateBookmarkStatus()
    }
    
    companion object {
        fun computeScore(
            answers: Map<String, String>,
            skipped: Set<String>,
            questions: List<ExamQuestion>,
            profile: ExamBlueprint?
        ): ExactFraction {
            if (profile == null) return ExactFraction.ZERO
            
            var correctCount = 0
            var incorrectCount = 0
            for (q in questions) {
                if (q !is MCQQuestion) continue
                if (skipped.contains(q.id)) continue
                
                val ans = answers[q.id]
                if (ans != null) {
                    if (ans == q.correctAnswerId) {
                        correctCount++
                    } else {
                        val isAbstain = q.options.find { it.id == ans }?.role == OptionRole.ABSTAIN
                        if (!isAbstain) {
                            incorrectCount++
                        }
                    }
                }
            }
            
            val posMarks = ExactFraction.fromBigDecimal(profile.positiveMarks)
            val correctFrac = posMarks * ExactFraction(correctCount.toLong(), 1L)
            val num = profile.negativePenaltyRule.numerator.toLong()
            val den = profile.negativePenaltyRule.denominator.toLong()
            val penRule = ExactFraction(num, den)
            
            val penaltyFrac = ExactFraction(incorrectCount.toLong(), 1L) * posMarks * penRule
            return correctFrac - penaltyFrac
        }
    }
}
