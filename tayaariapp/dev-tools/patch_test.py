with open("app/src/test/java/com/example/viewmodel/MainViewModelTest.kt", "r") as f:
    content = f.read()

content = content.replace("kotlinx.coroutines.delay(100)", "kotlinx.coroutines.delay(1000)")

with open("app/src/test/java/com/example/viewmodel/MainViewModelTest.kt", "w") as f:
    f.write(content)
