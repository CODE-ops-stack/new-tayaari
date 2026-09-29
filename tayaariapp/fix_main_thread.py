with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('.addMigrations(AppDatabase.MIGRATION_17_18)', '.addMigrations(AppDatabase.MIGRATION_17_18)\n            .allowMainThreadQueries()')

with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
