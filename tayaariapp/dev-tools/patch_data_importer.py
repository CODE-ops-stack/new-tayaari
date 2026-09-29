import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

# Let's replace the block correctly.

new_text = re.sub(
    r'val parsedQPattern = Regex\(.*?\)\s*\{(.*?)\}',
    r'val parsedQPattern = java.util.regex.Pattern.compile(\n                        "(?s)(.*?)\\\\s*\\\\(?[aA]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[bB]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[cC]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[dD]\\\\)[ )\\\\.](.*?)\\\\s*Correct [Aa]nswer:\\\\s*(?:[Oo]ption\\\\s*)?([a-dA-D])"\n                    )\n                    val qMatcher = parsedQPattern.matcher(rawQText)\n\n                    var qText = rawQText\n                    var optionsStr = "[]"\n                    var correctAnswerStr = "A"\n\n                    if (qMatcher.find()) {\1}',
    text,
    flags=re.DOTALL
)

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(new_text)

