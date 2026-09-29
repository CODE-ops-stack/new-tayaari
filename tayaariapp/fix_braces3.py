import re

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    text = f.read()

# Add missing } before FeedbackBox
text = text.replace("@Composable\nfun FeedbackBox", "}\n\n@Composable\nfun FeedbackBox")

# Remove the trailing }
text = text.rstrip()
if text.endswith("}"):
    text = text[:-1]

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")
