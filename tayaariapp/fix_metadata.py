with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('rawDb.execSQL("CREATE TABLE android_metadata (locale TEXT)")', '')

with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
