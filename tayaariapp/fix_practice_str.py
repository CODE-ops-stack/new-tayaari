import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('"You scored  out of "', '"You scored ${uiState.currentScore.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()} out of ${uiState.totalQuestionsInSet}"')

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
