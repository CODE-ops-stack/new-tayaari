package com.example.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.math.BigDecimal

class BlueprintRegressionTest {

    @Test
    fun `test BPSC 72nd CCE Blueprint properties`() {
        val bpsc = ExamBlueprintRegistry.getBlueprint("BPSC_CCE_72ND_2026")
        assertNotNull("Blueprint must exist", bpsc)
        requireNotNull(bpsc)
        
        assertTrue("Must synthesize abstain option E", bpsc.synthesizeAbstainOption)
        assertEquals("BPSC should have 5 options configured", 5, bpsc.optionCount)
        assertEquals("BPSC penalty rule is ONE_THIRD", PenaltyRule.ONE_THIRD, bpsc.negativePenaltyRule)
        assertEquals("BPSC unanswered penalty rule is ONE_THIRD", PenaltyRule.ONE_THIRD, bpsc.unansweredPenaltyRule)
        assertEquals("Positive marks should be 1.0", BigDecimal("1.0"), bpsc.positiveMarks)
    }

    @Test
    fun `test UPSC CSE 2026 Blueprint properties`() {
        val upsc = ExamBlueprintRegistry.getBlueprint("UPSC_CSE_2026")
        assertNotNull("Blueprint must exist", upsc)
        requireNotNull(upsc)
        
        assertEquals("UPSC should not synthesize abstain", false, upsc.synthesizeAbstainOption)
        assertEquals("UPSC penalty rule is ONE_THIRD", PenaltyRule.ONE_THIRD, upsc.negativePenaltyRule)
        assertEquals("UPSC has 4 options", 4, upsc.optionCount)
    }

    @Test
    fun `test SSC CGL 2025 Blueprint properties`() {
        val ssc = ExamBlueprintRegistry.getBlueprint("SSC_CGL_2025")
        assertNotNull(ssc)
        requireNotNull(ssc)
        
        assertEquals(false, ssc.synthesizeAbstainOption)
        assertEquals(PenaltyRule.ONE_FOURTH, ssc.negativePenaltyRule)
        assertEquals(BigDecimal("2.0"), ssc.positiveMarks)
    }
}
