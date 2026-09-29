import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'Text("Simple:' in line:
        new_lines.append('                                Text("Simple: % (/) | Complex: % (/)", \n')
    else:
        new_lines.append(line)

with codecs.open('app/src/main/java/com/example/ui/screens/InsightsDashboardScreen.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
