with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import com.example.database.ConfusionEventDao\nopen class LocalRepository(", "open class LocalRepository(")
content = "import com.example.database.ConfusionEventDao\n" + content

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w", encoding="utf-8") as f:
    f.write(content)
