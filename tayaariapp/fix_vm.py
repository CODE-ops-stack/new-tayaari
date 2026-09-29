import re

file = 'app/src/main/java/com/example/viewmodel/MistakeReplayViewModel.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace fun loadCandidate()
text = re.sub(
    r'fun loadCandidate\(\)\s*\{\s*viewModelScope\.launch\s*\{([\s\S]*?)\}\s*\}',
    r'fun loadCandidate() { viewModelScope.launch { loadCandidateSync() } }\n\n    suspend fun loadCandidateSync() {\1}',
    text
)

# Replace fun commitToRepair()
text = re.sub(
    r'fun commitToRepair\(\)\s*\{\s*viewModelScope\.launch\s*\{([\s\S]*?)\}\s*\}',
    r'fun commitToRepair() { viewModelScope.launch { commitToRepairSync() } }\n\n    suspend fun commitToRepairSync() {\1}',
    text
)

# Replace fun proceedToAlternate()
text = re.sub(
    r'fun proceedToAlternate\(\)\s*\{\s*viewModelScope\.launch\s*\{([\s\S]*?)\}\s*\}',
    r'fun proceedToAlternate() { viewModelScope.launch { proceedToAlternateSync() } }\n\n    suspend fun proceedToAlternateSync() {\1}',
    text
)

# Replace fun submitAlternateAnswer
text = re.sub(
    r'fun submitAlternateAnswer\(isCorrect: Boolean\)\s*\{\s*viewModelScope\.launch\s*\{([\s\S]*?)\}\s*\}',
    r'fun submitAlternateAnswer(isCorrect: Boolean) { viewModelScope.launch { submitAlternateAnswerSync(isCorrect) } }\n\n    suspend fun submitAlternateAnswerSync(isCorrect: Boolean) {\1}',
    text
)

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
