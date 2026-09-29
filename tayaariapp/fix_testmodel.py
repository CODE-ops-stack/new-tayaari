import codecs

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    content = f.read()

replacement = '''enum class OptionRole {
    ANSWER_CHOICE,
    ABSTAIN,
    NONE_OF_ABOVE,
    MORE_THAN_ONE,
    COMBINED_NONE_OR_MORE_THAN_ONE
}

data class Option(
    val id: String,
    val text: String,
    val role: OptionRole = OptionRole.ANSWER_CHOICE
)'''

content = content.replace('data class Option(\n    val id: String,\n    val text: String\n)', replacement)

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.write(content)
