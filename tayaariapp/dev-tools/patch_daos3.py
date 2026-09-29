with open("/app/applet/app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

import re
content = re.sub(
    r'@Query\("SELECT \* FROM questions WHERE topicId = \(SELECT id FROM topics WHERE name LIKE :topicName \|\| \'%\' LIMIT 1\) AND tier = :tier AND format = :format ORDER BY RANDOM\(\) LIMIT :limit"\)\n    @Query\("SELECT \* FROM questions WHERE topicId = \(SELECT id FROM topics WHERE name LIKE :topicName \|\| \'%\' LIMIT 1\) AND tier = :tier ORDER BY RANDOM\(\) LIMIT :limit"\)\n    suspend fun getQuestionsByTopicAndTier\(topicName: String, tier: String, limit: Int\): List<Question>\n\n    suspend fun getFewShotExamples',
    """@Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier = :tier ORDER BY RANDOM() LIMIT :limit")
    suspend fun getQuestionsByTopicAndTier(topicName: String, tier: String, limit: Int): List<Question>

    @Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier = :tier AND format = :format ORDER BY RANDOM() LIMIT :limit")
    suspend fun getFewShotExamples""",
    content
)

with open("/app/applet/app/src/main/java/com/example/database/Daos.kt", "w") as f:
    f.write(content)
