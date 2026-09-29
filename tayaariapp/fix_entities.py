import os

path = "app/src/main/java/com/example/database/Entities.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the accidental line from Question class
bad_line = '    val module: String = "Miscellaneous Topics",\n'
if "val source: String,\n" + bad_line in content:
    # Only replace the one in Question class
    # The topic one is: 'val source: String,\n    val module: String = "Miscellaneous Topics"\n' (without trailing comma)
    content = content.replace("val source: String,\n" + bad_line, "val source: String,\n")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed Entities.kt")
