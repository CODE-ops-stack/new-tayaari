import codecs
with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    content = f.read()

new_func = '''
    data class ConfidenceCalibrationReport(
        val overconfidenceDetected: Boolean,
        val underconfidenceDetected: Boolean,
        val overconfidenceMessage: String,
        val underconfidenceMessage: String
    )

    suspend fun getConfidenceCalibrationReport(): ConfidenceCalibrationReport? = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getConfidenceCalibration()
        if (stats.isEmpty() || stats.sumOf { it.totalAttempts } < 10) return@withContext null // Require sample size
        
        var over = false
        var under = false
        var overMsg = ""
        var underMsg = ""
        
        for (stat in stats) {
            val accuracy = stat.correctAttempts.toDouble() / stat.totalAttempts
            if (stat.selectedConfidence == "Certain" && accuracy < 0.6 && stat.totalAttempts >= 3) {
                over = true
                overMsg = "You're frequently highly confident on questions you later miss (Accuracy: \% when 'Certain')."
            }
            if ((stat.selectedConfidence == "Unsure" || stat.selectedConfidence == "Guessing") && accuracy > 0.7 && stat.totalAttempts >= 3) {
                under = true
                underMsg = "You're often unsure on questions you actually know (Accuracy: \% when '\')."
            }
        }
        
        if (!over && !under) return@withContext null
        ConfidenceCalibrationReport(over, under, overMsg, underMsg)
    }
'''

content = content.replace('    fun getAllTopics(): Flow<List<Topic>> = appDao.getAllTopics()', new_func + '\n    fun getAllTopics(): Flow<List<Topic>> = appDao.getAllTopics()')

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.write(content)
