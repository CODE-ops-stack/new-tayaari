package com.example.model

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ContentImportRulesTest {

    @Test
    fun `test valid question parsing rules`() {
        // A valid question must have: text, non-empty options, answerId, topicId
        assertTrue(isValidContent("Q1", listOf("A", "B"), "A", 1))
    }
    
    @Test
    fun `test invalid question rejection`() {
        // Missing text
        assertFalse(isValidContent("", listOf("A", "B"), "A", 1))
        
        // Missing options
        assertFalse(isValidContent("Q1", emptyList(), "A", 1))
        
        // Missing answer
        assertFalse(isValidContent("Q1", listOf("A", "B"), "", 1))
    }

    private fun isValidContent(text: String, options: List<String>, answer: String, topic: Int): Boolean {
        if (text.isBlank()) return false
        if (options.isEmpty()) return false
        if (answer.isBlank()) return false
        if (topic <= 0) return false
        return true
    }
}
