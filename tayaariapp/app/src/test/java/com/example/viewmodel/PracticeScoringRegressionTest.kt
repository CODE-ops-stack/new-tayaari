package com.example.viewmodel

import com.example.model.ExactFraction
import com.example.model.ExamBlueprint
import com.example.model.MCQQuestion
import com.example.model.Option
import com.example.model.OptionRole
import com.example.model.PenaltyRule
import org.junit.Assert.assertEquals
import org.junit.Test
import java.math.BigDecimal
import java.math.MathContext

class PracticeScoringRegressionTest {

    @Test
    fun testBpscScoringMatrices() {
        val bpscBlueprint = ExamBlueprint(
            examId = "BPSC_CCE_72ND_2026",
            version = "2026",
            displayName = "BPSC 72nd CCE",
            positiveMarks = BigDecimal.ONE,
            negativePenaltyRule = PenaltyRule.ONE_THIRD,
            unansweredPenaltyRule = PenaltyRule.NONE
        )

        val mockQuestions = (1..10).map { i ->
            MCQQuestion(
                id = "q$i",
                questionText = "Question $i",
                options = listOf(
                    Option("optA", "A", OptionRole.ANSWER_CHOICE),
                    Option("optB", "B", OptionRole.ANSWER_CHOICE),
                    Option("optC", "C", OptionRole.ANSWER_CHOICE),
                    Option("optD", "D", OptionRole.ANSWER_CHOICE),
                    Option("optE", "E", OptionRole.ABSTAIN)
                ),
                correctAnswerId = "optA",
                chapterCode = "CH1",
                correctExplanation = "Explanation",
                distractorDissections = emptyList()
            )
        }

        // Test A: 10 Correct
        val answersA = mockQuestions.associate { it.id to "optA" }
        val scoreA = PracticeViewModel.Companion.computeScore(answersA, emptySet<String>(), mockQuestions, bpscBlueprint)
        assertEquals(ExactFraction(10, 1), scoreA)

        // Test B: 10 Incorrect
        val answersB = mockQuestions.associate { it.id to "optB" }
        val scoreB = PracticeViewModel.Companion.computeScore(answersB, emptySet<String>(), mockQuestions, bpscBlueprint)
        assertEquals(ExactFraction(-10, 3), scoreB)

        // Test C: 10 Abstain
        val answersC = mockQuestions.associate { it.id to "optE" }
        val scoreC = PracticeViewModel.Companion.computeScore(answersC, emptySet<String>(), mockQuestions, bpscBlueprint)
        assertEquals(ExactFraction.ZERO, scoreC)

        // Test D: 10 Unanswered
        val skippedD = mockQuestions.map { it.id }.toSet()
        val scoreD = PracticeViewModel.Companion.computeScore(emptyMap<String, String>(), skippedD, mockQuestions, bpscBlueprint)
        assertEquals(ExactFraction.ZERO, scoreD)

        // Test E: 6 Correct, 2 Incorrect, 1 Abstain, 1 Unanswered
        val answersE = mutableMapOf<String, String>()
        for (i in 1..6) answersE["q$i"] = "optA"
        for (i in 7..8) answersE["q$i"] = "optB"
        answersE["q9"] = "optE"
        val skippedE = setOf("q10")

        val scoreE = PracticeViewModel.Companion.computeScore(answersE, skippedE, mockQuestions, bpscBlueprint)
        assertEquals(ExactFraction(16, 3), scoreE)

        println("All BPSC 72nd CCE State Machine and Regression Tests (A-E) PASSED.")
    }
}
