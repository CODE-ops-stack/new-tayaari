package com.example.repository

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

sealed class PracticeRecommendationResult {
    object Proceed : PracticeRecommendationResult()
    data class RecommendedDiversion(
        val reason: String,
        val evidence: List<String>,
        val recommendedDivertAction: String, 
        val divertRoute: String,
        val currentTopicValue: Double,
        val alternativeValue: Double
    ) : PracticeRecommendationResult()
}

class StopDoingEngine(
    private val learnerModelEngine: LearnerModelEngine,
    private val falseMasteryEngine: FalseMasteryEngine
) {
    suspend fun evaluatePracticeIntent(topicName: String): PracticeRecommendationResult = withContext(Dispatchers.IO) {
        val profile = learnerModelEngine.getLearnerProfile()
        
        val topicPerf = profile.topicPerformances.values.find { it.topicName == topicName }
            ?: return@withContext PracticeRecommendationResult.Proceed 
            
        // Insufficient Data
        if (topicPerf.total < 30) {
            return@withContext PracticeRecommendationResult.Proceed
        }

        // Relative Learning Value calculation
        // Baseline value: 100
        var currentTopicValue = 100.0 - (topicPerf.accuracy * 50.0) // Lower accuracy -> higher value
        var alternativeValue = 0.0
        var divertReason = ""
        var divertEvidence = emptyList<String>()
        var divertAction = ""
        var divertRoute = ""

        // False Mastery Check
        val transfers = falseMasteryEngine.evaluateTransfer()
        val topicTransfer = transfers.find { it.topicName == topicName }
        
        if (topicPerf.accuracy > 0.80 && topicTransfer?.state == KnowledgeState.FALSE_MASTERY) {
            return@withContext PracticeRecommendationResult.RecommendedDiversion(
                reason = "Transfer-First",
                evidence = listOf(
                    "Recall is strong (${(topicPerf.accuracy * 100).toInt()}% on direct questions).",
                    "Transfer evidence is weak (struggling on statement-based variants).",
                    "Practicing mixed formats may be more valuable than direct recall."
                ),
                recommendedDivertAction = "Practice Statement Questions",
                divertRoute = "papertwin", // Simplification: route to papertwin or specialized mode
                currentTopicValue = 20.0,
                alternativeValue = 80.0
            )
        }

        // Check if deeply mastered
        if (topicPerf.accuracy > 0.85 && topicPerf.total > 40 && topicTransfer?.state != KnowledgeState.FALSE_MASTERY) {
            currentTopicValue = 10.0 // Very low ROI to practice again
            
            // Search for better alternatives
            // 1. Revision Debt
            val revisionDebtValue = profile.revisionDebt * 5.0
            if (revisionDebtValue > 50 && revisionDebtValue > alternativeValue) {
                alternativeValue = revisionDebtValue
                divertReason = "Revision-First"
                divertEvidence = listOf(
                    "You're already strong here (${topicPerf.total} attempts, ${(topicPerf.accuracy * 100).toInt()}% accuracy).",
                    "Your existing revision queue currently has higher priority (${profile.revisionDebt} items due)."
                )
                divertAction = "Clear Revision Debt"
                divertRoute = "revision"
            }
            
            // 2. Active Traps
            val trapsValue = profile.activeTraps.size * 10.0
            if (trapsValue > 30 && trapsValue > alternativeValue) {
                alternativeValue = trapsValue
                divertReason = "Repair-First"
                divertEvidence = listOf(
                    "You're already strong here.",
                    "You have unresolved weaknesses (${profile.activeTraps.size} active traps) that are more important right now."
                )
                divertAction = "Repair Weaknesses"
                divertRoute = "mistake_replay"
            }
            
            // 3. Mixed Practice
            if (alternativeValue == 0.0) {
                alternativeValue = 40.0
                divertReason = "Mixed-Practice-First"
                divertEvidence = listOf(
                    "This topic is stable enough that mixed practice may be more valuable."
                )
                divertAction = "Take Paper Twin Mock"
                divertRoute = "papertwin"
            }
            
            // Only divert if alternative is significantly better (threshold: 20 points higher)
            if (alternativeValue > currentTopicValue + 20.0) {
                return@withContext PracticeRecommendationResult.RecommendedDiversion(
                    reason = divertReason,
                    evidence = divertEvidence,
                    recommendedDivertAction = divertAction,
                    divertRoute = divertRoute,
                    currentTopicValue = currentTopicValue,
                    alternativeValue = alternativeValue
                )
            }
        }
        
        PracticeRecommendationResult.Proceed
    }
}
