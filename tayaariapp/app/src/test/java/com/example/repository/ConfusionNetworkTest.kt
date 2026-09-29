package com.example.repository

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

class ConfusionNetworkTest {

    @Test
    fun testOnlyOneKeyword_returnsNull() {
        val result = ConfusionNetwork.detectConfusion("What is el nino?", "It is a climate phenomenon")
        assertNull(result)
    }

    @Test
    fun testQuestionAAndOptionA_returnsPossibleConfusion() {
        // "el nino" (A) and "warming" (A) -> POSSIBLE_CONFUSION
        val result = ConfusionNetwork.detectConfusion("What is el nino?", "It causes warming")
        assertNotNull(result)
        assertEquals(ConfusionEvidenceLevel.POSSIBLE_CONFUSION, result?.evidenceLevel)
        assertEquals("el_nino_la_nina", result?.pair?.id)
    }
    
    @Test
    fun testContradictoryMatch_returnsConfirmedContext() {
        // "el nino" (A) and "cooling" (B) -> CONFIRMED_CONTEXT
        val result = ConfusionNetwork.detectConfusion("What is el nino?", "It is characterized by cooling")
        assertNotNull(result)
        assertEquals(ConfusionEvidenceLevel.CONFIRMED_CONTEXT, result?.evidenceLevel)
        assertEquals("el_nino_la_nina", result?.pair?.id)
    }
}
