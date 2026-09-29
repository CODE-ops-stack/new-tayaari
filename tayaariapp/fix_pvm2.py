import codecs

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    'question.timeLimitSeconds',
    '(question as? com.example.model.MCQQuestion)?.timeLimitSeconds ?: 0'
)

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
