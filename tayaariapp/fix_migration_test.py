with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("testMigration17To18_preservesDataAndAddsColumns", "testMigration17To19_preservesDataAndAddsColumns")

# add check for confusion_events
check_code = """
        bookmarkCursor.close()
        
        val confusionCursor = roomDb.query("SELECT * FROM sqlite_master WHERE type='table' AND name='confusion_events'", null)
        assertTrue("confusion_events table should exist", confusionCursor.moveToFirst())
        confusionCursor.close()
"""
content = content.replace("bookmarkCursor.close()", check_code)

with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
