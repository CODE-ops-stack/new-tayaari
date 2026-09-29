import re
import codecs

with codecs.open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", "utf-8") as f:
    text = f.read()

# Replace computeScore
text = re.sub(
    r'fun computeScore\(.*?\)\s*:\s*java\.math\.BigDecimal\s*\{.*?return score\s*\}',
    '''fun computeScore(
            answers: Map<String, String>,
            skipped: Set<String>,
            questions: List<com.example.model.ExamQuestion>,
            profile: com.example.model.ExamBlueprint?
        ): java.math.BigDecimal {
            if (profile == null) error("Missing blueprint configuration")
            
            var correctCount = 0L
            var incorrectCount = 0L
            var unansweredCount = 0L
            val positive = profile.positiveMarks
            
            for (q in questions) {
                val mcq = q as? com.example.model.MCQQuestion ?: continue
                if (answers.containsKey(q.id)) {
                    val ans = answers[q.id]
                    val option = mcq.options.find { it.id == ans }
                    if (mcq.correctAnswerId == ans) {
                        correctCount++
                    } else if (option?.role != com.example.model.OptionRole.ABSTAIN) {
                        incorrectCount++
                    }
                } else if (skipped.contains(q.id)) {
                    unansweredCount++
                }
            }
            
            var totalScore = positive.multiply(java.math.BigDecimal(correctCount))
            
            if (profile.negativePenaltyRule != com.example.model.PenaltyRule.NONE && incorrectCount > 0) {
                val negNum = java.math.BigDecimal(incorrectCount * profile.negativePenaltyRule.numerator)
                val negDen = java.math.BigDecimal(profile.negativePenaltyRule.denominator)
                val negTotal = positive.multiply(negNum).divide(negDen, java.math.MathContext.DECIMAL128)
                totalScore = totalScore.subtract(negTotal)
            }
            
            if (profile.unansweredPenaltyRule != com.example.model.PenaltyRule.NONE && unansweredCount > 0) {
                val unansNum = java.math.BigDecimal(unansweredCount * profile.unansweredPenaltyRule.numerator)
                val unansDen = java.math.BigDecimal(profile.unansweredPenaltyRule.denominator)
                val unansTotal = positive.multiply(unansNum).divide(unansDen, java.math.MathContext.DECIMAL128)
                totalScore = totalScore.subtract(unansTotal)
            }
            
            return totalScore
        }''',
    text,
    flags=re.DOTALL
)

# Replace generateMarksLostReport
text = re.sub(
    r'val neg = profile\.negativeMarks.*?if \(report\.isEmpty\(\)\)',
    '''val positive = profile.positiveMarks
        
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
        }
        
        if (report.isEmpty())''',
    text,
    flags=re.DOTALL
)

with codecs.open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", "utf-8") as f:
    f.write(text)
