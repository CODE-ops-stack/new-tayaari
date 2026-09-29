package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.Question
import com.example.repository.LocalRepository
import com.example.repository.ReplayCandidate
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

enum class ReplayState {
    LOADING,
    NO_CANDIDATES,
    REVIEW_MISTAKE, // Showing original answer, correct answer, and evidence
    REPAIR, // Concept repair, contrast lab, etc.
    ALTERNATE_QUESTION, // Testing transfer
    RESULT
}

data class MistakeReplayUiState(
    val currentState: ReplayState = ReplayState.LOADING,
    val candidate: ReplayCandidate? = null,
    val alternateQuestion: Question? = null,
    val altOptions: List<String> = emptyList(),
    val altCorrectIndex: Int = -1,
    val selectedOptionIndex: Int? = null,
    val outcomeState: String? = null,
    val nextBestAction: String? = null
)

class MistakeReplayViewModel(
    private val repository: LocalRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(MistakeReplayUiState())
    val uiState: StateFlow<MistakeReplayUiState> = _uiState

    init {
        loadCandidate()
    }

    fun loadCandidate() { viewModelScope.launch { loadCandidateSync() } }

    suspend fun loadCandidateSync() {
        _uiState.value = _uiState.value.copy(currentState = ReplayState.LOADING)
        val candidate = repository.mistakeReplayEngine.getHighestPriorityCandidate()
        if (candidate != null) {
            _uiState.value = _uiState.value.copy(
                currentState = ReplayState.REVIEW_MISTAKE,
                candidate = candidate
            )
        } else {
            _uiState.value = _uiState.value.copy(currentState = ReplayState.NO_CANDIDATES)
        }
    }

    fun commitToRepair() {
        _uiState.value = _uiState.value.copy(currentState = ReplayState.REPAIR)
    }

    fun proceedToAlternate() { viewModelScope.launch { proceedToAlternateSync() } }

    suspend fun proceedToAlternateSync() {
        val original = _uiState.value.candidate?.originalQuestion ?: return
        val dbQuestion = repository.mistakeReplayEngine.findAlternateQuestion(original)
        
        if (dbQuestion != null) {
            _uiState.value = _uiState.value.copy(
                currentState = ReplayState.ALTERNATE_QUESTION,
                                alternateQuestion = dbQuestion,
                altOptions = parseOptions(dbQuestion.options),
                altCorrectIndex = parseCorrectIndex(dbQuestion.options, dbQuestion.correctAnswer),
                selectedOptionIndex = null
            )
        } else {
            submitAlternateAnswerSync(true)
        }
    }
    
    fun selectOption(index: Int) {
        _uiState.value = _uiState.value.copy(selectedOptionIndex = index)
    }

    fun submitAlternateAnswer(isCorrect: Boolean) { viewModelScope.launch { submitAlternateAnswerSync(isCorrect) } }

    suspend fun submitAlternateAnswerSync(isCorrect: Boolean) {
        val candidate = _uiState.value.candidate ?: return
                val altQuestion = _uiState.value.alternateQuestion
        
        val outcome = repository.mistakeReplayEngine.onReplayCompleted(candidate, altQuestion, isCorrect)
        val nba = repository.mistakeReplayEngine.getNextBestAction(outcome)
        
        _uiState.value = _uiState.value.copy(
            currentState = ReplayState.RESULT,
            outcomeState = outcome,
            nextBestAction = nba
        )
    }
    private fun parseOptions(jsonStr: String): List<String> {
        val list = mutableListOf<String>()
        try {
            val arr = org.json.JSONArray(jsonStr)
            for (i in 0 until arr.length()) {
                list.add(arr.getJSONObject(i).getString("text"))
            }
        } catch (e: Exception) {}
        return list
    }

    private fun parseCorrectIndex(jsonStr: String, correctId: String): Int {
        try {
            val arr = org.json.JSONArray(jsonStr)
            for (i in 0 until arr.length()) {
                if (arr.getJSONObject(i).getString("id") == correctId) return i
            }
        } catch (e: Exception) {}
        return -1
    }
}
