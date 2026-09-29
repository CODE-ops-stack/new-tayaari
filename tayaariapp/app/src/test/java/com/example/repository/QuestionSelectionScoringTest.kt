package com.example.repository

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.database.QuestionAttemptEntity
import com.example.model.DnaTheme
import com.example.model.ExamBlueprint
import com.example.model.MCQQuestion
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.math.BigDecimal

@RunWith(RobolectricTestRunner::class)
class QuestionSelectionScoringTest {

    private lateinit var db: AppDatabase
    private lateinit var engine: QuestionSelectionEngine
    private lateinit var repo: LocalRepository

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
        engine = QuestionSelectionEngine(repo)
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun testExactRepetitionPenaltyIsStrongerThanFamilyRepetition() = runBlocking {
        db.appDao().insertQuestions(listOf(
            createFamilyQuestion(1, "F1", "FOUNDATION"),
            createFamilyQuestion(2, "F1", "FOUNDATION"),
            createFamilyQuestion(3, "F1", "REINFORCEMENT")
        ))
        
        db.questionAttemptDao().insertAttempt(
            QuestionAttemptEntity(
                questionId = "1",
                timestamp = System.currentTimeMillis(),
                outcome = "INCORRECT",
                confidence = null,
                timeSpentSeconds = 10,
                trapFallenInto = null
            )
        )
        
        val blueprint = ExamBlueprint(examId = "TEST", version = "1.0", displayName = "Test", allowedTiers = listOf("Tier 1"), examDna = emptyList())
        val selected = engine.getQuestionsForProfile("Global", blueprint, 3, "Smart Practice")
        
        assertEquals(3, selected.size)
        assertEquals("3", selected[0].id) // +20 progression bonus -> highest score
        assertEquals("2", selected[1].id) // -5 recent family -> middle score
        assertEquals("1", selected[2].id) // -10 exact + -5 recent -> lowest score
    }
    
    private fun createFamilyQuestion(id: Int, familyId: String, familyStage: String): Question {
        return Question(
            id = id,
            topicId = 1,
            tier = "Tier 1",
            format = "Statement-based",
            examRelevance = "High",
            source = "Test",
            specificExam = "UPSC",
            questionText = "Q$id",
            options = "[{\"id\":\"A\",\"text\":\"A\"},{\"id\":\"B\",\"text\":\"B\"}]",
            correctAnswer = "A",
            explanation = "Exp",
            familyId = familyId,
            familyStage = familyStage
        )
    }
}
