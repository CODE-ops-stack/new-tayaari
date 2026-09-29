with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("q.id.toString()", "question.id.toString()")

with open("app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w", encoding="utf-8") as f:
    f.write(content)
