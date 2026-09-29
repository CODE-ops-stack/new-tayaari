with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r") as f:
    content = f.read()

new_method = """    suspend fun getQuestionCountForProfile(topicName: String, profile: ExamProfile): Int = withContext(Dispatchers.IO) {
        val allowElite = profile == ExamProfile.GROUP_A
        appDao.getQuestionCountForTopicAndProfile(topicName, profile.tiers, allowElite)
    }
"""

content = content.replace(
    "    suspend fun getQuestionsForProfile",
    new_method + "\n    suspend fun getQuestionsForProfile"
)

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w") as f:
    f.write(content)
