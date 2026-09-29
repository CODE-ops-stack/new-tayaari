import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Fix the broken insertion
bad_signature = '''class PracticeViewModel(

    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {
        var score = java.math.BigDecimal.ZERO
        val positive = profile?.positiveMarks ?: java.math.BigDecimal.ONE
        val negative = profile?.negativeMarks ?: java.math.BigDecimal("0.33")
        val unansweredPen = profile?.unansweredPenalty ?: java.math.BigDecimal.ZERO
        
        for (q in questions) {
            val mcq = q as? MCQQuestion ?: continue
            if (answers.containsKey(q.id)) {
                val ans = answers[q.id]
                val option = mcq.options.find { it.id == ans }
                if (mcq.correctAnswerId == ans) {
                    score = score.add(positive)
                } else if (option?.role == com.example.model.OptionRole.ABSTAIN) {
                    // zero penalty
                } else {
                    score = score.subtract(negative)
                }
            } else if (skipped.contains(q.id)) {
                score = score.subtract(unansweredPen)
            }
        }
        return score
    }
'''

content = content.replace(bad_signature, 'class PracticeViewModel(')

# Now insert it at the end of the class (before the last closing brace)
# The class ends at the last '}'
# We can just use a regex to replace the last '}' with the function + '}'
last_brace_index = content.rfind('}')
if last_brace_index != -1:
    content = content[:last_brace_index] + '''
    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {
        var score = java.math.BigDecimal.ZERO
        val positive = profile?.positiveMarks ?: java.math.BigDecimal.ONE
        val negative = profile?.negativeMarks ?: java.math.BigDecimal("0.33")
        val unansweredPen = profile?.unansweredPenalty ?: java.math.BigDecimal.ZERO
        
        for (q in questions) {
            val mcq = q as? MCQQuestion ?: continue
            if (answers.containsKey(q.id)) {
                val ans = answers[q.id]
                val option = mcq.options.find { it.id == ans }
                if (mcq.correctAnswerId == ans) {
                    score = score.add(positive)
                } else if (option?.role == com.example.model.OptionRole.ABSTAIN) {
                    // zero penalty
                } else {
                    score = score.subtract(negative)
                }
            } else if (skipped.contains(q.id)) {
                score = score.subtract(unansweredPen)
            }
        }
        return score
    }
}
'''

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
