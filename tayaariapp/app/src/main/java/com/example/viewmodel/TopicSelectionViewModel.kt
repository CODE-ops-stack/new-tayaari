package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.Topic
import com.example.model.ExamBlueprint
import com.example.repository.LocalRepository
import com.example.repository.UserPreferencesRepository
import com.example.repository.StopDoingEngine
import com.example.repository.PracticeRecommendationResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import com.example.model.RecommendedAction
import com.example.repository.NextBestActionEngine

data class TopicUIModel(
    val topic: Topic,
    val availableCount: Int
)

class TopicSelectionViewModel(
    private val actionEngine: NextBestActionEngine,
    private val localRepository: LocalRepository,
    private val userPrefsRepo: UserPreferencesRepository
) : ViewModel() {

    private val stopDoingEngine = StopDoingEngine(localRepository.learnerModelEngine, com.example.repository.FalseMasteryEngine(localRepository))

    private val _topics = MutableStateFlow<List<TopicUIModel>>(emptyList())
    val topics: StateFlow<List<TopicUIModel>> = _topics.asStateFlow()

    private val _profile = MutableStateFlow<ExamBlueprint?>(null)
    val profile: StateFlow<ExamBlueprint?> = _profile.asStateFlow()

    private val _nextAction = MutableStateFlow<RecommendedAction?>(null)
    val nextAction: StateFlow<RecommendedAction?> = _nextAction.asStateFlow()

    private val _interceptResult = MutableStateFlow<PracticeRecommendationResult?>(null)
    val interceptResult: StateFlow<PracticeRecommendationResult?> = _interceptResult.asStateFlow()

    // Temporary storage for when they bypass the intercept
    var pendingPracticeIntent: Triple<String, String, String>? = null

    val isSyncing = com.example.repository.CloudQuestionSyncService.isSyncing.asStateFlow()
    val syncStatusMessage = com.example.repository.CloudQuestionSyncService.syncStatusMessage.asStateFlow()

    init {
        viewModelScope.launch {
            userPrefsRepo.selectedExamProfiles.collectLatest { p ->
                val selectedProfile = p.firstOrNull() ?: com.example.model.ExamBlueprintRegistry.blueprints.first()
                _profile.value = selectedProfile
                loadTopics(selectedProfile)
                loadNextAction(selectedProfile.examId)
            }
        }
    }

    fun onPracticeIntent(topicName: String, tier: String, format: String, onApproved: (String, String, String) -> Unit) {
        if (topicName == "Global" || format == "Paper Twin") {
            onApproved(topicName, tier, format)
            return
        }
        viewModelScope.launch {
            val result = stopDoingEngine.evaluatePracticeIntent(topicName)
            if (result is PracticeRecommendationResult.Proceed) {
                onApproved(topicName, tier, format)
            } else {
                pendingPracticeIntent = Triple(topicName, tier, format)
                _interceptResult.value = result
            }
        }
    }

    fun clearIntercept() {
        _interceptResult.value = null
        pendingPracticeIntent = null
    }

    fun bypassIntercept(onApproved: (String, String, String) -> Unit) {
        pendingPracticeIntent?.let {
            onApproved(it.first, it.second, it.third)
        }
        clearIntercept()
    }

    private suspend fun loadNextAction(examId: String) {
        _nextAction.value = actionEngine.getNextBestAction(examId)
    }

    private var topicsJob: kotlinx.coroutines.Job? = null
    private fun loadTopics(p: ExamBlueprint) {
        topicsJob?.cancel()
        topicsJob = viewModelScope.launch {
            localRepository.getAllTopics().collectLatest { topicsList ->
                val uiModels = topicsList.map { topic ->
                    val count = com.example.repository.CloudQuestionSyncService.getTopicCount(topic.id)
                    TopicUIModel(topic, count)
                }
                _topics.value = uiModels
            }
        }
    }

    fun refreshFromCloud(context: android.content.Context) {
        viewModelScope.launch {
            com.example.repository.CloudQuestionSyncService.syncWithCloud(context, force = true)
        }
    }
}





