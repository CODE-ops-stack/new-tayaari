import re
with open("app/src/main/java/com/example/repository/GeminiRepository.kt", "r") as f:
    text = f.read()

# Fix the broken JSON structure first
text = text.replace(
    '"Irrelevant Fact".\n                4. Keep the correctExplanation concise (under 3 sentences) to avoid truncation. "dissection"',
    '"Irrelevant Fact", "dissection"'
)

with open("app/src/main/java/com/example/repository/GeminiRepository.kt", "w") as f:
    f.write(text)
