package com.example.repository
import com.example.database.ConfusionEventDao

import com.example.database.BookmarkDao
import com.example.database.BookmarkedQuestionEntity
import com.example.database.TrapAnalyticsDao
import com.example.database.TrapAnalyticsEntity
import com.example.model.ExamQuestion
import com.example.model.QuestionFormat
import com.example.model.MCQQuestion
import com.example.model.DescriptiveQuestion
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext

import com.example.model.ExamBlueprint
import com.example.database.AppDao
import com.example.database.Topic
import com.example.database.Question

open class LocalRepository(
    private val bookmarkDao: BookmarkDao,
    private val trapAnalyticsDao: TrapAnalyticsDao,
    private val mistakeReplayDao: com.example.database.MistakeReplayDao,
    private val appDao: AppDao,
    private val revisionDao: com.example.database.RevisionDao,
    private val questionAttemptDao: com.example.database.QuestionAttemptDao,
    private val analyticsDao: com.example.database.AnalyticsDao,
    private val confusionEventDao: com.example.database.ConfusionEventDao
) {
    private val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
    val mistakeReplayEngine = MistakeReplayEngine(mistakeReplayDao, trapAnalyticsDao, confusionEventDao, questionAttemptDao, appDao, revisionDao)
    val learnerModelEngine = LearnerModelEngine(appDao, questionAttemptDao, revisionDao, trapAnalyticsDao, confusionEventDao, analyticsDao, mistakeReplayDao)
    val syllabusEngine = SyllabusEngine(this)
    val timeBasedStudyPlanEngine = TimeBasedStudyPlanEngine(this)
    val paperTwinEngine = PaperTwinEngine(this)
    val examDecisionLabEngine = ExamDecisionLabEngine()
    val falseMasteryEngine = FalseMasteryEngine(this)
    val postTestDebriefEngine = PostTestDebriefEngine()
    val pressureLadderEngine = PressureLadderEngine()
    private val mcqAdapter = moshi.adapter(MCQQuestion::class.java)
    private val descriptiveAdapter = moshi.adapter(DescriptiveQuestion::class.java)



    enum class EvidenceConfidence {
        INSUFFICIENT, EARLY_SIGNAL, EMERGING, CONFIRMED
    }

    data class BlindSpotDetail(
        val topicName: String,
        val simpleCorrect: Int,
        val simpleTotal: Int,
        val complexCorrect: Int,
        val complexTotal: Int,
        val confidence: EvidenceConfidence
    )


    private var _lastGeneratedPaper: GeneratedPaper? = null
    fun getLastGeneratedPaper(): GeneratedPaper? = _lastGeneratedPaper
    
    suspend fun generatePaperTwin(examId: String, targetCount: Int): GeneratedPaper {
        val paper = paperTwinEngine.generatePaperTwin(examId, targetCount)
        _lastGeneratedPaper = paper
        return paper
    }

    suspend fun getFalseMasteryReport(): List<TransferAnalytics> {
        return falseMasteryEngine.evaluateTransfer()
    }

    suspend fun getStudyPlans(): Map<Int, StudyPlan> {
        return timeBasedStudyPlanEngine.generatePlans()
    }

    suspend fun getSyllabusMap(): List<SyllabusTopicNode> {
        return syllabusEngine.getSyllabusMap()
    }

    suspend fun getQuestionsByIds(ids: List<Int>): List<com.example.database.Question> {
        return appDao.getQuestionsByIds(ids)
    }

    suspend fun getLearnerProfile(): com.example.repository.LearnerProfile {
        return learnerModelEngine.getLearnerProfile()
    }

    suspend fun getBlindSpots(): List<BlindSpotDetail> = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getTopicFormatStats()
        val blindSpots = mutableListOf<BlindSpotDetail>()
        
        for (stat in stats) {
            val simpleRate = if (stat.simpleTotal > 0) stat.simpleCorrect.toDouble() / stat.simpleTotal else 0.0
            val complexRate = if (stat.complexTotal > 0) stat.complexCorrect.toDouble() / stat.complexTotal else 0.0
            
            // Meaningful gap: At least 30% difference between simple and complex formats, where simple is strong (>60%)
            val hasGap = simpleRate >= 0.6 && (simpleRate - complexRate) >= 0.3
            
            if (hasGap) {
                val totalSamples = stat.simpleTotal + stat.complexTotal
                
                val confidence = when {
                    totalSamples < 5 -> EvidenceConfidence.INSUFFICIENT
                    totalSamples in 5..9 -> EvidenceConfidence.EARLY_SIGNAL
                    totalSamples in 10..19 -> EvidenceConfidence.EMERGING
                    else -> EvidenceConfidence.CONFIRMED
                }
                
                if (confidence != EvidenceConfidence.INSUFFICIENT) {
                    blindSpots.add(
                        BlindSpotDetail(
                            topicName = stat.topicName,
                            simpleCorrect = stat.simpleCorrect,
                            simpleTotal = stat.simpleTotal,
                            complexCorrect = stat.complexCorrect,
                            complexTotal = stat.complexTotal,
                            confidence = confidence
                        )
                    )
                }
            }
        }
        
        // Sort by confidence (Confirmed first) then by gap size
        blindSpots.sortedByDescending { 
            val gap = (it.simpleCorrect.toDouble()/it.simpleTotal) - (it.complexCorrect.toDouble()/it.complexTotal)
            it.confidence.ordinal * 100 + gap
        }
    }

    data class ConfidenceCalibrationReport(
        val overconfidenceDetected: Boolean,
        val underconfidenceDetected: Boolean,
        val overconfidenceMessage: String,
        val underconfidenceMessage: String
    )

    suspend fun getConfidenceCalibrationReport(): ConfidenceCalibrationReport? = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getConfidenceCalibration()
        if (stats.isEmpty() || stats.sumOf { it.totalAttempts } < 10) return@withContext null // Require sample size
        
        var over = false
        var under = false
        var overMsg = ""
        var underMsg = ""
        
        for (stat in stats) {
            val accuracy = stat.correctAttempts.toDouble() / stat.totalAttempts
            if (stat.selectedConfidence == "Certain" && accuracy < 0.6 && stat.totalAttempts >= 3) {
                over = true
                overMsg = "You're frequently highly confident on questions you later miss (Accuracy: ${(accuracy * 100).toInt()}% when 'Certain')."
            }
            if ((stat.selectedConfidence == "Unsure" || stat.selectedConfidence == "Guessing") && accuracy > 0.7 && stat.totalAttempts >= 3) {
                under = true
                underMsg = "You're often unsure on questions you actually know (Accuracy: ${(accuracy * 100).toInt()}% when '${stat.selectedConfidence}')."
            }
        }
        
        if (!over && !under) return@withContext null
        ConfidenceCalibrationReport(over, under, overMsg, underMsg)
    }

    fun getAllTopics(): Flow<List<Topic>> = appDao.getAllTopics()

    fun getAllBookmarks(): Flow<List<BookmarkedQuestionEntity>> = bookmarkDao.getAllBookmarks()
    
    fun getBookmarksByFormat(format: QuestionFormat): Flow<List<BookmarkedQuestionEntity>> = bookmarkDao.getBookmarksByFormat(format)

    fun isBookmarked(id: String): Flow<Boolean> = bookmarkDao.isBookmarked(id)

    suspend fun getBookmarkById(id: String): BookmarkedQuestionEntity? = withContext(Dispatchers.IO) {
        bookmarkDao.getBookmarkById(id)
    }

    suspend fun addBookmark(question: ExamQuestion) = withContext(Dispatchers.IO) {
        val payload = when (question) {
            is MCQQuestion -> mcqAdapter.toJson(question)
            is DescriptiveQuestion -> descriptiveAdapter.toJson(question)
        }
        
        val entity = BookmarkedQuestionEntity(
            id = question.id,
            format = question.format,
            payloadJson = payload
        )
        bookmarkDao.insertBookmark(entity)
    }

    suspend fun removeBookmark(id: String) = withContext(Dispatchers.IO) {
        bookmarkDao.deleteBookmark(id)
    }

    fun getAllTraps(): Flow<List<TrapAnalyticsEntity>> = trapAnalyticsDao.getAllTraps()
    
    suspend fun getTrap(trapType: String): TrapAnalyticsEntity? = withContext(Dispatchers.IO) {
        trapAnalyticsDao.getTrap(trapType)
    }

    suspend fun insertTrap(trap: TrapAnalyticsEntity) = withContext(Dispatchers.IO) {
        trapAnalyticsDao.insertTrap(trap)
    }

    suspend fun incrementTrap(trapType: String, questionText: String, dissectionText: String) = withContext(Dispatchers.IO) {
        val existing = trapAnalyticsDao.getTrap(trapType)
        
        val newQuestionObj = org.json.JSONObject().apply {
            put("questionText", questionText)
            put("dissection", dissectionText)
            put("timestamp", System.currentTimeMillis())
        }

        if (existing != null) {
            val arr = try {
                org.json.JSONArray(existing.failedQuestionsJson)
            } catch (e: Exception) {
                org.json.JSONArray()
            }
            arr.put(newQuestionObj)
            
            val updated = existing.copy(
                frequency = existing.frequency + 1,
                failedQuestionsJson = arr.toString()
            )
            trapAnalyticsDao.insertTrap(updated)
        } else {
            val arr = org.json.JSONArray().put(newQuestionObj)
            trapAnalyticsDao.insertTrap(
                TrapAnalyticsEntity(
                    trapType = trapType,
                    frequency = 1,
                    failedQuestionsJson = arr.toString()
                )
            )
        }
    }

    suspend fun getQuestionCountForProfile(topicName: String, profile: ExamBlueprint): Int = withContext(Dispatchers.IO) {
        val allowElite = profile.allowedTiers.contains("Elite")
        appDao.getQuestionCountForTopicAndProfile(topicName, profile.allowedTiers, allowElite)
    }

    suspend fun getQuestionsForProfile(topicName: String, profile: ExamBlueprint, limit: Int): List<Question> = withContext(Dispatchers.IO) {
        val allowElite = profile.allowedTiers.contains("Elite")
        if (topicName == "Global") {
            appDao.getAllQuestionsForProfile(profile.allowedTiers, allowElite, limit)
        } else {
            appDao.getQuestionsForProfile(topicName, profile.allowedTiers, allowElite, limit)
        }
    }

    suspend fun getQuestionsForProfileWithFormat(topicName: String, profile: ExamBlueprint, format: String, limit: Int): List<Question> = withContext(Dispatchers.IO) {
        val allowElite = profile.allowedTiers.contains("Elite")
        val results = appDao.getQuestionsForProfileWithFormat(topicName, profile.allowedTiers, format, allowElite, limit)
        if (results.isEmpty()) {
            appDao.getQuestionsForProfile(topicName, profile.allowedTiers, allowElite, limit)
        } else {
            results
        }
    }

    open suspend fun getFewShotExamples(topicName: String, tier: String, format: String, limit: Int = 3): List<Question> = withContext(Dispatchers.IO) {
        appDao.getFewShotExamples(topicName, tier, format, limit)
    }

    suspend fun getQuestionsByTrapType(trapType: String, limit: Int): List<Question> = withContext(Dispatchers.IO) {
        appDao.getQuestionsByTrapType(trapType, limit)
    }


    suspend fun getRevisionItem(questionId: String): com.example.database.RevisionItemEntity? = withContext(Dispatchers.IO) {
        revisionDao.getRevisionItem(questionId)
    }

    suspend fun logQuestionAttempt(
        questionId: String,
        outcome: com.example.model.AttemptOutcome,
        confidence: String?,
        timeSpentSeconds: Int,
        trapFallenInto: String?
    ) {
        val attempt = com.example.database.QuestionAttemptEntity(
            questionId = questionId,
            timestamp = System.currentTimeMillis(),
            outcome = outcome.name,
            confidence = confidence,
            timeSpentSeconds = timeSpentSeconds,
            trapFallenInto = trapFallenInto
        )
        questionAttemptDao.insertAttempt(attempt)
    }

    suspend fun logRevisionAttempt(questionId: String, outcome: com.example.model.AttemptOutcome, associatedTrap: String?) = withContext(Dispatchers.IO) {
        if (outcome == com.example.model.AttemptOutcome.ABSTAINED || outcome == com.example.model.AttemptOutcome.UNANSWERED) return@withContext
        val isCorrect = outcome == com.example.model.AttemptOutcome.CORRECT
        val existing = revisionDao.getRevisionItem(questionId)
        val now = System.currentTimeMillis()
        if (existing == null) {
            val newState = if (isCorrect) "IMPROVING" else "NEW"
            val interval = if (isCorrect) 3 * 24 * 3600 * 1000L else 12 * 3600 * 1000L
            val priority = if (isCorrect) 3 else 1
            revisionDao.insertOrUpdate(
                com.example.database.RevisionItemEntity(
                    questionId = questionId,
                    firstAttemptTime = now,
                    lastAttemptTime = now,
                    attemptCount = 1,
                    correctCount = if (isCorrect) 1 else 0,
                    incorrectCount = if (isCorrect) 0 else 1,
                    masteryState = newState,
                    nextRevisionDate = now + interval,
                    priority = priority,
                    associatedTrap = associatedTrap
                )
            )
        } else {
            val correctCount = existing.correctCount + if (isCorrect) 1 else 0
            val incorrectCount = existing.incorrectCount + if (isCorrect) 0 else 1
            var newState = existing.masteryState
            var interval = 0L
            var priority = existing.priority

            if (isCorrect) {
                when (existing.masteryState) {
                    "NEW", "DUE" -> { newState = "IMPROVING"; interval = 3 * 24 * 3600 * 1000L; priority = 3 }
                    "IMPROVING" -> { newState = "STRONG"; interval = 10 * 24 * 3600 * 1000L; priority = 4 }
                    "STRONG", "MASTERED" -> { newState = "MASTERED"; interval = 30 * 24 * 3600 * 1000L; priority = 5 }
                }
            } else {
                newState = "DUE"
                interval = 6 * 3600 * 1000L
                priority = 1
            }

            revisionDao.insertOrUpdate(
                existing.copy(
                    lastAttemptTime = now,
                    attemptCount = existing.attemptCount + 1,
                    correctCount = correctCount,
                    incorrectCount = incorrectCount,
                    masteryState = newState,
                    nextRevisionDate = now + interval,
                    priority = priority,
                    associatedTrap = associatedTrap ?: existing.associatedTrap
                )
            )
        }
    }
    
    fun getDueItemsCountFlow(): Flow<Int> = revisionDao.getDueItemsCount(System.currentTimeMillis())
    suspend fun getDueItemsCountSync(): Int = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        return@withContext revisionDao.getDueItemsCountSync(System.currentTimeMillis())
    }

    suspend fun getAllTrapsList(): List<com.example.database.TrapAnalyticsEntity> = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        return@withContext trapAnalyticsDao.getAllTrapsSync()
    }
    
    suspend fun getAllAnalytics(): List<com.example.database.TrapAnalyticsEntity> = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        return@withContext trapAnalyticsDao.getAllTrapsSync()
    }
    
    suspend fun getRevisionDueQuestions(limit: Int): List<Question> = withContext(Dispatchers.IO) {
        val items = revisionDao.getDueItems(System.currentTimeMillis(), limit)
        val qIds = items.map { it.questionId.toIntOrNull() ?: -1 }.filter { it != -1 }
        appDao.getQuestionsByIds(qIds)
    }

            suspend fun getRecentFamilyAttempts(timeWindowMs: Long): List<com.example.database.FamilyAttemptRecord> = withContext(Dispatchers.IO) {
        val since = System.currentTimeMillis() - timeWindowMs
        questionAttemptDao.getRecentFamilyAttempts(since)
    }


    suspend fun logConfusionEvent(
        pairId: String,
        questionId: String,
        selectedOptionText: String,
        evidenceLevel: com.example.repository.ConfusionEvidenceLevel
    ) {
        withContext(Dispatchers.IO) {
            val event = com.example.database.ConfusionEventEntity(
                pairId = pairId,
                questionId = questionId,
                selectedOptionText = selectedOptionText,
                timestamp = System.currentTimeMillis(),
                evidenceLevel = evidenceLevel.name
            )
            confusionEventDao.insertEvent(event)
        }
    }

    suspend fun getConfusionEventsForPair(pairId: String): List<com.example.database.ConfusionEventEntity> {
        return withContext(Dispatchers.IO) {
            confusionEventDao.getEventsForPair(pairId)
        }
    }

    // Mistake Replay
    suspend fun insertMistakeReplayOutcome(outcome: com.example.database.ReplayOutcomeEntity) {
        mistakeReplayDao.insertOutcome(outcome)
    }

    suspend fun getAllMistakeReplayOutcomes(): List<com.example.database.ReplayOutcomeEntity> {
        return mistakeReplayDao.getAllOutcomes()
    }

    suspend fun getMistakeReplayOutcomesForQuestion(questionId: String): List<com.example.database.ReplayOutcomeEntity> {
        return mistakeReplayDao.getOutcomesForQuestion(questionId)
    }

    suspend fun getQuestionsByTopicAndTier(topicName: String, tier: String, limit: Int): List<com.example.database.Question> = withContext(kotlinx.coroutines.Dispatchers.IO) {
        appDao.getQuestionsByTopicAndTier(topicName, tier, limit)
    }
}
