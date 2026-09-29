import os

path = "app/src/test/java/com/example/viewmodel/RealAppFlowRunnerTest.kt"
with open(path, "r", encoding="utf-8") as file:
    content = file.read()

content = content.replace("viewModel.startPractice(topic, blueprint, \"All\")", "viewModel.startPractice(topic, blueprint, \"All\", \"MCQ\")")

with open(path, "w", encoding="utf-8") as file:
    file.write(content)

print("Fixed RealAppFlowRunnerTest")
