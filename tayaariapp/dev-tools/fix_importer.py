with open("/app/applet/app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    content = f.read()

content = content.replace(
    "- \\*\\*Specific-Exam\\*\\*: (.*?)\\n\" +\n                    \"- \\*\\*Question",
    "- \\*\\*Specific-Exam\\*\\*: (.*?)\\n\" +\n                    \"- \\*\\*PDF-Sequence-Number\\*\\*: (.*?)\\n\" +\n                    \"- \\*\\*Question"
)

with open("/app/applet/app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(content)
