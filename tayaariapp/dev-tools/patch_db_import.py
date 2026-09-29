import re

with open('app/src/main/java/com/example/database/AppDatabase.kt', 'r') as f:
    content = f.read()

if "import kotlinx.coroutines.launch" not in content:
    content = content.replace("import androidx.room.RoomDatabase", "import androidx.room.RoomDatabase\nimport kotlinx.coroutines.launch")

with open('app/src/main/java/com/example/database/AppDatabase.kt', 'w') as f:
    f.write(content)
