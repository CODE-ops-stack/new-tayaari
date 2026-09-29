file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

new_meth = """    suspend fun generatePaperTwin(examId: String, targetCount: Int): GeneratedPaper {
        return paperTwinEngine.generatePaperTwin(examId, targetCount)
    }\n\n"""

text = text.replace('    suspend fun getStudyPlans(): Map<Int, StudyPlan> {', new_meth + '    suspend fun getStudyPlans(): Map<Int, StudyPlan> {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
