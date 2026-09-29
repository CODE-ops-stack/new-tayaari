package com.example.repository

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.*
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class StopDoingEngineTest {

    private lateinit var db: AppDatabase
    private lateinit var repo: LocalRepository
    private lateinit var engine: StopDoingEngine

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).allowMainThreadQueries().build()
        repo = LocalRepository(
            db.bookmarkDao(),
            db.trapAnalyticsDao(),
            db.mistakeReplayDao(),
            db.appDao(),
            db.revisionDao(),
            db.questionAttemptDao(),
            db.analyticsDao(),
            db.confusionEventDao()
        )
        
        runBlocking {
            db.appDao().insertTopics(listOf(Topic(1, "Test Topic", "Subject")))
            db.appDao().insertQuestions(listOf(
                Question(
                    id = 1, topicId = 1, tier = "Medium", format = "Direct Fact", examRelevance = "Core",
                    source = "PYQ", specificExam = "Test", questionText = "Q",
                    options = "[]", correctAnswer = "A", explanation = "Exp", distractorDissections = "[]"
                )
            ))
        }
        
        engine = StopDoingEngine(repo.learnerModelEngine, repo.falseMasteryEngine)
    }

    @After
    fun tearDown() {
        db.close()
    }

    private fun simulateAttempts(attempts: Int, correctCount: Int) {
        runBlocking {
            val attemptEntities = mutableListOf<QuestionAttemptEntity>()
            for (i in 1..attempts) {
                val outcome = if (i <= correctCount) "CORRECT" else "INCORRECT"
                attemptEntities.add(
                    QuestionAttemptEntity(
                        questionId = "1",
                        timestamp = System.currentTimeMillis(),
                        outcome = outcome,
                        confidence = "Sure",
                        timeSpentSeconds = 30,
                        trapFallenInto = null
                    )
                )
            }
            attemptEntities.forEach { db.questionAttemptDao().insertAttempt(it) }
        }
    }

    @Test
    fun testInsufficientEvidence_Proceeds() = runBlocking {
        simulateAttempts(10, 9)
        val result = engine.evaluatePracticeIntent("Test Topic")
        assertTrue(result is PracticeRecommendationResult.Proceed)
    }

    @Test
    fun testModerateEvidence_Proceeds() = runBlocking {
        simulateAttempts(100, 60)
        val result = engine.evaluatePracticeIntent("Test Topic")
        assertTrue(result is PracticeRecommendationResult.Proceed)
    }

    @Test
    fun testStrongTopicWithRevisionDebt_Diverts() = runBlocking {
        simulateAttempts(100, 90)
        
        for(i in 1..30) {
            db.revisionDao().insertOrUpdate(
                RevisionItemEntity(
                    questionId = i.toString(),
                    firstAttemptTime = 0, lastAttemptTime = 0,
                    attemptCount = 1, correctCount = 0, incorrectCount = 1,
                    masteryState = "DUE", nextRevisionDate = System.currentTimeMillis() - 1000,
                    priority = 1
                )
            )
        }
        
        val result = engine.evaluatePracticeIntent("Test Topic")
        assertTrue(result is PracticeRecommendationResult.RecommendedDiversion)
        assertEquals("Revision-First", (result as PracticeRecommendationResult.RecommendedDiversion).reason)
    }
}
