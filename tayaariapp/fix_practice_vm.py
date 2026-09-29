file = 'app/src/main/java/com/example/viewmodel/PracticeViewModel.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('currentScore = BigDecimal.ZERO', 'currentScore = ExactFraction.ZERO')
text = text.replace('import java.math.BigDecimal\n', 'import java.math.BigDecimal\nimport com.example.model.ExactFraction\n')

# update computeScore definition
text = text.replace('): BigDecimal {', '): ExactFraction {')
text = text.replace('if (profile == null) return BigDecimal.ZERO', 'if (profile == null) return ExactFraction.ZERO')

old_compute = """            val num = BigDecimal(profile.negativePenaltyRule.numerator)
            val den = BigDecimal(profile.negativePenaltyRule.denominator)
            
            val correctTotal = profile.positiveMarks.multiply(BigDecimal(correctCount))
            val penaltyNumerator = BigDecimal(incorrectCount).multiply(profile.positiveMarks).multiply(num)
            
            val totalNumerator = correctTotal.multiply(den).subtract(penaltyNumerator)
            return totalNumerator.divide(den, java.math.MathContext.DECIMAL128)"""

new_compute = """            val posMarks = ExactFraction.fromBigDecimal(profile.positiveMarks)
            val correctFrac = posMarks * ExactFraction(correctCount.toLong(), 1L)
            val num = profile.negativePenaltyRule.numerator.toLong()
            val den = profile.negativePenaltyRule.denominator.toLong()
            val penRule = ExactFraction(num, den)
            
            val penaltyFrac = ExactFraction(incorrectCount.toLong(), 1L) * posMarks * penRule
            return correctFrac - penaltyFrac"""

text = text.replace(old_compute, new_compute)

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
