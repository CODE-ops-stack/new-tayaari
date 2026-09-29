import codecs
with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('database.appDao(), database.revisionDao()) }', 'database.appDao(), database.revisionDao(), database.questionAttemptDao()) }')

with codecs.open('app/src/main/java/com/example/MainActivity.kt', 'w', 'utf-8') as f:
    f.write(content)
