package com.example.viewmodel

import org.junit.Test
import java.math.BigDecimal
import java.math.MathContext

class ExactScoringDebug {
    @Test
    fun debug() {
        val correctCount = 6
        val incorrectCount = 2
        val positiveMarks = BigDecimal("1")
        val num = BigDecimal("1")
        val den = BigDecimal("3")
        
        val correctTotal = positiveMarks.multiply(BigDecimal(correctCount))
        val penaltyNumerator = BigDecimal(incorrectCount).multiply(positiveMarks).multiply(num)
        
        val totalNumerator = correctTotal.multiply(den).subtract(penaltyNumerator)
        val score = totalNumerator.divide(den, MathContext.DECIMAL128)
        
        val expected = BigDecimal("6").subtract(BigDecimal("2").divide(BigDecimal("3"), MathContext.DECIMAL128))
        
        println("Score: " + score)
        println("Expected: " + expected)
        println("Diff: " + score.compareTo(expected))
    }
}
