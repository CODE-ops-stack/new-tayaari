with open("/app/applet/app/src/main/java/com/example/repository/LocalRepository.kt", "r") as f:
    content = f.read()

content = content.replace(
    "class LocalRepository(\n    private val bookmarkDao: BookmarkDao,\n    private val trapAnalyticsDao: TrapAnalyticsDao\n)",
    "import com.example.database.AppDao\nimport com.example.database.Question\n\nclass LocalRepository(\n    private val bookmarkDao: BookmarkDao,\n    private val trapAnalyticsDao: TrapAnalyticsDao,\n    private val appDao: AppDao\n)"
)

content = content.replace(
    "        } else {\n            trapAnalyticsDao.insertTrap(TrapAnalyticsEntity(trapType = trapType, frequency = 1))\n        }\n    }\n}",
    "        } else {\n            trapAnalyticsDao.insertTrap(TrapAnalyticsEntity(trapType = trapType, frequency = 1))\n        }\n    }\n\n    suspend fun getFewShotExamples(topicName: String, tier: String, format: String, limit: Int = 3): List<Question> = withContext(Dispatchers.IO) {\n        appDao.getFewShotExamples(topicName, tier, format, limit)\n    }\n}"
)

with open("/app/applet/app/src/main/java/com/example/repository/LocalRepository.kt", "w") as f:
    f.write(content)
