import re

with open("app/src/main/java/com/example/database/AppDatabase.kt", "r", encoding="utf-8") as f:
    content = f.read()

# Add to entities
content = content.replace(
    "entities = [BookmarkedQuestionEntity::class, TrapAnalyticsEntity::class, Topic::class, Question::class, TestSession::class, RevisionItemEntity::class, QuestionAttemptEntity::class]",
    "entities = [BookmarkedQuestionEntity::class, TrapAnalyticsEntity::class, Topic::class, Question::class, TestSession::class, RevisionItemEntity::class, QuestionAttemptEntity::class, ConfusionEventEntity::class]"
)

# Bump version
content = content.replace("version = 18", "version = 19")

# Add DAO
dao_str = "    abstract fun bookmarkDao(): BookmarkDao\n    abstract fun confusionEventDao(): ConfusionEventDao"
content = content.replace("    abstract fun bookmarkDao(): BookmarkDao", dao_str)

# Add MIGRATION_18_19
migration_18_19 = """        val MIGRATION_18_19 = object : Migration(18, 19) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("CREATE TABLE IF NOT EXISTS `confusion_events` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `pairId` TEXT NOT NULL, `questionId` TEXT NOT NULL, `selectedOptionText` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `evidenceLevel` TEXT NOT NULL)")
            }
        }"""

content = content.replace("val MIGRATION_17_18 = object", migration_18_19 + "\n\n        val MIGRATION_17_18 = object")

with open("app/src/main/java/com/example/database/AppDatabase.kt", "w", encoding="utf-8") as f:
    f.write(content)
