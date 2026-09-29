package com.example.repository

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.database.*
import com.example.model.*
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.math.BigDecimal

@RunWith(RobolectricTestRunner::class)
class PatternShockEngineTest {

    private lateinit var db: AppDatabase
    private lateinit var repo: LocalRepository
    private lateinit var qEngine: QuestionSelectionEngine
    private lateinit var pEngine: PressureLadderEngine
    private lateinit var engine: PatternShockEngine
    
    private val blueprint = ExamBlueprint(
        examId = "TEST", version = "1", displayName = "Test",
        optionCount = 4, positiveMarks = BigDecimal.ONE,
        negativePenaltyRule = PenaltyRule.NONE, unansweredPenaltyRule = PenaltyRule.NONE,
        synthesizeAbstainOption = false, abstainOptionLabel = "",
        defaultRelevance = "Core", recommendedPracticeMode = "Standard",
        allowedTiers = listOf("Medium", "Elite"), effectiveDate = "",
        sourceReference = "", lastVerificationDate = "", isActive = true,
        examDna = emptyList<DnaTheme>()
    )

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
        qEngine = QuestionSelectionEngine(repo)
        pEngine = PressureLadderEngine()
        engine = PatternShockEngine(repo, pEngine)
    }

    @After
    fun tearDown() {
        db.close()
    }

    private fun insertQuestion(id: Int, format: String, tier: String, distractorDissections: String = "[]", text: String = "Test Q") {
        runBlocking {
            db.appDao().insertQuestions(listOf(
                Question(
                    id = id, topicId = 1, tier = tier, format = format, examRelevance = "Core",
                    source = "PYQ", specificExam = "Test", questionText = text,
                    options = "[{\"id\":\"A\", \"text\":\"A\"}, {\"id\":\"B\", \"text\":\"B\"}]",
                    correctAnswer = "A", explanation = "Exp", distractorDissections = distractorDissections
                )
            ))
        }
    }

    @Test
    fun testTimeShock_AppliesCorrectTimeLimit() = runBlocking {
        insertQuestion(1, "Direct Fact", "Medium")
        val paper = engine.generateShockPaper(blueprint, ShockProfile.TIME_SHOCK, 1)
        assertEquals(1, paper.questions.size)
        val q = paper.questions.first() as MCQQuestion
        val config = pEngine.getPressureConfig(4)
        assertEquals(config.timeLimitSecondsPerQuestion, q.timeLimitSeconds)
    }

    @Test
    fun testFormatShock_PrioritizesAtypicalFormats() = runBlocking {
        insertQuestion(1, "Direct Fact", "Medium")
        insertQuestion(2, "Statement-based", "Medium")
        insertQuestion(3, "Assertion-Reason", "Medium")
        
        val paper = engine.generateShockPaper(blueprint, ShockProfile.FORMAT_SHOCK, 2)
        assertEquals(2, paper.questions.size)
        val formats = paper.questions.map { it.questionFormatType }
        assertTrue(formats.all { it.contains("Statement") || it.contains("Assertion") })
    }

    @Test
    fun testInsufficientData_ValidationFails() = runBlocking {
        insertQuestion(1, "Direct Fact", "Medium")
        val paper = engine.generateShockPaper(blueprint, ShockProfile.FORMAT_SHOCK, 5)
        
        assertFalse(paper.report.passedValidation)
        assertEquals(0, paper.report.actualTiers["status_pass"])
        assertEquals(1, paper.report.actualTiers["status_insufficient"])
    }

    @Test
    fun testWordingShock_FiltersNotQuestions() = runBlocking {
        insertQuestion(1, "Direct Fact", "Medium", text = "Which is true?")
        insertQuestion(2, "Direct Fact", "Medium", text = "Which of the following is NOT correct?")
        
        val paper = engine.generateShockPaper(blueprint, ShockProfile.WORDING_SHOCK, 1)
        assertEquals(1, paper.questions.size)
        assertTrue(paper.questions.first().questionText.contains("NOT"))
    }
}
