import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

bad_block = """                val ansMatcher = java.util.regex.Pattern.compile("(?i)Correct [Aa]nswer:\s*(?:Option\s*)?([a-d])").matcher(rawQText)
                if (ansMatcher.find()) {
                    correctAnswerStr = "opt_" + ansMatcher.group(1).lowercase().trim()
                }

                val optionsPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\s*\(?[aA]\)[ )\.](.*?)\s*\(?[bB]\)[ )\.](.*?)\s*\(?[cC]\)[ )\.](.*?)\s*\(?[dD]\)[ )\.](.*)"
                )"""

good_block = """                val ansMatcher = java.util.regex.Pattern.compile("(?i)Correct [Aa]nswer:\\\\s*(?:Option\\\\s*)?([a-d])").matcher(rawQText)
                if (ansMatcher.find()) {
                    correctAnswerStr = "opt_" + ansMatcher.group(1).lowercase().trim()
                }

                val optionsPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\\\\s*\\\\(?[aA]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[bB]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[cC]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[dD]\\\\)[ )\\\\.](.*)"
                )"""

if bad_block in text:
    print("Found exact block, replacing!")
    text = text.replace(bad_block, good_block)
else:
    print("Did not find exact block!")

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(text)
