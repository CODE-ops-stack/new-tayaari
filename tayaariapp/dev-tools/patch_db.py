import re

with open("app/src/main/java/com/example/database/AppDatabase.kt", "r") as f:
    text = f.read()

new_text = text.replace("version = 3", "version = 4")

with open("app/src/main/java/com/example/database/AppDatabase.kt", "w") as f:
    f.write(new_text)
