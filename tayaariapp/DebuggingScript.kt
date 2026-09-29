package com.example.viewmodel

import org.junit.Test

class DebuggingScript {
    @Test
    fun debug() {
        val total = java.math.BigDecimal("6")
        val p1 = java.math.BigDecimal.ONE.divide(java.math.BigDecimal("3"), java.math.MathContext.DECIMAL128)
        val scoreE = total.subtract(p1).subtract(p1)
        val expectedE = java.math.BigDecimal("6").subtract(java.math.BigDecimal("2").divide(java.math.BigDecimal("3"), java.math.MathContext.DECIMAL128))
        println("scoreE: " + scoreE)
        println("expectedE: " + expectedE)
        println("diff: " + expectedE.compareTo(scoreE))
    }
}
