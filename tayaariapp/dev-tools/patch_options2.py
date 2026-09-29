import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

replacement = """                val optionsPattern = java.util.regex.Pattern.compile(
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
                }"""

old_block = """                val optionsPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)(?:\\s*Correct [Aa]nswer:|$)"
                )
                val optMatcher = optionsPattern.matcher(rawQText)

                if (optMatcher.find()) {
                    qText = optMatcher.group(1)?.trim() ?: rawQText
                    val optA = optMatcher.group(2)?.trim()?.replace("\"", "\\\"")?.replace("\\n", " ") ?: ""
                    val optB = optMatcher.group(3)?.trim()?.replace("\"", "\\\"")?.replace("\\n", " ") ?: ""
                    val optC = optMatcher.group(4)?.trim()?.replace("\"", "\\\"")?.replace("\\n", " ") ?: ""
                    var optD = optMatcher.group(5)?.trim()?.replace("\"", "\\\"")?.replace("\\n", " ") ?: ""
                    if (optD.endsWith("\"")) {
                        optD = optD.substring(0, optD.length - 1).trim()
                    }
                    
                    optionsStr = "[{\"id\":\"opt_a\",\"text\":\"" + optA + "\"},{\"id\":\"opt_b\",\"text\":\"" + optB + "\"},{\"id\":\"opt_c\",\"text\":\"" + optC + "\"},{\"id\":\"opt_d\",\"text\":\"" + optD + "\"}]"
                }"""

text = text.replace(old_block, replacement)

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(text)
