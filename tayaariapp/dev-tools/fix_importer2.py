import re
with open("/app/applet/app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    content = f.read()

content = re.sub(
    r'- \\\*\\\*Specific-Exam\\\*\\\*: \(\.\*\?\)\\n"\s*\+\s*"- \\\*\\\*Question',
    r'- \\*\\*Specific-Exam\\*\\*: (.*?)\\n" +\n                    "- \\*\\*PDF-Sequence-Number\\*\\*: (.*?)\\n" +\n                    "- \\*\\*Question',
    content
)

with open("/app/applet/app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(content)
