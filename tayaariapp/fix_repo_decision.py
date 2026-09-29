file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val paperTwinEngine = PaperTwinEngine(this)', 'val paperTwinEngine = PaperTwinEngine(this)\n    val examDecisionLabEngine = ExamDecisionLabEngine()')

new_meth = """    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {
        return examDecisionLabEngine
    }\n\n"""

text = text.replace('    suspend fun getStudyPlans(): Map<Int, StudyPlan> {', new_meth + '    suspend fun getStudyPlans(): Map<Int, StudyPlan> {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
