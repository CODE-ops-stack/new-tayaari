import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'fun TopicSelectionScreen(' in line:
        new_lines.append(line)
        new_lines.append('    onInsightsClick: () -> Unit = {},\n')
        continue
    
    if 'import androidx.compose.foundation.layout.*' in line:
        new_lines.append(line)
        new_lines.append('import androidx.compose.material.icons.filled.Lightbulb\n')
        continue

    if 'DashboardActionCard(' in line and 'icon = Icons.Default.Warning,' in lines[i+2]:
        insert = '''
                DashboardActionCard(
                    title = "Insights",
                    subtitle = "Blind-Spots",
                    icon = Icons.Default.Lightbulb,
                    onClick = onInsightsClick
                )
'''
        new_lines.append(insert)
        new_lines.append(line)
        continue

    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
