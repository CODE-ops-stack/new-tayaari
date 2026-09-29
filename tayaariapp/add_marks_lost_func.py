import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Add a function computeMarksLostAnalysis()
marks_lost_func = '''
    private suspend fun computeMarksLostAnalysis() {
        // compute marks lost based on userAnswers and the current questions
        var negativeMarkingLoss = java.math.BigDecimal.ZERO
        var knowledgeLoss = java.math.BigDecimal.ZERO
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
                if (!trap.isNullOrEmpty() && trap != "None") {
                    trapRelatedLoss += pos
                } else {
                    knowledgeLoss += pos
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
            report.add("Trap-related Loss: You lost \ potential marks falling for distractors.")
        }
        if (knowledgeLoss > java.math.BigDecimal.ZERO) {
            report.add("Knowledge Gap Loss: You lost \ potential marks on non-trap incorrect answers.")
        }
        
        if (report.isEmpty()) {
            report.add("Perfect session! No marks lost.")
        }
        
        _uiState.update { it.copy(marksLostReport = report) }
    }
'''

# Find the end of test condition
old_end = '''// End of test
            _uiState.update { it.copy(isTestFinished = true) }'''

new_end = '''// End of test
            viewModelScope.launch {
                computeMarksLostAnalysis()
                _uiState.update { it.copy(isTestFinished = true) }
            }'''

content = content.replace(old_end, new_end)
content = content.replace('}\n\n}', '}\n' + marks_lost_func + '\n}')

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
