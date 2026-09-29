with open("/app/applet/app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "r") as f:
    content = f.read()

content = content.replace(
    "private val repository = GeminiRepository()",
    "private val repository = GeminiRepository(localRepository)"
)

with open("/app/applet/app/src/main/java/com/example/viewmodel/PracticeViewModel.kt", "w") as f:
    f.write(content)
