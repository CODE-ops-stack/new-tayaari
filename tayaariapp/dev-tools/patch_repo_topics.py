with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r") as f:
    content = f.read()

if "fun getAllTopics" not in content:
    content = content.replace(
        "import com.example.database.AppDao",
        "import com.example.database.AppDao\nimport com.example.database.Topic"
    )
    content = content.replace(
        "fun getAllBookmarks(): Flow<List<BookmarkedQuestionEntity>>",
        "fun getAllTopics(): Flow<List<Topic>> = appDao.getAllTopics()\n\n    fun getAllBookmarks(): Flow<List<BookmarkedQuestionEntity>>"
    )

    with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w") as f:
        f.write(content)
