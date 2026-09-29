with open("app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

new_query = """    @Query("SELECT COUNT(*) FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier IN (:allowedTiers) AND (:allowElite = 1 OR examRelevance != 'Elite')")
    suspend fun getQuestionCountForTopicAndProfile(topicName: String, allowedTiers: List<String>, allowElite: Boolean): Int
"""

content = content.replace(
    "    suspend fun getQuestionsForProfile(topicName: String, allowedTiers: List<String>, allowElite: Boolean, limit: Int): List<Question>",
    "    suspend fun getQuestionsForProfile(topicName: String, allowedTiers: List<String>, allowElite: Boolean, limit: Int): List<Question>\n\n" + new_query
)

with open("app/src/main/java/com/example/database/Daos.kt", "w") as f:
    f.write(content)
