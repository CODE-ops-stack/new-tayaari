file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val falseMasteryEngine = FalseMasteryEngine(this)', 'val falseMasteryEngine = FalseMasteryEngine(this)\n    val postTestDebriefEngine = PostTestDebriefEngine()')

new_meth = """    fun getPostTestDebriefEngine(): PostTestDebriefEngine {
        return postTestDebriefEngine
    }\n\n"""

text = text.replace('    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {', new_meth + '    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
