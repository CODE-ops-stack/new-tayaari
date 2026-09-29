import os

path = "app/src/test/java/com/example/database/RealMigrationTest.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the migrations being added
content = content.replace(
    ".addMigrations(AppDatabase.MIGRATION_17_18, AppDatabase.MIGRATION_18_19, AppDatabase.MIGRATION_19_20)",
    ".addMigrations(AppDatabase.MIGRATION_17_18, AppDatabase.MIGRATION_18_19, AppDatabase.MIGRATION_19_20, AppDatabase.MIGRATION_20_21)"
)

# 2. Insert test data for topics before closing rawDb
topics_insert = """rawDb.execSQL(
            "INSERT INTO `topics` (`id`, `name`, `source`) VALUES (1, 'Test Topic', 'Test Source')"
        )
        rawDb.close()"""
content = content.replace("rawDb.close()", topics_insert)

# 3. Add assertions for topics at the end
topics_verify = """
        val topicCursor = roomDb.query("SELECT * FROM topics WHERE id = 1", null)
        assertTrue("Topic record should exist", topicCursor.moveToFirst())
        
        val moduleIndex = topicCursor.getColumnIndex("module")
        assertTrue("module column should exist", moduleIndex != -1)
        assertEquals("Miscellaneous Topics", topicCursor.getString(moduleIndex))
        assertEquals("Test Topic", topicCursor.getString(topicCursor.getColumnIndexOrThrow("name")))
        topicCursor.close()

        roomDb.close()"""
content = content.replace("roomDb.close()", topics_verify)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched RealMigrationTest.kt successfully")
