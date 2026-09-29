import re

with open("app/src/main/java/com/example/model/TestModels.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("val detectedConfusionPair: com.example.repository.ConfusionPair? = null", "val detectedConfusionPair: com.example.repository.ConfusionDetectionResult? = null")

with open("app/src/main/java/com/example/model/TestModels.kt", "w", encoding="utf-8") as f:
    f.write(content)
