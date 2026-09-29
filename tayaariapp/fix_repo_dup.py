file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    private val revisionDao: com.example.database.RevisionDao,\n', '', 1)

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
