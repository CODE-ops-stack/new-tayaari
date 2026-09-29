import codecs
with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '@Database(entities =' in line:
        line = line.replace('RevisionItemEntity::class]', 'RevisionItemEntity::class, QuestionAttemptEntity::class]')
    if 'version = 16' in line:
        line = line.replace('version = 16', 'version = 17')
    if 'abstract fun revisionDao(): RevisionDao' in line:
        new_lines.append(line)
        new_lines.append('    abstract fun questionAttemptDao(): QuestionAttemptDao\n')
        continue
    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
