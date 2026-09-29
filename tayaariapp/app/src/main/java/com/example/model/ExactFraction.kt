package com.example.model

import java.math.BigDecimal
import java.math.MathContext
import java.math.RoundingMode

data class ExactFraction(
    val numerator: Long,
    val denominator: Long
) {
    init {
        require(denominator != 0L) { "Denominator cannot be zero" }
    }

    fun simplify(): ExactFraction {
        val gcd = gcd(Math.abs(numerator), Math.abs(denominator))
        var num = numerator / gcd
        var den = denominator / gcd
        if (den < 0) {
            num = -num
            den = -den
        }
        return ExactFraction(num, den)
    }

    operator fun plus(other: ExactFraction): ExactFraction {
        val num = this.numerator * other.denominator + other.numerator * this.denominator
        val den = this.denominator * other.denominator
        return ExactFraction(num, den).simplify()
    }

    operator fun minus(other: ExactFraction): ExactFraction {
        val num = this.numerator * other.denominator - other.numerator * this.denominator
        val den = this.denominator * other.denominator
        return ExactFraction(num, den).simplify()
    }

    operator fun times(other: ExactFraction): ExactFraction {
        val num = this.numerator * other.numerator
        val den = this.denominator * other.denominator
        return ExactFraction(num, den).simplify()
    }

    fun toDisplayString(): String {
        return BigDecimal(numerator)
            .divide(BigDecimal(denominator), MathContext.DECIMAL128)
            .setScale(2, RoundingMode.HALF_UP)
            .stripTrailingZeros()
            .toPlainString()
    }

    // Ensure equals handles simplified equality
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is ExactFraction) return false
        val s1 = this.simplify()
        val s2 = other.simplify()
        return s1.numerator == s2.numerator && s1.denominator == s2.denominator
    }

    override fun hashCode(): Int {
        val s1 = this.simplify()
        var result = s1.numerator.hashCode()
        result = 31 * result + s1.denominator.hashCode()
        return result
    }

    private fun gcd(a: Long, b: Long): Long {
        var x = a
        var y = b
        while (y > 0) {
            val temp = y
            y = x % y
            x = temp
        }
        return x
    }

    companion object {
        val ZERO = ExactFraction(0, 1)

        fun fromBigDecimal(bd: BigDecimal): ExactFraction {
            val scale = bd.scale()
            var den = 1L
            for (i in 0 until Math.max(0, scale)) den *= 10
            val num = bd.unscaledValue().toLong() * if (scale < 0) {
                var factor = 1L
                for (i in 0 until -scale) factor *= 10
                factor
            } else 1L
            return ExactFraction(num, den).simplify()
        }
    }
}
