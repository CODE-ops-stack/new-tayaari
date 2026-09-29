package com.example.repository

import org.junit.Test
import org.junit.Assert.*
import com.example.model.ExamBlueprint
import com.example.model.DnaTheme
import com.example.model.MCQQuestion
import com.example.model.QuestionFormat

class PaperTwinValidationTest {

    @Test
    fun testPaperTwinDistribution() {
        val blueprint = ExamBlueprint(
            examId = "test_exam",
            version = "1.0",
            displayName = "Test Exam",
            examDna = listOf(
                DnaTheme("Statement-based", 45),
                DnaTheme("Direct Fact", 30),
                DnaTheme("Assertion-Reason", 25)
            )
        )
        
        // Mock a pool of questions
        val pool = mutableListOf<com.example.model.ExamQuestion>()
        for (i in 1..50) {
            pool.add(MCQQuestion(
                id = "q$i",
                format = QuestionFormat.PRELIMS_MCQ,
                chapterCode = "CH1",
                questionText = "Q",
                options = emptyList(),
                correctAnswerId = "A",
                correctExplanation = "Explanation",
                distractorDissections = emptyList(),
                questionFormatType = if (i <= 20) "Statement-based" else if (i <= 35) "Direct Fact" else "Assertion-Reason"
            ))
        }
        
        // Engine logic emulation
        val targetCount = 10
        val selected = mutableListOf<com.example.model.ExamQuestion>()
        for (theme in blueprint.examDna) {
            val themeCount = Math.round((theme.historicalWeightage / 100.0) * targetCount).toInt()
            val themeQuestions = pool.filter { it.questionFormatType == theme.themeName }.take(themeCount)
            selected.addAll(themeQuestions)
        }
        
        val statementCount = selected.count { it.questionFormatType == "Statement-based" }
        val factCount = selected.count { it.questionFormatType == "Direct Fact" }
        
        assertTrue("Statement count should be close to 45%", statementCount in 4..5)
        assertTrue("Fact count should be close to 30%", factCount in 2..4)
    }
}

