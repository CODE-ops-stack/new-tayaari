with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import com.example.database.ConfusionEventDao\npackage com.example.repository", "package com.example.repository\nimport com.example.database.ConfusionEventDao")
content = content.replace("import com.example.database.ConfusionEventDao\nimport com.example.database.ConfusionEventDao\n", "")
if content.startswith("import com.example.database.ConfusionEventDao\n"):
    content = content[len("import com.example.database.ConfusionEventDao\n"):]

if "import com.example.database.ConfusionEventDao" not in content:
    content = content.replace("package com.example.repository", "package com.example.repository\nimport com.example.database.ConfusionEventDao")

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w", encoding="utf-8") as f:
    f.write(content)
