import codecs
with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("ExamProfile::class, ", "")

with codecs.open('app/src/main/java/com/example/database/AppDatabase.kt', 'w', 'utf-8') as f:
    f.write(content)
