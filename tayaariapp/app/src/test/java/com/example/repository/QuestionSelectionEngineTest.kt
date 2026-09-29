package com.example.repository

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.model.DnaTheme
import com.example.model.ExamBlueprint
import com.example.model.PenaltyRule
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
class QuestionSelectionEngineTest {

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
    fun testPaperTwin_distributesQuestionsAccordingToBlueprint() = runBlocking {
        // Insert dummy questions
        val questions = mutableListOf<Question>()
        for (i in 1..50) questions.add(createDummyQuestion(i, "Statement-based"))
        for (i in 51..80) questions.add(createDummyQuestion(i, "Direct Fact"))
        for (i in 81..100) questions.add(createDummyQuestion(i, "Assertion-Reason"))
        
        db.appDao().insertQuestions(questions)

        // Target Blueprint
        val blueprint = ExamBlueprint(
            examId = "TEST_EXAM",
            version = "1.0",
            displayName = "Test Exam",
            positiveMarks = BigDecimal.ONE, allowedTiers = listOf("Tier 1"),
            examDna = listOf(
                DnaTheme("Statement-based", 50, ""),
                DnaTheme("Direct Fact", 30, ""),
                DnaTheme("Assertion-Reason", 20, "")
            )
        )
        
        // Act - Request 10 questions
        val selected = engine.getQuestionsForProfile("Global", blueprint, 10, "Paper Twin")
        
        // Assert
        assertEquals(10, selected.size)
        
        val formatCounts: Map<String, Int> = selected.map { (it as MCQQuestion).questionFormatType }.groupingBy { it }.eachCount()
        
        val stmtCount: Int = formatCounts["Statement-based"] ?: 0
        val factCount: Int = formatCounts["Direct Fact"] ?: 0
        val arCount: Int = formatCounts["Assertion-Reason"] ?: 0
        
        assertTrue("Should have Statement-based questions", stmtCount > 0)
        assertTrue("Should have Direct Fact questions", factCount > 0)
        assertTrue("Should have Assertion-Reason questions", arCount > 0)
        
        // DNA proportions: 5, 3, 2
        assertEquals(5, stmtCount)
        assertEquals(3, factCount)
        assertEquals(2, arCount)
    }
    
    private fun createDummyQuestion(id: Int, format: String): Question {
        return Question(
            id = id,
            topicId = 1,
            tier = "Tier 1",
            format = format,
            examRelevance = "High",
            source = "Test",
            specificExam = "UPSC",
            questionText = "Q$id",
            options = "[{\"id\":\"A\",\"text\":\"A\"},{\"id\":\"B\",\"text\":\"B\"}]",
            correctAnswer = "A",
            explanation = "Exp"
        )
    }
}
