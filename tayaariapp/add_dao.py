import codecs
with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read()

new_dao = '''
@Dao
interface QuestionAttemptDao {
    @Insert
    suspend fun insertAttempt(attempt: QuestionAttemptEntity)

    @Query("SELECT * FROM question_attempts ORDER BY timestamp DESC")
    suspend fun getAllAttempts(): List<QuestionAttemptEntity>

    @Query("SELECT * FROM question_attempts WHERE questionId = :questionId ORDER BY timestamp DESC")
    suspend fun getAttemptsForQuestion(questionId: String): List<QuestionAttemptEntity>
}
'''

content += new_dao

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content)
