import codecs

with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('"DB-Real-PYQ"', '"UNVERIFIED"')

with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'w', 'utf-8') as f:
    f.write(content)
