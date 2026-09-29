with open("app/src/main/java/com/example/MainActivity.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), database.appDao(), database.revisionDao(), database.questionAttemptDao(), database.analyticsDao())",
    "LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), database.appDao(), database.revisionDao(), database.questionAttemptDao(), database.analyticsDao(), database.confusionEventDao())"
)

with open("app/src/main/java/com/example/MainActivity.kt", "w", encoding="utf-8") as f:
    f.write(content)
