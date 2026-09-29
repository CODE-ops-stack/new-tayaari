import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('Text("- ", style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)', 'Text("- $report", style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)')

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
