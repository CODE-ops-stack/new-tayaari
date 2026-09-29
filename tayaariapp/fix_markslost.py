import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Add computeMarksLostAnalysis
analysis_func = '''
    private fun computeMarksLostAnalysis(): List<String> {
        val currentState = _uiState.value
        val report = mutableListOf<String>()
        var incorrectCount = 0
        var skippedCount = 0
        
        for (q in questionsQueue) {
            val mcq = q as? MCQQuestion ?: continue
            val ans = currentState.userAnswers[q.id]
            if (ans != null) {
                val option = mcq.options.find { it.id == ans }
                if (ans != mcq.correctAnswerId && option?.role != com.example.model.OptionRole.ABSTAIN) {
                    incorrectCount++
                }
            } else if (currentState.skippedQuestions.contains(q.id)) {
                skippedCount++
            }
        }
        
        val pos = currentProfile?.positiveMarks ?: java.math.BigDecimal.ONE
        val neg = currentProfile?.negativeMarks ?: java.math.BigDecimal("0.33")
        val unans = currentProfile?.unansweredPenalty ?: java.math.BigDecimal.ZERO
        
        if (incorrectCount > 0) {
            val lostToNeg = java.math.BigDecimal(incorrectCount).multiply(neg)
            report.add("Lost " + lostToNeg.toPlainString() + " marks due to " + incorrectCount + " incorrect answers.")
        }
        if (skippedCount > 0 && unans > java.math.BigDecimal.ZERO) {
            val lostToSkip = java.math.BigDecimal(skippedCount).multiply(unans)
            report.add("Lost " + lostToSkip.toPlainString() + " marks due to " + skippedCount + " unanswered/skipped questions.")
        }
        
        if (report.isEmpty()) {
            report.add("Perfect score or no penalties applied!")
        }
        
        return report
    }
'''

# Find the end and insert it
last_brace_index = content.rfind('}')
if last_brace_index != -1:
    content = content[:last_brace_index] + analysis_func + '}\n'

# Now call it in isTestFinished = true
content = content.replace(
    '_uiState.update { it.copy(isTestFinished = true) }',
    '_uiState.update { it.copy(isTestFinished = true, marksLostReport = computeMarksLostAnalysis()) }'
)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
