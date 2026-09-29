file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    lateinit var paperTwinEngine: PaperTwinEngine\n', '    val paperTwinEngine = PaperTwinEngine(this)\n')
text = text.replace('    fun initPaperTwin(selectionEngine: QuestionSelectionEngine) {\n        paperTwinEngine = PaperTwinEngine(this, selectionEngine)\n    }\n', '')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
