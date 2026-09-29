import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    'import androidx.compose.material.icons.filled.Cancel',
    'import androidx.compose.material.icons.filled.Cancel\nimport androidx.compose.material.icons.filled.RemoveCircleOutline'
)

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
