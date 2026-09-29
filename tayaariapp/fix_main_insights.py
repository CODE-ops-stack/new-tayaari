import codecs
with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'composable("topic_selection") {' in line:
        new_lines.append(line)
        continue
    
    if 'TopicSelectionScreen(' in line and 'navController = navController' in lines[i-1]:
        new_lines.append(line)
        new_lines.append('                        onInsightsClick = { navController.navigate("insights") },\n')
        continue

    if 'composable("bookmarks") {' in line:
        insert = '''
                composable("insights") {
                    InsightsDashboardScreen(
                        localRepository = localRepository,
                        onBack = { navController.popBackStack() }
                    )
                }
'''
        new_lines.append(insert)
        new_lines.append(line)
        continue
        
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
