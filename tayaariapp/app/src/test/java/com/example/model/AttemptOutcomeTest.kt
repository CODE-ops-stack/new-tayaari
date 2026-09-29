package com.example.model

import org.junit.Assert.assertEquals
import org.junit.Test

class AttemptOutcomeTest {
    @Test
    fun `test all outcome strings`() {
        assertEquals("CORRECT", AttemptOutcome.CORRECT.name)
        assertEquals("INCORRECT", AttemptOutcome.INCORRECT.name)
        assertEquals("ABSTAINED", AttemptOutcome.ABSTAINED.name)
        assertEquals("UNANSWERED", AttemptOutcome.UNANSWERED.name)
    }

    @Test
    fun `test outcome persistence mapping`() {
        val persistedCorrect = AttemptOutcome.valueOf("CORRECT")
        assertEquals(AttemptOutcome.CORRECT, persistedCorrect)

        val persistedAbstained = AttemptOutcome.valueOf("ABSTAINED")
        assertEquals(AttemptOutcome.ABSTAINED, persistedAbstained)
    }
}
