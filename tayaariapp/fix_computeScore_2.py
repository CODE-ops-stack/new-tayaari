import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Replace private fun computeScore with companion object { fun computeScore }
old_func = '''    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {
        if (profile == null) error("Missing blueprint configuration")
        
        var score = java.math.BigDecimal.ZERO
        val positive = profile.positiveMarks
        val negative = profile.negativeMarks // Ensure math exactness
        val unansweredPen = profile.unansweredPenalty
        
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
    }'''

new_func = '''    companion object {
        fun computeScore(
            answers: Map<String, String>,
            skipped: Set<String>,
            questions: List<com.example.model.ExamQuestion>,
            profile: com.example.model.ExamBlueprint?
        ): java.math.BigDecimal {
            if (profile == null) error("Missing blueprint configuration")
            
            var score = java.math.BigDecimal.ZERO
            val positive = profile.positiveMarks
            val negative = profile.negativeMarks // Ensure math exactness
            val unansweredPen = profile.unansweredPenalty
            
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
    }'''

content = content.replace(old_func, new_func)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
