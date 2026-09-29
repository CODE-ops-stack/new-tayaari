import re

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", encoding="utf-8") as f:
    content = f.read()

# I will find the EXACT timerJob?.cancel() that comes right after this update block in onSubmitAnswerWithConfidence

pattern = r"""(\s*state\.copy\(\s*detectedConfusionPair = null, // Will be updated async.*?\}).*?(timerJob\?\.cancel\(\))"""

block = """        // Confusion Detection and Persistence
        if (!isCorrect && !isAbstain) {
            viewModelScope.launch {
                val initialResult = com.example.repository.ConfusionNetwork.detectConfusion(
                    question.questionText, selectedOption?.text ?: ""
                )
                
                if (initialResult != null) {
                    // Check history to potentially upgrade
                    val history = localRepository.getConfusionEventsForPair(initialResult.pair.id)
                    var finalEvidenceLevel = initialResult.evidenceLevel
                    
                    if (history.isNotEmpty() && finalEvidenceLevel == com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION) {
                        // Upgrade if it happened before
                        finalEvidenceLevel = com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT
                    }
                    
                    val finalResult = initialResult.copy(evidenceLevel = finalEvidenceLevel)
                    
                    localRepository.logConfusionEvent(
                        pairId = finalResult.pair.id,
                        questionId = question.id,
                        selectedOptionText = selectedOption?.text ?: "",
                        evidenceLevel = finalEvidenceLevel
                    )
                    
                    _uiState.update { it.copy(detectedConfusionPair = finalResult) }
                }
            }
        }
"""

def replacer(match):
    return match.group(1) + "\n" + block + "\n        " + match.group(2)

content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", encoding="utf-8") as f:
    f.write(content)
