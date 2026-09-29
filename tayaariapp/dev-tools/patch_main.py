with open("/app/applet/app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

content = content.replace(
    "LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao())",
    "LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), database.appDao())"
)

with open("/app/applet/app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
