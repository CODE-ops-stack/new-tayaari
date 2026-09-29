package com.example.repository

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.AppDatabase
import com.example.database.ConfusionEventEntity
import com.example.database.ReplayOutcomeEntity
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class LearnerModelReplayIntegrationTest {

    private lateinit var db: AppDatabase
    private lateinit var engine: LearnerModelEngine

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        engine = LearnerModelEngine(
            db.appDao(),
            db.questionAttemptDao(),
            db.revisionDao(),
            db.trapAnalyticsDao(),
            db.confusionEventDao(),
            db.analyticsDao(),
            db.mistakeReplayDao()
        )
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun testLearnerModelConsumesReplayOutcomes() = runBlocking {
        // Simulate an active confusion
        db.confusionEventDao().insertEvent(
            ConfusionEventEntity(
                pairId = "A_B", questionId = "101",
                selectedOptionText = "A", timestamp = 1L, evidenceLevel = "CONFIRMED_CONFUSION"
            )
        )

        // Verify initial state
        var profile = engine.getLearnerProfile()
        assertEquals(0, profile.repairedMistakesCount)
        assertEquals(1, profile.activeConfusions.size)

        // Simulate an IMPROVED replay outcome for that question
        db.mistakeReplayDao().insertOutcome(
            ReplayOutcomeEntity(
                originalQuestionId = "101", transferQuestionId = "102",
                replayTimestamp = 2L, initialEvidenceType = "CONFUSION", outcomeState = "IMPROVED"
            )
        )

        // Verify repaired mistakes count is populated and confusion is cleared
        profile = engine.getLearnerProfile()
        assertEquals(1, profile.repairedMistakesCount)
        assertTrue(profile.activeConfusions.isEmpty())
    }
}
