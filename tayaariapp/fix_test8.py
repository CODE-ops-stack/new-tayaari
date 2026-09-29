with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('assertTrue("Should have Statement-based questions", formatCounts.containsKey("Statement-based"))', 'println("Format counts: $formatCounts")\n        assertTrue("Should have Statement-based questions", formatCounts.containsKey("Statement-based"))')

with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
