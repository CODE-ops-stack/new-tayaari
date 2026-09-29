import codecs

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    'val userAnswers: Map<String, String> = emptyMap(),',
    'val userAnswers: Map<String, String> = emptyMap(),\n    val skippedQuestions: Set<String> = emptySet(),'
)
with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.write(content)
