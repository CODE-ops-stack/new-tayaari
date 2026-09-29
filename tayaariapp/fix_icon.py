import os

path = "app/src/main/java/com/example/ui/screens/PracticeScreen.kt"
with open(path, "r", encoding="utf-8") as file:
    content = file.read()

content = content.replace(
    "} else if (isSelected && isAbstain) {\n                                // no icon for abstain\n                                Icon(Icons.Filled.HighlightOff, tint = errorRed, contentDescription = \"Incorrect\")",
    "} else if (isSelected && isAbstain) {\n                                // no icon for abstain"
)

with open(path, "w", encoding="utf-8") as file:
    file.write(content)

print("Fixed icon logic")
