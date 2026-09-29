file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val timeBasedStudyPlanEngine = TimeBasedStudyPlanEngine(this)', 'val timeBasedStudyPlanEngine = TimeBasedStudyPlanEngine(this)\n    lateinit var paperTwinEngine: PaperTwinEngine')

text = text.replace('    suspend fun getStudyPlans(): Map<Int, StudyPlan> {', '    fun initPaperTwin(selectionEngine: QuestionSelectionEngine) {\n        paperTwinEngine = PaperTwinEngine(this, selectionEngine)\n    }\n\n    suspend fun getStudyPlans(): Map<Int, StudyPlan> {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
