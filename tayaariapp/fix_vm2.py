import re

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", encoding="utf-8") as f:
    content = f.read()

# I will find all instances of the block and replace them with just timerJob?.cancel() EXCEPT the one that is inside `onSubmitAnswerWithConfidence`.
# Actually, the block is:
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

content = content.replace(block, "")

# Now I'll add it back only inside onSubmitAnswerWithConfidence
# I'll find:
target = """          _uiState.update { state ->
              val updatedAnswers = state.userAnswers.toMutableMap()
              updatedAnswers[question.id] = optionId
              
              val updatedSkipped = state.skippedQuestions.toMutableSet()
              updatedSkipped.remove(question.id)
              
              val newScore = computeScore(updatedAnswers, updatedSkipped, questionsQueue, currentProfile)
              
              state.copy(
                  detectedConfusionPair = null, // Will be updated async
                  selectedOptionId = optionId,
                  pendingOptionId = null,
                  selectedConfidence = confidence,
                  currentScore = newScore,
                  userAnswers = updatedAnswers,
                  skippedQuestions = updatedSkipped
              ) 
          }
          
          timerJob?.cancel()"""

if target in content:
    content = content.replace(target, target.replace("timerJob?.cancel()", block + "\n          timerJob?.cancel()"))
else:
    print("Could not find the target block to add it back")

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", encoding="utf-8") as f:
    f.write(content)
