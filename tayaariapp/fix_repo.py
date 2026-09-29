file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val mistakeReplayEngine = MistakeReplayEngine(mistakeReplayDao, trapAnalyticsDao, confusionEventDao, questionAttemptDao, appDao, revisionDao)\n', 'val mistakeReplayEngine = MistakeReplayEngine(mistakeReplayDao, trapAnalyticsDao, confusionEventDao, questionAttemptDao, appDao, revisionDao)\n    val learnerModelEngine = LearnerModelEngine(appDao, questionAttemptDao, revisionDao, trapAnalyticsDao, confusionEventDao, analyticsDao)\n')

new_meth = """    suspend fun getLearnerProfile(): com.example.repository.LearnerProfile {
        return learnerModelEngine.getLearnerProfile()
    }\n\n"""

text = text.replace('    suspend fun getBlindSpots(): List<BlindSpotDetail> = withContext(Dispatchers.IO) {', new_meth + '    suspend fun getBlindSpots(): List<BlindSpotDetail> = withContext(Dispatchers.IO) {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
