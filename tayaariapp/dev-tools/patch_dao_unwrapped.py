with open("app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

new_method = """    @Query("SELECT * FROM topics ORDER BY id ASC")
    suspend fun getAllTopicsUnwrapped(): List<Topic>"""

content = content.replace("    fun getAllTopics(): Flow<List<Topic>>", "    fun getAllTopics(): Flow<List<Topic>>\n\n" + new_method)

with open("app/src/main/java/com/example/database/Daos.kt", "w") as f:
    f.write(content)
