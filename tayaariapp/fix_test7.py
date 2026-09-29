with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("val formatCounts: Map<String, Int> = selected.map { (it as Question).format }.groupingBy { it }.eachCount()", "val formatCounts: Map<String, Int> = selected.map { (it as MCQQuestion).questionFormatType }.groupingBy { it }.eachCount()")

with open("app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt", "w", encoding="utf-8") as f:
    f.write(content)
