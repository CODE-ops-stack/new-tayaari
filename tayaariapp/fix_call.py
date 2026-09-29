import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'selectedOptionId = uiState.selectedOptionId,' in line and 'PremiumOptionsList(' in ''.join(lines[i-5:i]):
        lines.insert(i+1, '                                        pendingOptionId = uiState.pendingOptionId,\n')
        break

for i, line in enumerate(lines):
    if 'onOptionSelected = onOptionSelected,' in line and 'PremiumOptionsList(' in ''.join(lines[i-10:i]):
        lines.insert(i+1, '                                        onSubmitAnswerWithConfidence = onSubmitAnswerWithConfidence,\n')
        break

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'w', 'utf-8') as f:
    f.writelines(lines)
