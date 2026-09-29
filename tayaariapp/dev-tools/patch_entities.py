import re

with open("app/src/main/java/com/example/database/Entities.kt", "r") as f:
    text = f.read()

new_text = text.replace(
    "val explanation: String\n)",
    "val explanation: String,\n    val distractorDissections: String = \"[]\"\n)"
)

with open("app/src/main/java/com/example/database/Entities.kt", "w") as f:
    f.write(new_text)
