package com.example.repository

import com.example.database.ConfusionEventEntity
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import androidx.test.core.app.ApplicationProvider
import android.content.Context
import androidx.room.Room
import com.example.database.AppDatabase
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Before
import com.example.model.MCQQuestion
import com.example.model.Option
import com.example.viewmodel.PracticeViewModel

@RunWith(RobolectricTestRunner::class)
class ConfusionEvidenceTest {

    private lateinit var db: AppDatabase
    private lateinit var repo: LocalRepository
    private lateinit var viewModel: PracticeViewModel

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        repo = LocalRepository(
            bookmarkDao = db.bookmarkDao(),
            trapAnalyticsDao = db.trapAnalyticsDao(),
            mistakeReplayDao = db.mistakeReplayDao(),
            appDao = db.appDao(),
            revisionDao = db.revisionDao(),
            questionAttemptDao = db.questionAttemptDao(),
            analyticsDao = db.analyticsDao(),
            confusionEventDao = db.confusionEventDao()
        )
        viewModel = PracticeViewModel(repo)
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun testDistinctQuestionEvidence() = runBlocking {
        val pairId = "el_nino_la_nina"
        
        // Case 4: 1 distinct question -> POSSIBLE
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId, questionId = "10", timestamp = 0L, evidenceLevel = ConfusionEvidenceLevel.POSSIBLE_CONFUSION.name, selectedOptionText = "warming"))
        
        val history1 = repo.getConfusionEventsForPair(pairId)
        val distinct1 = history1.map { it.questionId }.toSet()
        assertEquals(1, distinct1.size)
        // If a new distinct question is attempted
        assertEquals(2, distinct1.size + 1) // -> EMERGING

        // Case 5: 2 distinct questions -> EMERGING
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId, questionId = "11", timestamp = 0L, evidenceLevel = ConfusionEvidenceLevel.EMERGING_CONFUSION.name, selectedOptionText = "warming"))
        
        val history2 = repo.getConfusionEventsForPair(pairId)
        val distinct2 = history2.map { it.questionId }.toSet()
        assertEquals(2, distinct2.size)

        // Case 6: 3 distinct questions -> EMERGING
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId, questionId = "12", timestamp = 0L, evidenceLevel = ConfusionEvidenceLevel.EMERGING_CONFUSION.name, selectedOptionText = "warming"))
        
        val history3 = repo.getConfusionEventsForPair(pairId)
        val distinct3 = history3.map { it.questionId }.toSet()
        assertEquals(3, distinct3.size)

        // Case 7: 4 distinct questions -> CONFIRMED
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId, questionId = "13", timestamp = 0L, evidenceLevel = ConfusionEvidenceLevel.CONFIRMED_CONFUSION.name, selectedOptionText = "warming"))
        
        val history4 = repo.getConfusionEventsForPair(pairId)
        val distinct4 = history4.map { it.questionId }.toSet()
        assertEquals(4, distinct4.size)

        // Case 8: 4 Repeated Questions -> NOT CONFIRMED (Still POSSIBLE)
        // We will simulate user answering Q14 four times in a row
        val pairId2 = "tropopause_stratopause"
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId2, questionId = "14", timestamp = 0L, evidenceLevel = ConfusionEvidenceLevel.POSSIBLE_CONFUSION.name, selectedOptionText = "boundary"))
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId2, questionId = "14", timestamp = 1L, evidenceLevel = ConfusionEvidenceLevel.POSSIBLE_CONFUSION.name, selectedOptionText = "boundary"))
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId2, questionId = "14", timestamp = 2L, evidenceLevel = ConfusionEvidenceLevel.POSSIBLE_CONFUSION.name, selectedOptionText = "boundary"))
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = pairId2, questionId = "14", timestamp = 3L, evidenceLevel = ConfusionEvidenceLevel.POSSIBLE_CONFUSION.name, selectedOptionText = "boundary"))
        
        val historyRepeated = repo.getConfusionEventsForPair(pairId2)
        val distinctRepeated = historyRepeated.map { it.questionId }.toSet()
        assertEquals(1, distinctRepeated.size) // Only 1 distinct question, remains POSSIBLE
    }
}
