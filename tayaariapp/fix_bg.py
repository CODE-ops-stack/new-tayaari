import os

path = "app/src/main/java/com/example/ui/screens/PracticeScreen.kt"
with open(path, "r", encoding="utf-8") as file:
    content = file.read()

content = content.replace("isAnswerSubmitted && isSelected && !isCorrect && !isAbstain -> errorRed\n", "isAnswerSubmitted && isSelected && !isCorrect && !isAbstain -> errorRed.copy(alpha = 0.05f)\n")

with open(path, "w", encoding="utf-8") as file:
    file.write(content)

print("Fixed targetBgColor")
