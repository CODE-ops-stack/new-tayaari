file = 'app/src/main/java/com/example/ui/screens/PracticeScreen.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('uiState.currentScore.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()', 'uiState.currentScore.toDisplayString()')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
