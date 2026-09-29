import codecs
with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'fun onOptionPending(optionId: String)' in line:
        insert = '''
    fun toggleOptionCrossedOut(optionId: String) {
        val currentState = _uiState.value
        if (currentState.selectedOptionId != null) return // Already submitted
        
        _uiState.update { state ->
            val currentCrossedOut = state.crossedOutOptionIds.toMutableSet()
            if (currentCrossedOut.contains(optionId)) {
                currentCrossedOut.remove(optionId)
            } else {
                currentCrossedOut.add(optionId)
            }
            state.copy(crossedOutOptionIds = currentCrossedOut)
        }
    }
'''
        new_lines.append(insert)
        new_lines.append(line)
        continue
        
    if 'val isCorrect = question.correctAnswerId == optionId' in line and 'fun submitAnswerWithConfidence' in ''.join(lines[i-10:i]):
        new_lines.append(line)
        new_lines.append('        val crossedOutCorrect = currentState.crossedOutOptionIds.contains(question.correctAnswerId)\n')
        new_lines.append('        val isFatalElimination = crossedOutCorrect\n')
        continue
        
    if 'val points = if (isCorrect)' in line and 'submitAnswerWithConfidence' in ''.join(lines[i-20:i]):
        new_lines.append('            var points = if (isCorrect) (currentProfile?.positiveMarks ?: java.math.BigDecimal.ONE) else (currentProfile?.negativeMarks?.negate() ?: java.math.BigDecimal("-0.33"))\n')
        new_lines.append('            if (isFatalElimination) points = points.subtract(java.math.BigDecimal("0.5")) // extra penalty for eliminating correct answer\n')
        continue

    if 'val associatedTrap = question.distractorDissections.find { it.optionId == optionId }?.trapType' in line:
        new_lines.append('        val associatedTrap = if (isFatalElimination) "Fatal Elimination" else question.distractorDissections.find { it.optionId == optionId }?.trapType\n')
        continue
        
    if 'fun showCurrentQuestion()' in line:
        new_lines.append(line)
        continue
        
    if 'isBookmarked = isMarked,' in line and 'showCurrentQuestion' in ''.join(lines[i-15:i]):
        new_lines.append(line)
        new_lines.append('                        crossedOutOptionIds = emptySet(),\n')
        new_lines.append('                        pendingOptionId = null,\n')
        new_lines.append('                        selectedConfidence = null,\n')
        continue
        
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
