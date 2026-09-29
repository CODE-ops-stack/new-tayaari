import codecs
with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'suspend fun logQuestionAttempt(' in line:
        new_lines.append('    suspend fun getRevisionItem(questionId: String): com.example.database.RevisionItemEntity? = withContext(Dispatchers.IO) {\n')
        new_lines.append('        revisionDao.getRevisionItem(questionId)\n')
        new_lines.append('    }\n\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
