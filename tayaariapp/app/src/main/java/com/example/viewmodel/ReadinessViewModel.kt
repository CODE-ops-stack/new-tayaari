package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.repository.LocalRepository
import com.example.repository.LearnerProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class ReadinessPillar(
    val title: String,
    val description: String,
    val status: String, // "STRONG", "WATCH", "NEEDS WORK", "INSUFFICIENT DATA"
    val evidence: List<String>
)

data class ReadinessUiState(
    val isLoading: Boolean = true,
    val pillars: List<ReadinessPillar> = emptyList()
)

class ReadinessViewModel(
    private val repository: LocalRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(ReadinessUiState())
    val uiState: StateFlow<ReadinessUiState> = _uiState

    init {
        loadReadiness()
    }

    private fun loadReadiness() {
        viewModelScope.launch {
            val profile = repository.learnerModelEngine.getLearnerProfile()
            val totalQ = profile.totalQuestionsAttempted
            
            val pillars = mutableListOf<ReadinessPillar>()
            
            // Coverage
            val coverageStatus = if (totalQ < 10) "INSUFFICIENT DATA" else if (totalQ < 300) "NEEDS WORK" else if (totalQ < 1000) "WATCH" else "STRONG"
            pillars.add(ReadinessPillar(
                "Coverage",
                "How much of the target syllabus has meaningful practice evidence?",
                coverageStatus,
                if (coverageStatus == "INSUFFICIENT DATA") listOf("Not enough questions attempted ($totalQ).") else listOf("Attempted $totalQ questions across ${profile.topicPerformances.size} topics.")
            ))

            // Revision Stability (Retention)
            val revStatus = if (totalQ < 50) "INSUFFICIENT DATA" else if (profile.revisionDebt > 50) "NEEDS WORK" else if (profile.revisionDebt > 15) "WATCH" else "STRONG"
            pillars.add(
                ReadinessPillar(
                    title = "Retention (Revision Stability)",
                    description = "Is performance stable across spaced attempts?",
                    status = revStatus,
                    evidence = if (revStatus == "INSUFFICIENT DATA") listOf("Not enough spaced-revision evidence yet.") else listOf("Revision Debt: ${profile.revisionDebt} items due.", if (profile.revisionDebt <= 15) "Retention is stable." else "Forgetting curves suggest decay.")
                )
            )
            
            // Mistake Repair
            val mStatus = if (totalQ < 100) "INSUFFICIENT DATA" else if (profile.activeTraps.size > 5) "NEEDS WORK" else if (profile.activeTraps.isNotEmpty()) "WATCH" else if (profile.repairedMistakesCount > 0) "STRONG" else "INSUFFICIENT DATA"
            pillars.add(
                ReadinessPillar(
                    title = "Mistake Repair",
                    description = "Are recurring errors actually disappearing?",
                    status = mStatus,
                    evidence = if (mStatus == "INSUFFICIENT DATA") listOf("Trap readiness cannot be assessed yet.") else listOf("Active Traps: ${profile.activeTraps.size}", "Active Confusions: ${profile.activeConfusions.size}", "Successfully Repaired: ${profile.repairedMistakesCount}")
                )
            )
            
            // Confidence
            var over = 0.0
            var under = 0.0
            profile.confidenceCalibration.forEach { (c, a) ->
                if (c == "Sure" && a < 0.7) over += (0.7 - a)
                if (c == "Guess" && a > 0.5) under += (a - 0.5)
            }
            val cStatus = if (totalQ < 50) "INSUFFICIENT DATA" else if (over > 0.2) "NEEDS WORK" else if (under > 0.2) "WATCH" else "STRONG"
            pillars.add(
                ReadinessPillar(
                    title = "Confidence Calibration",
                    description = "Does confidence correspond reasonably with results?",
                    status = cStatus,
                    evidence = if (cStatus == "INSUFFICIENT DATA") listOf("Confidence tracking requires more attempts.") else listOf("High Confidence Accuracy: ${(profile.confidenceCalibration["Sure"] ?: 0.0) * 100}%", if (over > 0.2) "High Risk: Overconfident." else "Confidence matches knowledge.")
                )
            )
            
            // Transfer
            pillars.add(ReadinessPillar("Transfer", "Can the learner solve different formulations?", "INSUFFICIENT DATA", listOf("Not enough transfer data yet.")))
            // Exam Format
            pillars.add(ReadinessPillar("Exam Format", "How does the learner perform on target question styles?", "INSUFFICIENT DATA", listOf("Awaiting format-level distribution mapping.")))
            // Timing
            pillars.add(ReadinessPillar("Timing", "Can the learner solve within realistic time?", "INSUFFICIENT DATA", listOf("Timing variance is not statistically significant yet.")))
            // Decision Quality
            pillars.add(ReadinessPillar("Decision Quality", "Does the learner make sensible attempt/skip decisions?", "INSUFFICIENT DATA", listOf("Decision Lab needs more strategic skips to evaluate.")))
            
            _uiState.value = ReadinessUiState(isLoading = false, pillars = pillars)
        }
    }
}
