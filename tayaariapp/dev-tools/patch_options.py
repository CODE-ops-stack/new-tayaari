import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

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
                    "(?s)(.*?)\\\\s*\\\\(?[aA]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[bB]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[cC]\\\\)[ )\\\\.](.*?)\\\\s*\\\\(?[dD]\\\\)[ )\\\\.](.*?)(?:\\\\s*Correct [Aa]nswer:|$)"
                )
                val optMatcher = optionsPattern.matcher(rawQText)

                if (optMatcher.find()) {
                    qText = optMatcher.group(1)?.trim() ?: rawQText
                    val optA = optMatcher.group(2)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    val optB = optMatcher.group(3)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    val optC = optMatcher.group(4)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    var optD = optMatcher.group(5)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""
                    if (optD.endsWith("\\"")) {
                        optD = optD.substring(0, optD.length - 1).trim()
                    }
                    
                    optionsStr = "[{\\"id\\":\\"opt_a\\",\\"text\\":\\"" + optA + "\\"},{\\"id\\":\\"opt_b\\",\\"text\\":\\"" + optB + "\\"},{\\"id\\":\\"opt_c\\",\\"text\\":\\"" + optC + "\\"},{\\"id\\":\\"opt_d\\",\\"text\\":\\"" + optD + "\\"}]"
                }"""

# Need to find the exact block to replace
old_block = """                val parsedQPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)\\s*Correct [Aa]nswer:\\s*(?:[Oo]ption\\s*)?([a-dA-D])"
                )
                val qMatcher = parsedQPattern.matcher(rawQText)
                var qText = rawQText
                var optionsStr = "[]"
                var correctAnswerStr = "A"
                var distractorJson = "[]"
                
                if (trapType.isNotEmpty()) {
                    distractorJson = "[{\\"optionId\\":\\"opt_distractor\\",\\"trapType\\":\\"$trapType\\",\\"dissection\\":\\"Parsed from md\\"}]"
                }

                if (qMatcher.find()) {
                    qText = qMatcher.group(1)?.trim() ?: rawQText
                    val optA = qMatcher.group(2)?.trim()?.replace("\\"", "\\\\\\\"") ?: ""
                    val optB = qMatcher.group(3)?.trim()?.replace("\\"", "\\\\\\\"") ?: ""
                    val optC = qMatcher.group(4)?.trim()?.replace("\\"", "\\\\\\\"") ?: ""
                    val optD = qMatcher.group(5)?.trim()?.replace("\\"", "\\\\\\\"") ?: ""
                    
                    optionsStr = "[{\\"id\\":\\"opt_a\\",\\"text\\":\\"" + optA + "\\"},{\\"id\\":\\"opt_b\\",\\"text\\":\\"" + optB + "\\"},{\\"id\\":\\"opt_c\\",\\"text\\":\\"" + optC + "\\"},{\\"id\\":\\"opt_d\\",\\"text\\":\\"" + optD + "\\"}]"
                    
                    val ansLetter = qMatcher.group(6)?.lowercase()?.trim() ?: "a"
                    correctAnswerStr = "opt_" + ansLetter
                }"""

text = text.replace(old_block, replacement)

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(text)
