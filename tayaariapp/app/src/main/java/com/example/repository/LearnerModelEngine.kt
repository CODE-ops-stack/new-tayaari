package com.example.repository

import com.example.database.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class LearnerProfile(
    val totalQuestionsAttempted: Int,
    val totalCorrect: Int,
    val totalIncorrect: Int,
    val totalAbstained: Int,
    val totalUnanswered: Int,
    val overallAccuracy: Double,
    
    val topicPerformances: Map<Int, TopicPerformance>,
    val weakTopics: List<TopicPerformance>,
    val strongTopics: List<TopicPerformance>,
    
    val blindSpots: List<LocalRepository.BlindSpotDetail>,
    
    val activeTraps: List<TrapAnalyticsEntity>,
    val activeConfusions: List<ConfusionEventEntity>,
    
    val revisionDebt: Int,
    val masteryDistribution: Map<String, Int>,
    
    val confidenceCalibration: Map<String, Double>,
    
    val repairedMistakesCount: Int = 0
)

data class TopicPerformance(
    val topicId: Int,
    val topicName: String,
    val correct: Int,
    val total: Int,
    val accuracy: Double
)

class LearnerModelEngine(
    private val appDao: AppDao,
    private val questionAttemptDao: QuestionAttemptDao,
    private val revisionDao: RevisionDao,
    private val trapAnalyticsDao: TrapAnalyticsDao,
    private val confusionEventDao: ConfusionEventDao,
    private val analyticsDao: AnalyticsDao,
    private val mistakeReplayDao: MistakeReplayDao
) {
    suspend fun getLearnerProfile(): LearnerProfile = withContext(Dispatchers.IO) {
        val attempts = questionAttemptDao.getAllAttempts()
        val replays = mistakeReplayDao.getAllOutcomes()
        
        var correct = 0
        var incorrect = 0
        var abstained = 0
        var unanswered = 0
        
        attempts.forEach { 
            when(it.outcome) {
                "CORRECT" -> correct++
                "INCORRECT" -> incorrect++
                "ABSTAINED" -> abstained++
                "UNANSWERED" -> unanswered++
            }
        }
        
        val totalAttempts = correct + incorrect
        val accuracy = if (totalAttempts > 0) correct.toDouble() / totalAttempts else 0.0
        
        // topics
        val topics = appDao.getAllTopicsUnwrapped()
        val topicPerf = mutableMapOf<Int, TopicPerformance>()
        topics.forEach { t -> topicPerf[t.id] = TopicPerformance(t.id, t.name, 0, 0, 0.0) }
        
        val qIds = attempts.map { it.questionId.toInt() }.distinct()
        val questions = if(qIds.isNotEmpty()) appDao.getQuestionsByIds(qIds) else emptyList()
        val qToTopic = questions.associate { it.id to it.topicId }
        
        attempts.forEach { att ->
            val tId = qToTopic[att.questionId.toInt()]
            if (tId != null && (att.outcome == "CORRECT" || att.outcome == "INCORRECT")) {
                val curr = topicPerf[tId]!!
                val nCorrect = curr.correct + if (att.outcome == "CORRECT") 1 else 0
                val nTotal = curr.total + 1
                topicPerf[tId] = curr.copy(correct = nCorrect, total = nTotal, accuracy = nCorrect.toDouble()/nTotal)
            }
        }
        
        val activeTopics = topicPerf.values.filter { it.total > 0 }.sortedByDescending { it.accuracy }
        val strongTopics = activeTopics.take(3).filter { it.accuracy >= 0.7 }
        val weakTopics = activeTopics.takeLast(3).filter { it.accuracy < 0.5 }.reversed()
        
        // blind spots
        val stats = analyticsDao.getTopicFormatStats()
        val blindSpots = mutableListOf<LocalRepository.BlindSpotDetail>()
        for (stat in stats) {
            val simpleRate = if (stat.simpleTotal > 0) stat.simpleCorrect.toDouble() / stat.simpleTotal else 0.0
            val complexRate = if (stat.complexTotal > 0) stat.complexCorrect.toDouble() / stat.complexTotal else 0.0
            val gap = simpleRate - complexRate
            
            if (stat.simpleTotal >= 3 && stat.complexTotal >= 3 && simpleRate > 0.6 && gap >= 0.3) {
                val conf = if (gap > 0.5) LocalRepository.EvidenceConfidence.CONFIRMED 
                          else if (stat.complexTotal >= 5) LocalRepository.EvidenceConfidence.EMERGING 
                          else LocalRepository.EvidenceConfidence.EARLY_SIGNAL
                blindSpots.add(LocalRepository.BlindSpotDetail(
                    stat.topicName, stat.simpleCorrect, stat.simpleTotal, stat.complexCorrect, stat.complexTotal, conf
                ))
            }
        }
        
        val improvedQuestionIds = replays.filter { it.outcomeState == "IMPROVED" }.map { it.originalQuestionId }.toSet()
        val repairedCount = improvedQuestionIds.size
        
        val traps = trapAnalyticsDao.getAllTrapsSync().filter { it.frequency > 0 }
        val confEvents = confusionEventDao.getAllEventsSync().filter { 
            (it.evidenceLevel == "EMERGING_CONFUSION" || it.evidenceLevel == "CONFIRMED_CONFUSION") && 
            !improvedQuestionIds.contains(it.questionId) 
        }
        
        val revDue = revisionDao.getDueItems(System.currentTimeMillis(), 1000).size
        val allRevs = revisionDao.getAllRevisionItems()
        val masteryCounts = allRevs.groupBy { it.masteryState }.mapValues { it.value.size }
        
        val calibStats = analyticsDao.getConfidenceCalibration()
        val calibMap = calibStats.associate { it.selectedConfidence to (if(it.totalAttempts > 0) it.correctAttempts.toDouble()/it.totalAttempts else 0.0) }
        
        LearnerProfile(
            totalQuestionsAttempted = attempts.size,
            totalCorrect = correct,
            totalIncorrect = incorrect,
            totalAbstained = abstained,
            totalUnanswered = unanswered,
            overallAccuracy = accuracy,
            topicPerformances = topicPerf,
            weakTopics = weakTopics,
            strongTopics = strongTopics,
            blindSpots = blindSpots,
            activeTraps = traps,
            activeConfusions = confEvents,
            revisionDebt = revDue,
            masteryDistribution = masteryCounts,
            confidenceCalibration = calibMap,
            repairedMistakesCount = repairedCount
        )
    }
}
