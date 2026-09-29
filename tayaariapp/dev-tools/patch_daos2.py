with open("/app/applet/app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

if "getQuestionsByTopicAndTier" not in content:
    content = content.replace(
        "    suspend fun getFewShotExamples",
        "    @Query(\"SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier = :tier ORDER BY RANDOM() LIMIT :limit\")\n    suspend fun getQuestionsByTopicAndTier(topicName: String, tier: String, limit: Int): List<Question>\n\n    suspend fun getFewShotExamples"
    )
    with open("/app/applet/app/src/main/java/com/example/database/Daos.kt", "w") as f:
        f.write(content)
