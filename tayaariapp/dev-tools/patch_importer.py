import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

# Replace everything from `val parsedQPattern` to `questions.add(Question(`
pattern_to_find = re.compile(r"val parsedQPattern.*?questions\.add\(Question\(", re.DOTALL)

replacement = """                var qText = rawQText
                var optionsStr = "[]"
                var correctAnswerStr = "opt_a"
                var distractorJson = "[]"
                
                if (trapType.isNotEmpty()) {
                    distractorJson = "[{\\"optionId\\":\\"opt_distractor\\",\\"trapType\\":\\"$trapType\\",\\"dissection\\":\\"Parsed from md\\"}]"
                }

                val ansMatcher = java.util.regex.Pattern.compile("(?i)Correct [Aa]nswer:\\\\s*(?:Option\\\\s*)?([a-d])").matcher(rawQText)
                if (ansMatcher.find()) {
                    correctAnswerStr = "opt_" + ansMatcher.group(1).lowercase().trim()
                }

                val optionsPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\\\\s*\\\\(?[aA]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[bB]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[cC]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[dD]\\\\)[ )\\\\.](.*)"
                )
                val optMatcher = optionsPattern.matcher(rawQText)

                if (optMatcher.find()) {
                    qText = optMatcher.group(1)?.trim() ?: rawQText
                    val optA = optMatcher.group(2)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    val optB = optMatcher.group(3)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    val optC = optMatcher.group(4)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    var optD = optMatcher.group(5)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    
                    // Manually strip "Correct Answer" from optD if present
                    val caRegex = Regex("(?i)\\\\s*Correct [Aa]nswer:.*")
                    optD = optD.replace(caRegex, "").trim()

                    if (optD.endsWith("\\"")) {
                        optD = optD.substring(0, optD.length - 1).trim()
                    }
                    
                    optionsStr = "[{\\"id\\":\\"opt_a\\",\\"text\\":\\"" + optA + "\\"},{\\"id\\":\\"opt_b\\",\\"text\\":\\"" + optB + "\\"},{\\"id\\":\\"opt_c\\",\\"text\\":\\"" + optC + "\\"},{\\"id\\":\\"opt_d\\",\\"text\\":\\"" + optD + "\\"}]"
                }
                
                questions.add(Question("""

new_text, count = pattern_to_find.subn(replacement, text)
print(f"Replaced {count} instances.")

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(new_text)
