file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val syllabusEngine = SyllabusEngine(this)', 'val syllabusEngine = SyllabusEngine(this)\n    val timeBasedStudyPlanEngine = TimeBasedStudyPlanEngine(this)')

new_meth = """    suspend fun getStudyPlans(): Map<Int, StudyPlan> {
        return timeBasedStudyPlanEngine.generatePlans()
    }\n\n"""

text = text.replace('    suspend fun getSyllabusMap(): List<SyllabusTopicNode> {', new_meth + '    suspend fun getSyllabusMap(): List<SyllabusTopicNode> {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
