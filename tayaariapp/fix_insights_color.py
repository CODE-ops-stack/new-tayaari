import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'import com.example.ui.theme.deepBlue' in line or 'import com.example.ui.theme.lightBackground' in line:
        continue
    line = line.replace('deepBlue', 'MaterialTheme.colorScheme.primary')
    line = line.replace('lightBackground', 'MaterialTheme.colorScheme.background')
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
