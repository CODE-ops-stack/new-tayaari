import codecs
with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read()

new_dao = '''
data class ConfidenceCalibrationStats(
    val selectedConfidence: String,
    val totalAttempts: Int,
    val correctAttempts: Int
)

'''

content = content.replace('@Dao\ninterface AnalyticsDao {', new_dao + '@Dao\ninterface AnalyticsDao {\n    @Query("SELECT selectedConfidence, COUNT(*) as totalAttempts, SUM(CASE WHEN isCorrect THEN 1 ELSE 0 END) as correctAttempts FROM question_attempts WHERE selectedConfidence != \'None\' GROUP BY selectedConfidence")\n    suspend fun getConfidenceCalibration(): List<ConfidenceCalibrationStats>\n')

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content)
