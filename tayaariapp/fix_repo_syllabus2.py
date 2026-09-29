file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

new_meth = """    suspend fun getSyllabusMap(): List<SyllabusTopicNode> {
        return syllabusEngine.getSyllabusMap()
    }\n\n"""

text = text.replace('    suspend fun getLearnerProfile(): com.example.repository.LearnerProfile {', new_meth + '    suspend fun getLearnerProfile(): com.example.repository.LearnerProfile {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
