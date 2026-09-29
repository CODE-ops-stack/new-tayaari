package com.example.model

import org.junit.Assert.assertEquals
import org.junit.Test

class BlindSpotEngineTest {

    @Test
    fun `test blind spot evidence categorization`() {
        assertEquals("INSUFFICIENT", categorizeEvidence(2))
        assertEquals("EMERGING", categorizeEvidence(6))
        assertEquals("CONFIRMED", categorizeEvidence(15))
    }

    private fun categorizeEvidence(attempts: Int): String {
        return when {
            attempts < 5 -> "INSUFFICIENT"
            attempts < 10 -> "EMERGING"
            else -> "CONFIRMED"
        }
    }
}
