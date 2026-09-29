import codecs

with codecs.open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", "utf-8") as f:
    content = f.read()

old_report = '''        val neg = profile.negativeMarks
        val unans = profile.unansweredPenalty
        
        if (incorrectCount > 0) {
            val lostToNeg = java.math.BigDecimal(incorrectCount).multiply(neg)
            report.add("Lost " + lostToNeg.toPlainString() + " marks due to " + incorrectCount + " incorrect answers.")
        }
        if (skippedCount > 0 && unans > java.math.BigDecimal.ZERO) {
            val lostToSkip = java.math.BigDecimal(skippedCount).multiply(unans)
            report.add("Lost " + lostToSkip.toPlainString() + " marks due to " + skippedCount + " unanswered/skipped questions.")
        }'''

new_report = '''        val positive = profile.positiveMarks
        
        if (incorrectCount > 0 && profile.negativePenaltyRule != com.example.model.PenaltyRule.NONE) {
            val negNum = java.math.BigDecimal(incorrectCount * profile.negativePenaltyRule.numerator)
            val negDen = java.math.BigDecimal(profile.negativePenaltyRule.denominator)
            val lostToNeg = positive.multiply(negNum).divide(negDen, java.math.MathContext.DECIMAL128)
            report.add("Lost " + lostToNeg.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString() + " marks due to " + incorrectCount + " incorrect answers.")
        }
        if (skippedCount > 0 && profile.unansweredPenaltyRule != com.example.model.PenaltyRule.NONE) {
            val unansNum = java.math.BigDecimal(skippedCount * profile.unansweredPenaltyRule.numerator)
            val unansDen = java.math.BigDecimal(profile.unansweredPenaltyRule.denominator)
            val lostToSkip = positive.multiply(unansNum).divide(unansDen, java.math.MathContext.DECIMAL128)
            report.add("Lost " + lostToSkip.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString() + " marks due to " + skippedCount + " unanswered/skipped questions.")
        }'''

content = content.replace(old_report, new_report)

with codecs.open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", "utf-8") as f:
    f.write(content)
