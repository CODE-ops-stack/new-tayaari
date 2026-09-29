import re

with open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the hanging part
text = re.sub(
    r'suspend fun logConfusionEvent\(\s*pairId: String,\s*questionId: String,\s*selectedOptionText: String,\s*evidenceLevel: com.example.repository.ConfusionEvidenceLevel\s*\)\s*\{\s*withContext\(Dispatchers\.IO\)\s*\{\s*suspend fun logConfusionEvent\(',
    r'suspend fun logConfusionEvent(',
    text,
    flags=re.DOTALL
)

with open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', encoding='utf-8') as f:
    f.write(text)
