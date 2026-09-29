import codecs

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('PYQ_REVERSE_ENGINEER("PYQ Reverse Engineer")', 'REVERSE_ENGINEER("Reverse Engineer")')
content = content.replace('PYQ_REVERSE_ENGINEER', 'REVERSE_ENGINEER')

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.write(content)
