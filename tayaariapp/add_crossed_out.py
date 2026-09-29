import codecs
with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'val pendingOptionId: String? = null,' in line:
        new_lines.append(line)
        new_lines.append('    val crossedOutOptionIds: Set<String> = emptySet(),\n')
    else:
        new_lines.append(line)

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
