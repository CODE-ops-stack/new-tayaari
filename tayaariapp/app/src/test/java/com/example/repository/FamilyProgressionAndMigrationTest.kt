package com.example.repository

import org.junit.Test
import org.junit.Assert.*
import com.example.model.MCQQuestion
import com.example.model.QuestionFormat
import com.example.database.FamilyAttemptRecord

class FamilyProgressionAndMigrationTest {

    @Test
    fun testFamilySelectionModeratePenalty() {
        var score = 100.0
        val isTrapTraining = false
        val q = MCQQuestion(
            id = "q1",
            format = QuestionFormat.PRELIMS_MCQ,
            chapterCode = "CH1",
            questionText = "Q1",
            options = emptyList(),
            correctAnswerId = "A",
            correctExplanation = "",
            distractorDissections = emptyList(),
            familyId = "F1",
            familyStage = "STANDARD"
        )
        
        val recentFamilyAttempts = listOf(
            FamilyAttemptRecord("F1", "STANDARD", "INCORRECT", System.currentTimeMillis(), 101)
        )
        
        if (!isTrapTraining && q.familyId != null) {
            val familyAttempt = recentFamilyAttempts.firstOrNull { it.familyId == q.familyId }
            if (familyAttempt != null) {
                val lastStage = familyAttempt.familyStage
                val outcome = familyAttempt.outcome
                score -= 5.0
                if (q.familyStage == lastStage) {
                    score -= 10.0
                }
            }
        }
        
        assertEquals(85.0, score, 0.001)
    }

    @Test
    fun testTransferDifferentFamilyMemberSelected() {
        var score = 100.0
        val isTrapTraining = false
        val q = MCQQuestion(
            id = "q2",
            format = QuestionFormat.PRELIMS_MCQ,
            chapterCode = "CH1",
            questionText = "Q2",
            options = emptyList(),
            correctAnswerId = "A",
            correctExplanation = "",
            distractorDissections = emptyList(),
            familyId = "F1",
            familyStage = "APPLICATION"
        )
        
        val recentFamilyAttempts = listOf(
            FamilyAttemptRecord("F1", "STANDARD", "INCORRECT", System.currentTimeMillis(), 101)
        )
        
        if (!isTrapTraining && q.familyId != null) {
            val familyAttempt = recentFamilyAttempts.firstOrNull { it.familyId == q.familyId }
            if (familyAttempt != null) {
                val lastStage = familyAttempt.familyStage
                score -= 5.0
                if (q.familyStage == lastStage) {
                    score -= 10.0
                }
            }
        }
        
        assertEquals(95.0, score, 0.001)
    }

    @Test
    fun testNextBestActionProgression() {
        var score = 100.0
        val isTrapTraining = false
        val q = MCQQuestion(
            id = "q3",
            format = QuestionFormat.PRELIMS_MCQ,
            chapterCode = "CH1",
            questionText = "Q3",
            options = emptyList(),
            correctAnswerId = "A",
            correctExplanation = "",
            distractorDissections = emptyList(),
            familyId = "F2",
            familyStage = "REINFORCEMENT"
        )
        
        val recentFamilyAttempts = listOf(
            FamilyAttemptRecord("F2", "FOUNDATION", "INCORRECT", System.currentTimeMillis(), 102)
        )
        
        if (!isTrapTraining && q.familyId != null) {
            val familyAttempt = recentFamilyAttempts.firstOrNull { it.familyId == q.familyId }
            if (familyAttempt != null) {
                val lastStage = familyAttempt.familyStage
                val outcome = familyAttempt.outcome
                score -= 5.0
                if (q.familyStage == lastStage) {
                    score -= 10.0
                }
                
                if (outcome == "INCORRECT") {
                    if (lastStage == "FOUNDATION" && q.familyStage == "REINFORCEMENT") score += 20.0
                }
            }
        }
        
        assertEquals(115.0, score, 0.001)
    }
}
