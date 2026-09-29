import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    'color = if (isCorrect) forestGreen.copy(alpha = 0.1f) else terracotta.copy(alpha = 0.1f),',
    'color = borderColor.copy(alpha = 0.1f),'
)

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
