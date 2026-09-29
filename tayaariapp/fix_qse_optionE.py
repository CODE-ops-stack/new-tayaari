import codecs

with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'r', 'utf-8') as f:
    content = f.read()

replacement = '''                while (parsedOptions.size > examBlueprint.optionCount) {
                    parsedOptions.removeLast()
                }
                
                // Add 5th option if blueprint demands it but question doesn't have it (e.g. BPSC)
                if (examBlueprint.optionCount == 5 && parsedOptions.size == 4) {
                    parsedOptions.add(Option(id = "opt_e", text = "None of the above / More than one of the above"))
                }'''

content = content.replace('                while (parsedOptions.size > examBlueprint.optionCount) {\n                    parsedOptions.removeLast()\n                }', replacement)

with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'w', 'utf-8') as f:
    f.write(content)
