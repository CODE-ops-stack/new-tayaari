import codecs
with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'abstract fun questionAttemptDao(): QuestionAttemptDao' in line:
        new_lines.append(line)
        new_lines.append('    abstract fun analyticsDao(): AnalyticsDao\n')
        continue
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
