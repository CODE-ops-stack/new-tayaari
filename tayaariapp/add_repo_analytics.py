import codecs
with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'private val questionAttemptDao: com.example.database.QuestionAttemptDao' in line:
        line = line.replace('private val questionAttemptDao: com.example.database.QuestionAttemptDao', 'private val questionAttemptDao: com.example.database.QuestionAttemptDao,\n    private val analyticsDao: com.example.database.AnalyticsDao')
    
    if 'fun getAllTopics(): Flow<List<Topic>>' in line:
        insert = '''
    suspend fun getBlindSpots(): List<com.example.database.TopicFormatStats> = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getTopicFormatStats()
        // Filter for "Fragile Knowledge": Strong in simple formats, weak in complex formats
        stats.filter { stat ->
            val simpleRate = if (stat.simpleTotal > 0) stat.simpleCorrect.toDouble() / stat.simpleTotal else 0.0
            val complexRate = if (stat.complexTotal > 0) stat.complexCorrect.toDouble() / stat.complexTotal else 0.0
            simpleRate > 0.6 && complexRate < 0.4
        }
    }
'''
        new_lines.append(insert)

    new_lines.append(line)

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.writelines(new_lines)
