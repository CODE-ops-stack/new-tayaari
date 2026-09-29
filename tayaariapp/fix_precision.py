import codecs

with codecs.open('app/src/main/java/com/example/model/ExamBlueprint.kt', 'r', 'utf-8') as f:
    content = f.read()

replacement = '''    private fun calcOneThirdNegative(positive: BigDecimal): BigDecimal {
        // Use MathContext.DECIMAL128 for high precision instead of fixed scale 4, to avoid 49.995 rounding errors
        return positive.divide(BigDecimal("3"), java.math.MathContext.DECIMAL128)
    }

    private fun calcOneFourthNegative(positive: BigDecimal): BigDecimal {
        return positive.divide(BigDecimal("4"), java.math.MathContext.DECIMAL128)
    }'''

content = content.replace('''    private fun calcOneThirdNegative(positive: BigDecimal): BigDecimal {
        return positive.divide(BigDecimal("3"), 4, RoundingMode.HALF_UP)
    }

    private fun calcOneFourthNegative(positive: BigDecimal): BigDecimal {
        return positive.divide(BigDecimal("4"), 4, RoundingMode.HALF_UP)
    }''', replacement)

with codecs.open('app/src/main/java/com/example/model/ExamBlueprint.kt', 'w', 'utf-8') as f:
    f.write(content)
