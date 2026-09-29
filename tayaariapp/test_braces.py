import re

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's count open and close braces up to FeedbackBox
idx = text.find("@Composable\nfun FeedbackBox")
text_before = text[:idx]

open_braces = text_before.count("{")
close_braces = text_before.count("}")

print(f"Before FeedbackBox: open {open_braces}, close {close_braces}")
