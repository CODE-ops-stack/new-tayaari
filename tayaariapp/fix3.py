import os

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    text = f.read()

# add missing }
if text.strip()[-1] == '}':
    text = text + "\n}"
else:
    text = text + "\n}"

# add import
if "import androidx.compose.material.icons.filled.Lightbulb" not in text:
    text = text.replace("import androidx.compose.material.icons.filled.WarningAmber\n", "import androidx.compose.material.icons.filled.WarningAmber\nimport androidx.compose.material.icons.filled.Lightbulb\n")

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed")
