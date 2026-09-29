package com.example.database

import com.example.model.AttemptOutcome
import org.junit.Assert.assertEquals
import org.junit.Test

// This tests the data model serialization of the database entities
class DatabasePersistenceTest {

    @Test
    fun `test QuestionAttemptEntity serialization`() {
        val attempt = QuestionAttemptEntity(
            questionId = "q1",
            timestamp = 1000L,
            outcome = AttemptOutcome.UNANSWERED.name,
            confidence = "None",
            timeSpentSeconds = 5,
            trapFallenInto = null
        )
        
        assertEquals("UNANSWERED", attempt.outcome)
        val enumValue = AttemptOutcome.valueOf(attempt.outcome)
        assertEquals(AttemptOutcome.UNANSWERED, enumValue)
    }

    @Test
    fun `test RevisionItemEntity mastery states`() {
        val rev = RevisionItemEntity(
            questionId = "q1",
            firstAttemptTime = 100L,
            lastAttemptTime = 200L,
            attemptCount = 2,
            correctCount = 1,
            incorrectCount = 1,
            masteryState = "IMPROVING",
            nextRevisionDate = 300L,
            priority = 3
        )
        assertEquals("IMPROVING", rev.masteryState)
        assertEquals(3, rev.priority)
    }
}
