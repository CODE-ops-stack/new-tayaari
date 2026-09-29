package com.example.repository

import com.example.model.RecommendedAction
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class NextBestActionEngine(
    private val localRepository: LocalRepository
) {
    suspend fun getNextBestAction(examId: String): RecommendedAction = withContext(Dispatchers.IO) {
        val profile = localRepository.getLearnerProfile()
        val blueprint = com.example.model.ExamBlueprintRegistry.getBlueprint(examId)
        val isSpeedHeavy = blueprint?.recommendedPracticeMode?.contains("Speed") == true

        if (profile.totalQuestionsAttempted > 20 && profile.overallAccuracy < 0.3) {
            return@withContext RecommendedAction.RecoveryMode(
                reason = "Your recent accuracy is low. Let's do a Recovery Mode session to rebuild foundational confidence.",
                importance = "CRITICAL"
            )
        }

        val confirmedConfusion = profile.activeConfusions.find { it.evidenceLevel == "CONFIRMED_CONFUSION" }
        if (confirmedConfusion != null) {
            val parts = confirmedConfusion.pairId.split("_")
            val cA = if (parts.isNotEmpty()) parts[0] else "A"
            val cB = if (parts.size > 1) parts[1] else "B"
            return@withContext RecommendedAction.Contrast(
                conceptA = cA,
                conceptB = cB,
                reason = "You have a confirmed confusion between '${cA}' and '${cB}'. Contrast Lab will fix this.",
                importance = "CRITICAL"
            )
        }

        if (profile.revisionDebt > 15) {
            return@withContext RecommendedAction.Revision(
                pendingCount = profile.revisionDebt,
                reason = "You have ${profile.revisionDebt} concepts overdue for revision. Clearing this debt prevents forgetting.",
                importance = "HIGH"
            )
        }

        val highRiskTrap = profile.activeTraps.maxByOrNull { it.frequency }
        if (highRiskTrap != null && highRiskTrap.frequency >= 3) {
            return@withContext RecommendedAction.TrapTraining(
                trapType = highRiskTrap.trapType,
                reason = "You frequently fall for '${highRiskTrap.trapType}' traps. Trap Training will build immunity.",
                importance = "HIGH"
            )
        }
        
        val transferAnalytics = localRepository.getFalseMasteryReport()
        val falseMastery = transferAnalytics.find { it.state == KnowledgeState.FALSE_MASTERY }
        if (falseMastery != null) {
            return@withContext RecommendedAction.TransferPractice(
                reason = falseMastery.recommendation,
                importance = "HIGH"
            )
        }

        if (profile.weakTopics.isNotEmpty()) {
            val weakest = profile.weakTopics.first()
            if (weakest.total > 5) {
                return@withContext RecommendedAction.MistakeReplay(
                    reason = "You're struggling with ${weakest.topicName}. Mistake Replay will help you learn from past errors.",
                    importance = "MEDIUM"
                )
            } else {
                return@withContext RecommendedAction.PrerequisiteRepair(
                    reason = "You're finding ${weakest.topicName} difficult. Let's step back and repair the prerequisites.",
                    importance = "MEDIUM"
                )
            }
        }

        if (isSpeedHeavy && profile.totalQuestionsAttempted > 50) {
            return@withContext RecommendedAction.TimedDrill(
                reason = "Your exam requires speed. Let's do a Timed Drill to improve your time management.",
                importance = "MEDIUM"
            )
        } else if (profile.totalQuestionsAttempted > 100) {
            return@withContext RecommendedAction.ExamSimulation(
                reason = "You have built sufficient baseline knowledge. Take a mini Exam Simulation to test your readiness.",
                importance = "MEDIUM"
            )
        }

        return@withContext RecommendedAction.SmartPractice(
            topicName = "Mixed",
            reason = "Continue with Smart Practice to build a balanced conceptual foundation.",
            importance = "LOW"
        )
    }
}
