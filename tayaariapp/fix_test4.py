import re

with open("app/src/test/java/com/example/repository/FamilyProgressionAndMigrationTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r'FamilyAttemptRecord\("F1", "STANDARD", 101, "INCORRECT", System.currentTimeMillis\(\)\)', r'FamilyAttemptRecord("F1", "STANDARD", "INCORRECT", System.currentTimeMillis(), 101)', content)
content = re.sub(r'FamilyAttemptRecord\("F2", "FOUNDATION", 102, "INCORRECT", System.currentTimeMillis\(\)\)', r'FamilyAttemptRecord("F2", "FOUNDATION", "INCORRECT", System.currentTimeMillis(), 102)', content)
content = re.sub(r'FamilyAttemptRecord\("F1", "STANDARD", 101, "CORRECT", System.currentTimeMillis\(\)\)', r'FamilyAttemptRecord("F1", "STANDARD", "CORRECT", System.currentTimeMillis(), 101)', content)

with open("app/src/test/java/com/example/repository/FamilyProgressionAndMigrationTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
