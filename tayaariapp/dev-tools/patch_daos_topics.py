with open("app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

if "fun getAllTopics" not in content:
    content = content.replace(
        "suspend fun insertTopics(topics: List<Topic>)",
        "suspend fun insertTopics(topics: List<Topic>)\n\n    @Query(\"SELECT * FROM topics ORDER BY id ASC\")\n    fun getAllTopics(): Flow<List<Topic>>"
    )

    with open("app/src/main/java/com/example/database/Daos.kt", "w") as f:
        f.write(content)
