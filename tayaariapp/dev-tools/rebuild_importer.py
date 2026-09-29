import re

with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "val optA = optMatcher.group(2)" in line:
        skip = True
        new_lines.append('                    val optA = optMatcher.group(2)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""\n')
        new_lines.append('                    val optB = optMatcher.group(3)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""\n')
        new_lines.append('                    val optC = optMatcher.group(4)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""\n')
        new_lines.append('                    var optD = optMatcher.group(5)?.trim()?.replace("\\"", "\\\\\\\"")?.replace("\\n", " ") ?: ""\n')
        new_lines.append('                    \n')
        new_lines.append('                    // Manually strip "Correct Answer" from optD if present\n')
        new_lines.append('                    val caRegex = Regex("(?i)\\\\s*Correct [Aa]nswer:.*")\n')
        new_lines.append('                    optD = optD.replace(caRegex, "").trim()\n')
        new_lines.append('\n')
        new_lines.append('                    if (optD.endsWith("\\"")) {\n')
        new_lines.append('                        optD = optD.substring(0, optD.length - 1).trim()\n')
        new_lines.append('                    }\n')
        new_lines.append('                    \n')
    elif skip and "optionsStr =" in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.writelines(new_lines)
