with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("opicId", "topicId").replace("ier", "tier").replace("\x0format", "format").replace("\x0c", "f")

# Let's just rewrite the CREATE TABLE query correctly:
import re
new_query = '"CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, topicId INTEGER NOT NULL, tier TEXT NOT NULL, format TEXT NOT NULL, examRelevance TEXT NOT NULL, source TEXT NOT NULL, specificExam TEXT NOT NULL, questionText TEXT NOT NULL, options TEXT NOT NULL, correctAnswer TEXT NOT NULL, explanation TEXT NOT NULL, distractorDissections TEXT NOT NULL, imageUrl TEXT NOT NULL)"'
content = re.sub(r'"CREATE TABLE IF NOT EXISTS questions.*?\)"', new_query, content, flags=re.DOTALL)

with open("app/src/test/java/com/example/database/RealMigrationTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
