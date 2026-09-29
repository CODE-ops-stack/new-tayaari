package com.example.viewmodel

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.AppDatabase
import com.example.database.ConfusionEventEntity
import com.example.database.Topic
import com.example.database.QuestionAttemptEntity
import com.example.database.TrapAnalyticsEntity
import com.example.database.Question
import com.example.repository.LocalRepository
import com.example.repository.MistakeReplayEngine
import com.example.repository.QuestionSelectionEngine
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import android.content.Context

@RunWith(RobolectricTestRunner::class)
class MistakeReplayTest {

    private lateinit var db: AppDatabase
    private lateinit var repo: LocalRepository
    private lateinit var replayEngine: MistakeReplayEngine
    private lateinit var viewModel: MistakeReplayViewModel

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
        replayEngine = MistakeReplayEngine(
            db.mistakeReplayDao(),
            db.trapAnalyticsDao(),
            db.confusionEventDao(),
            db.questionAttemptDao(),
            db.appDao(),
            db.revisionDao()
        )
        val selectionEngine = QuestionSelectionEngine(repo)
        viewModel = MistakeReplayViewModel(repo)
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun testReplaySelection_PrioritizesMeaningfulMistakes() = runBlocking {
        // Create some questions
        db.appDao().insertTopics(listOf(Topic(id = 1, name = "1", source = "Mock")))
        db.appDao().insertQuestions(listOf(
            Question(id = 1, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Q1", options = "[]", correctAnswer = "A", explanation = ""),
            Question(id = 2, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Q2", options = "[]", correctAnswer = "B", explanation = "")
        ))

        // 1. A repeated incorrect (priority 80)
        db.questionAttemptDao().insertAttempt(QuestionAttemptEntity(questionId = "1", timestamp = 1L, outcome = "INCORRECT", confidence = "Likely", timeSpentSeconds = 10, trapFallenInto = null))
        db.questionAttemptDao().insertAttempt(QuestionAttemptEntity(questionId = "1", timestamp = 2L, outcome = "INCORRECT", confidence = "Likely", timeSpentSeconds = 10, trapFallenInto = null))

        // 2. A confirmed confusion (priority 100)
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = "el_nino", questionId = "2", selectedOptionText = "warming", timestamp = 3L, evidenceLevel = "CONFIRMED_CONFUSION"))

        val candidate = replayEngine.getHighestPriorityCandidate()
        assertNotNull(candidate)
        assertEquals("CONFUSION", candidate?.evidenceType)
        assertEquals(2, candidate?.originalQuestion?.id)
    }

    @Test
    fun testAlternateSelection_DoesNotDuplicateOriginal() = runBlocking {
        db.appDao().insertTopics(listOf(Topic(id = 1, name = "1", source = "Mock")))
        db.appDao().insertQuestions(listOf(
            Question(id = 1, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Original", options = "[]", correctAnswer = "A", explanation = "", familyId = "F1"),
            Question(id = 2, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Alternate", options = "[]", correctAnswer = "B", explanation = "", familyId = "F1")
        ))
        
        db.questionAttemptDao().insertAttempt(QuestionAttemptEntity(questionId = "1", timestamp = 1L, outcome = "INCORRECT", confidence = "Likely", timeSpentSeconds = 10, trapFallenInto = null))
        db.questionAttemptDao().insertAttempt(QuestionAttemptEntity(questionId = "1", timestamp = 2L, outcome = "INCORRECT", confidence = "Likely", timeSpentSeconds = 10, trapFallenInto = null))

        viewModel.loadCandidateSync()
        assertEquals(ReplayState.REVIEW_MISTAKE, viewModel.uiState.value.currentState)
        assertEquals(1, viewModel.uiState.value.candidate?.originalQuestion?.id)

        viewModel.commitToRepair()
        assertEquals(ReplayState.REPAIR, viewModel.uiState.value.currentState)

        viewModel.proceedToAlternateSync()
        assertEquals(ReplayState.ALTERNATE_QUESTION, viewModel.uiState.value.currentState)
        val alt = viewModel.uiState.value.alternateQuestion
        assertNotNull(alt)
        assertNotEquals(1, alt?.id)
        assertEquals(2, alt?.id)
    }

    @Test
    fun testOutcome_UpdatesLearnerState() = runBlocking {
        db.appDao().insertTopics(listOf(Topic(id = 1, name = "1", source = "Mock")))
        db.appDao().insertQuestions(listOf(
            Question(id = 1, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Q1", options = "[]", correctAnswer = "A", explanation = ""),
            Question(id = 2, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Q2", options = "[]", correctAnswer = "B", explanation = "")
        ))
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = "el_nino", questionId = "1", selectedOptionText = "warming", timestamp = 3L, evidenceLevel = "CONFIRMED_CONFUSION"))

        viewModel.loadCandidateSync()
        viewModel.commitToRepair()
        viewModel.proceedToAlternateSync() // Sets alternate to Q2
        viewModel.submitAlternateAnswerSync(isCorrect = true)

        assertEquals(ReplayState.RESULT, viewModel.uiState.value.currentState)
        assertEquals("IMPROVED", viewModel.uiState.value.outcomeState)

        val outcomes = repo.getAllMistakeReplayOutcomes()
        assertEquals(1, outcomes.size)
        assertEquals("1", outcomes[0].originalQuestionId)
        assertEquals("IMPROVED", outcomes[0].outcomeState)
    

    @Test
    fun testScoring_DoesNotCorruptOfficialExamScore() = runBlocking {
        // Attempting an alternate question during replay shouldn't log a normal attempt that pollutes exam scoring
        db.appDao().insertTopics(listOf(Topic(id = 1, name = "1", source = "Mock")))
        db.appDao().insertQuestions(listOf(
            Question(id = 1, topicId = 1, tier = "Tier 1", format = "Direct Fact", examRelevance = "All", source = "Mock", specificExam = "", questionText = "Q1", options = "[]", correctAnswer = "A", explanation = "")
        ))
        db.confusionEventDao().insertEvent(ConfusionEventEntity(pairId = "el_nino", questionId = "1", selectedOptionText = "warming", timestamp = 3L, evidenceLevel = "CONFIRMED_CONFUSION"))

        val initialAttempts = db.questionAttemptDao().getAllAttempts().size
        
        viewModel.loadCandidateSync()
        viewModel.proceedToAlternateSync()
        viewModel.submitAlternateAnswerSync(isCorrect = true)

        val finalAttempts = db.questionAttemptDao().getAllAttempts().size
        assertEquals("Replay should not log normal question attempts", initialAttempts, finalAttempts)
        
        val outcomes = repo.getAllMistakeReplayOutcomes()
        assertEquals(1, outcomes.size)
    }
}
}
