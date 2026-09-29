file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val postTestDebriefEngine = PostTestDebriefEngine()', 'val postTestDebriefEngine = PostTestDebriefEngine()\n    val pressureLadderEngine = PressureLadderEngine()')

new_meth = """    fun getPressureLadderEngine(): PressureLadderEngine {
        return pressureLadderEngine
    }\n\n"""

text = text.replace('    fun getPostTestDebriefEngine(): PostTestDebriefEngine {', new_meth + '    fun getPostTestDebriefEngine(): PostTestDebriefEngine {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
