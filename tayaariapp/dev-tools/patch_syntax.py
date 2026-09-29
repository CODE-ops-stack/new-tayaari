import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

# Fix the broken lines
new_text = text.replace('val optA = optMatcher.group(2)?.trim()?.replace("\\"", "\\"")?.replace("\\n", " ") ?: ""', 'val optA = optMatcher.group(2)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\\\n", " ") ?: ""')
new_text = new_text.replace('val optB = optMatcher.group(3)?.trim()?.replace("\\"", "\\"")?.replace("\\n", " ") ?: ""', 'val optB = optMatcher.group(3)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\\\n", " ") ?: ""')
new_text = new_text.replace('val optC = optMatcher.group(4)?.trim()?.replace("\\"", "\\"")?.replace("\\n", " ") ?: ""', 'val optC = optMatcher.group(4)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\\\n", " ") ?: ""')
new_text = new_text.replace('var optD = optMatcher.group(5)?.trim()?.replace("\\"", "\\"")?.replace("\\n", " ") ?: ""', 'var optD = optMatcher.group(5)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\\\n", " ") ?: ""')

new_text = new_text.replace('val caRegex = Regex("(?i)\\s*Correct [Aa]nswer:.*")', 'val caRegex = Regex("(?i)\\\\s*Correct [Aa]nswer:.*")')

# Wait, my previous python replaced literal newlines, let's just do a blanket regex replace of the whole block

bad_block = re.compile(r"val optA = optMatcher\.group\(2\).*?optionsStr = ", re.DOTALL)

good_block = r"""val optA = optMatcher.group(2)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                    val optB = optMatcher.group(3)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                    val optC = optMatcher.group(4)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                    var optD = optMatcher.group(5)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                    
                    // Manually strip "Correct Answer" from optD if present
                    val caRegex = Regex("(?i)\\s*Correct [Aa]nswer:.*")
                    optD = optD.replace(caRegex, "").trim()

                    if (optD.endsWith("\"")) {
                        optD = optD.substring(0, optD.length - 1).trim()
                    }
                    
                    optionsStr = """

new_text = bad_block.sub(good_block, text)

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(new_text)
