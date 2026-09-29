file = 'app/src/main/java/com/example/repository/PaperTwinEngine.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val actualTiers = examQuestions.groupingBy { it.tier }.eachCount()', 'val qIds = examQuestions.map { it.id.toInt() }\n        val dbQuestions = localRepository.getQuestionsByIds(qIds)\n        val actualTiers = dbQuestions.groupingBy { it.tier }.eachCount()')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
