file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    fun getPressureLadderEngine(): PressureLadderEngine {\n        return pressureLadderEngine\n    }\n\n', '')
text = text.replace('    fun getPostTestDebriefEngine(): PostTestDebriefEngine {\n        return postTestDebriefEngine\n    }\n\n', '')
text = text.replace('    fun getExamDecisionLabEngine(): ExamDecisionLabEngine {\n        return examDecisionLabEngine\n    }\n\n', '')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
