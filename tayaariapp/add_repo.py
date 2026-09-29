import codecs
with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'val revisionDao: RevisionDao' in line:
        line = line.replace('val revisionDao: RevisionDao', 'val revisionDao: RevisionDao, private val questionAttemptDao: com.example.database.QuestionAttemptDao')
    new_lines.append(line)
    if 'suspend fun logRevisionAttempt(' in line:
        # We will insert a new method right before this one
        insert = '''
    suspend fun logQuestionAttempt(
        questionId: String,
        isCorrect: Boolean,
        confidence: String?,
        timeSpentSeconds: Int,
        trapFallenInto: String?
    ) {
        val attempt = com.example.database.QuestionAttemptEntity(
            questionId = questionId,
            timestamp = System.currentTimeMillis(),
            isCorrect = isCorrect,
            confidence = confidence,
            timeSpentSeconds = timeSpentSeconds,
            trapFallenInto = trapFallenInto
        )
        questionAttemptDao.insertAttempt(attempt)
    }

'''
        new_lines.insert(-1, insert)

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
