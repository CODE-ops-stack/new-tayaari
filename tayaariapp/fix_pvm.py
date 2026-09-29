import re

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", encoding="utf-8") as f:
    content = f.read()

# Revert my bad replace
content = content.replace("state.copy(`n                detectedConfusionPair = if (!isCorrect) com.example.repository.ConfusionNetwork.detectConfusion(question.questionText, selectedOption?.text ?: \"\") else null,", "state.copy(")
content = content.replace("state.copy(`n                detectedConfusionPair = if (!isCorrect) com.example.repository.ConfusionNetwork.detectConfusion(question.questionText, selectedOption?.text ?: \"\") else null,crossedOutOptionIds = currentCrossedOut)", "state.copy(crossedOutOptionIds = currentCrossedOut)")

def replacement(match):
    return match.group(0).replace(
        "state.copy(",
        "state.copy(\n                  detectedConfusionPair = if (!isCorrect) com.example.repository.ConfusionNetwork.detectConfusion(question.questionText, selectedOption?.text ?: \"\") else null,"
    )

content = re.sub(r'fun submitAnswerWithConfidence\(.*?\n.*?state\.copy\(', replacement, content, flags=re.DOTALL)

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", encoding="utf-8") as f:
    f.write(content)
