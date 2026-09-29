with open("app/src/main/java/com/example/database/AppDatabase.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    ".addMigrations(MIGRATION_17_18)",
    ".addMigrations(MIGRATION_17_18, MIGRATION_18_19)"
)

with open("app/src/main/java/com/example/database/AppDatabase.kt", "w", encoding="utf-8") as f:
    f.write(content)
