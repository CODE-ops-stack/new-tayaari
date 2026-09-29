with open("app/src/main/java/com/example/database/AppDatabase.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("ALTER TABLE Question ADD COLUMN", "ALTER TABLE questions ADD COLUMN")

with open("app/src/main/java/com/example/database/AppDatabase.kt", "w", encoding="utf-8") as f:
    f.write(content)
