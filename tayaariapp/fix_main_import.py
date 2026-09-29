import codecs
with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'import com.example.ui.screens.TopicSelectionScreen' in line:
        new_lines.append(line)
        new_lines.append('import com.example.ui.screens.InsightsDashboardScreen\n')
        continue
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
