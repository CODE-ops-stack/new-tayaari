file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val examDecisionLabEngine = ExamDecisionLabEngine()', 'val examDecisionLabEngine = ExamDecisionLabEngine()\n    val falseMasteryEngine = FalseMasteryEngine(this)')

new_meth = """    suspend fun getFalseMasteryReport(): List<TransferAnalytics> {
        return falseMasteryEngine.evaluateTransfer()
    }\n\n"""

text = text.replace('    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {', new_meth + '    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
