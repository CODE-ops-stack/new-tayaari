import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

replacement = '''
    private suspend fun computeMarksLostAnalysis() {
        var negativeMarkingLoss = java.math.BigDecimal.ZERO
        var unclassifiedLoss = java.math.BigDecimal.ZERO
        var trapRelatedLoss = java.math.BigDecimal.ZERO
        var unansweredOpportunity = java.math.BigDecimal.ZERO
        
        val blueprint = currentProfile ?: ExamBlueprintRegistry.blueprints[0]
        val pos = blueprint.positiveMarks
        val neg = blueprint.negativeMarks
        
        for (q in questionsQueue) {
            val ans = _uiState.value.userAnswers[q.id]
            val correctAns = (q as? com.example.database.Question)?.correctAnswer
            val trap = (q as? com.example.database.Question)?.trapType
            
            if (ans == null) {
                unansweredOpportunity += pos
            } else if (ans != correctAns) {
                negativeMarkingLoss += neg
                // Only count as Trap Loss if explicitly verified in metadata
                if (!trap.isNullOrEmpty() && trap != "None" && trap != "UNCLASSIFIED") {
                    trapRelatedLoss += pos
                } else {
                    unclassifiedLoss += pos
                }
            }
        }
        
        val report = mutableListOf<String>()
        if (negativeMarkingLoss > java.math.BigDecimal.ZERO) {
            report.add("Negative Marking Loss: You lost \ marks purely due to incorrect guesses.")
        }
        if (unansweredOpportunity > java.math.BigDecimal.ZERO) {
            report.add("Unanswered Opportunity: You left \ marks on the table by skipping.")
        }
        if (trapRelatedLoss > java.math.BigDecimal.ZERO) {
            report.add("Verified Trap Loss: You lost \ potential marks falling for confirmed distractors.")
        }
        if (unclassifiedLoss > java.math.BigDecimal.ZERO) {
            report.add("Unclassified Errors: You lost \ potential marks (Requires further diagnostic data to determine if knowledge gap or strategy error).")
        }
        
        if (report.isEmpty()) {
            report.add("Perfect session! No marks lost.")
        }
        
        _uiState.update { it.copy(marksLostReport = report) }
    }
'''

# We need to replace the old function.
import re
content = re.sub(r'private suspend fun computeMarksLostAnalysis\(\) \{.*?\n\s*\}', replacement.strip(), content, flags=re.DOTALL)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
