import codecs
with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read()

new_dao = '''
data class TopicFormatStats(
    val topicId: Int,
    val topicName: String,
    val simpleCorrect: Int,
    val simpleTotal: Int,
    val complexCorrect: Int,
    val complexTotal: Int
)

@Dao
interface AnalyticsDao {
    @Query("""
        SELECT q.topicId, 
               t.name as topicName,
               SUM(CASE WHEN q.format IN ('Direct Fact', 'Matching') AND qa.isCorrect THEN 1 ELSE 0 END) as simpleCorrect,
               SUM(CASE WHEN q.format IN ('Direct Fact', 'Matching') THEN 1 ELSE 0 END) as simpleTotal,
               SUM(CASE WHEN q.format IN ('Assertion-Reason', 'Statement-based') AND qa.isCorrect THEN 1 ELSE 0 END) as complexCorrect,
               SUM(CASE WHEN q.format IN ('Assertion-Reason', 'Statement-based') THEN 1 ELSE 0 END) as complexTotal
        FROM question_attempts qa
        INNER JOIN questions q ON qa.questionId = CAST(q.id AS TEXT)
        INNER JOIN topics t ON q.topicId = t.id
        GROUP BY q.topicId
        HAVING simpleTotal > 0 AND complexTotal > 0
    """)
    suspend fun getTopicFormatStats(): List<TopicFormatStats>
}
'''

content += new_dao

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content)
