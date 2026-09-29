with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('engine.getQuestionsForProfile("All", blueprint, 10, "Paper Twin")', 'engine.getQuestionsForProfile("Global", blueprint, 10, "Paper Twin")')

content = content.replace('positiveMarks = BigDecimal.ONE,', 'positiveMarks = BigDecimal.ONE, allowedTiers = listOf("Tier 1"),')

with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
