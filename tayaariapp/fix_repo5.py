import re

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("open open class LocalRepository(", "open class LocalRepository(")

target = """open class LocalRepository(
    private val bookmarkDao: BookmarkDao,
    private val trapAnalyticsDao: TrapAnalyticsDao,
    private val appDao: AppDao,
    private val revisionDao: com.example.database.RevisionDao,
    private val questionAttemptDao: com.example.database.QuestionAttemptDao,
    private val analyticsDao: com.example.database.AnalyticsDao
)"""

replacement = """open class LocalRepository(
    private val bookmarkDao: BookmarkDao,
    private val trapAnalyticsDao: TrapAnalyticsDao,
    private val appDao: AppDao,
    private val revisionDao: com.example.database.RevisionDao,
    private val questionAttemptDao: com.example.database.QuestionAttemptDao,
    private val analyticsDao: com.example.database.AnalyticsDao,
    private val confusionEventDao: com.example.database.ConfusionEventDao
)"""

content = content.replace(target, replacement)

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w", encoding="utf-8") as f:
    f.write(content)
