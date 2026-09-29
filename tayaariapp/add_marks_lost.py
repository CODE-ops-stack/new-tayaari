import codecs
with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    content = f.read()

replacement = '''val allQuestions: List<ExamQuestion> = emptyList(),
    val marksLostReport: List<String> = emptyList()
)'''

content = content.replace('val allQuestions: List<ExamQuestion> = emptyList()\n)', replacement)

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.write(content)
