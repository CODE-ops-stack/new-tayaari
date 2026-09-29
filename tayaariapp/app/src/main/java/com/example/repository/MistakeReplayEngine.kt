package com.example.repository

import com.example.database.MistakeReplayDao
import com.example.database.TrapAnalyticsDao
import com.example.database.ConfusionEventDao
import com.example.database.QuestionAttemptDao
import com.example.database.AppDao
import com.example.database.RevisionDao
import com.example.database.RevisionItemEntity
import com.example.database.ReplayOutcomeEntity
import com.example.database.Question
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class ReplayCandidate(
    val originalQuestion: Question,
    val evidenceType: String,
    val context: String, // E.g., trap name, confusion pair
    val priority: Int,
    val repairRoute: String
)

class MistakeReplayEngine(
    private val mistakeReplayDao: MistakeReplayDao,
    private val trapAnalyticsDao: TrapAnalyticsDao,
    private val confusionEventDao: ConfusionEventDao,
    private val questionAttemptDao: QuestionAttemptDao,
    private val appDao: AppDao,
    private val revisionDao: RevisionDao
) {
    suspend fun getHighestPriorityCandidate(): ReplayCandidate? = withContext(Dispatchers.IO) {
        val attempts = questionAttemptDao.getAllAttempts()
        val confusions = confusionEventDao.getAllEventsSync()
        
        var bestCandidate: ReplayCandidate? = null
        
        // Helper to check if we should replay
        suspend fun shouldReplay(qId: String): Boolean {
            val outcomes = mistakeReplayDao.getOutcomesForQuestion(qId)
            return outcomes.isEmpty() || outcomes.last().outcomeState == "STILL_STRUGGLING" || outcomes.last().outcomeState == "PARTIALLY_IMPROVED"
        }
        
        // 1. Recurring confusion
        val emergingOrConfirmed = confusions.filter { it.evidenceLevel == "EMERGING_CONFUSION" || it.evidenceLevel == "CONFIRMED_CONFUSION" }
        for (conf in emergingOrConfirmed) {
            if (shouldReplay(conf.questionId)) {
                val questions = appDao.getQuestionsByIds(listOf(conf.questionId.toInt()))
                if (questions.isNotEmpty()) {
                    return@withContext ReplayCandidate(questions.first(), "CONFUSION", conf.pairId, 100, "Contrast Lab")
                }
            }
        }

        // 2. Verified trap
        val traps = trapAnalyticsDao.getAllTrapsSync()
        val verifiedTrapTypes = traps.filter { it.frequency > 0 }.map { it.trapType }.toSet()
        val trapAttempts = attempts.filter { it.trapFallenInto != null && verifiedTrapTypes.contains(it.trapFallenInto) && it.outcome == "INCORRECT" }
        for (attempt in trapAttempts) {
            if (shouldReplay(attempt.questionId)) {
                val questions = appDao.getQuestionsByIds(listOf(attempt.questionId.toInt()))
                if (questions.isNotEmpty()) {
                    return@withContext ReplayCandidate(questions.first(), "TRAP", attempt.trapFallenInto!!, 90, "Trap Training")
                }
            }
        }

        // 3. Repeated incorrect answer
        val attemptGroups = attempts.filter { it.outcome == "INCORRECT" }.groupBy { it.questionId }
        for ((qId, fails) in attemptGroups) {
            if (fails.size > 1 && shouldReplay(qId)) {
                val questions = appDao.getQuestionsByIds(listOf(qId.toInt()))
                if (questions.isNotEmpty()) {
                    val candidate = ReplayCandidate(questions.first(), "REPEATED_INCORRECT", "Failed ${fails.size} times", 80, "Concept Repair")
                    if (bestCandidate == null || bestCandidate.priority < candidate.priority) bestCandidate = candidate
                }
            }
        }
        
        if (bestCandidate != null) return@withContext bestCandidate

        // 4. High-confidence wrong
        val highConfFails = attempts.filter { it.outcome == "INCORRECT" && (it.confidence == "Sure" || it.confidence == "Highly Likely") }
        for (attempt in highConfFails) {
            if (shouldReplay(attempt.questionId)) {
                val questions = appDao.getQuestionsByIds(listOf(attempt.questionId.toInt()))
                if (questions.isNotEmpty()) {
                    return@withContext ReplayCandidate(questions.first(), "HIGH_CONFIDENCE_WRONG", "Confidence: ${attempt.confidence}", 70, "Confidence Calibration")
                }
            }
        }
        
        return@withContext null
    }

    suspend fun findAlternateQuestion(original: Question): Question? = withContext(Dispatchers.IO) {
        val stageProgression = listOf("FOUNDATION", "REINFORCEMENT", "STANDARD", "APPLICATION", "TRANSFER", "EXAM_STYLE")
        
        if (original.familyId != null) {
            val familyQuestions = appDao.getQuestionsByFamilyId(original.familyId).filter { it.id != original.id }
            if (familyQuestions.isNotEmpty()) {
                val currentStageIdx = stageProgression.indexOf(original.familyStage?.uppercase())
                if (currentStageIdx != -1) {
                    val furtherStages = familyQuestions.filter { 
                        stageProgression.indexOf(it.familyStage?.uppercase()) > currentStageIdx
                    }.sortedBy { stageProgression.indexOf(it.familyStage?.uppercase()) }
                    if (furtherStages.isNotEmpty()) return@withContext furtherStages.first()
                }
                return@withContext familyQuestions.first()
            }
        }
        
        val topicQuestions = appDao.getQuestionsByTopic(original.topicId, 50).filter { it.id != original.id }
        return@withContext topicQuestions.randomOrNull()
    }
    
    suspend fun onReplayCompleted(candidate: ReplayCandidate, alternateQuestion: Question?, isAlternateCorrect: Boolean): String = withContext(Dispatchers.IO) {
        val outcome = if (isAlternateCorrect) "IMPROVED" else "STILL_STRUGGLING"
        val entity = ReplayOutcomeEntity(
            originalQuestionId = candidate.originalQuestion.id.toString(),
            transferQuestionId = alternateQuestion?.id?.toString(),
            replayTimestamp = System.currentTimeMillis(),
            initialEvidenceType = candidate.evidenceType,
            outcomeState = outcome
        )
        mistakeReplayDao.insertOutcome(entity)
        
        val existingRev = revisionDao.getRevisionItem(candidate.originalQuestion.id.toString())
        val newNextReview = if (outcome == "IMPROVED") {
            System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000
        } else if (outcome == "PARTIALLY_IMPROVED") {
            System.currentTimeMillis() + 3L * 24 * 60 * 60 * 1000
        } else {
            System.currentTimeMillis() + 1L * 24 * 60 * 60 * 1000
        }
        val newState = if (outcome == "IMPROVED") "IMPROVING" else if (outcome == "PARTIALLY_IMPROVED") "IMPROVING" else "DUE"
        
        if (existingRev != null) {
            revisionDao.insertOrUpdate(existingRev.copy(nextRevisionDate = newNextReview, masteryState = newState, priority = if (outcome == "STILL_STRUGGLING") 1 else 3))
        } else {
            if (outcome == "STILL_STRUGGLING") {
                revisionDao.insertOrUpdate(RevisionItemEntity(
                    questionId = candidate.originalQuestion.id.toString(),
                    firstAttemptTime = System.currentTimeMillis(),
                    lastAttemptTime = System.currentTimeMillis(),
                    attemptCount = 1,
                    correctCount = 0,
                    incorrectCount = 1,
                    masteryState = "NEW",
                    nextRevisionDate = newNextReview,
                    priority = 1,
                    associatedTrap = null
                ))
            }
        }
        return@withContext outcome
    }
    
    fun getNextBestAction(outcome: String): String {
        return when (outcome) {
            "STILL_STRUGGLING" -> "Revise Prerequisite Concepts\nWhy: You are still missing the foundation.\nWhat this improves: Closes fundamental gaps."
            "PARTIALLY_IMPROVED" -> "Practice Sibling Questions\nWhy: You need more reps to solidify this.\nWhat this improves: Consistency and recall."
            "IMPROVED" -> "Return to Smart Practice\nWhy: You successfully transferred the concept.\nWhat this improves: Breadth of knowledge."
            else -> "Return to Smart Practice"
        }
    }
}
