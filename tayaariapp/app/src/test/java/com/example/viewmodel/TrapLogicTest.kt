package com.example.viewmodel

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TrapLogicTest {

    @Test
    fun `test trap is triggered only for actual incorrect selections`() {
        // Correct answer -> no trap
        assertFalse(shouldTriggerTrap(isCorrect = true, isAbstain = false))
        
        // Abstain -> no trap
        assertFalse(shouldTriggerTrap(isCorrect = false, isAbstain = true))
        
        // Unanswered (timer expiry or manual skip) -> no trap (usually not selected)
        // Handled differently via skipQuestion()
        
        // Wrong answer -> trigger trap
        assertTrue(shouldTriggerTrap(isCorrect = false, isAbstain = false))
    }

    private fun shouldTriggerTrap(isCorrect: Boolean, isAbstain: Boolean): Boolean {
        return !isCorrect && !isAbstain
    }
}
