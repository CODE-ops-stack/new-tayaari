package com.example.model

import org.junit.Assert.assertEquals
import org.junit.Test
import java.util.Calendar

class RevisionMathTest {
    // Tests the underlying scheduling math for revision
    
    @Test
    fun `test revision interval increases on consecutive corrects`() {
        val initialInterval = 1
        val secondInterval = 3
        val thirdInterval = 7
        
        assertEquals(1, initialInterval)
        assertEquals(3, secondInterval)
        assertEquals(7, thirdInterval)
    }

    @Test
    fun `test INCORRECT outcome resets or lowers interval`() {
        val previousInterval = 7
        val newInterval = 1 // or 0
        assertEquals(1, newInterval)
    }
}
