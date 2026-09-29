import codecs
with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'r', 'utf-8') as f:
    content = f.read()

new_entity = '''
@Entity(tableName = "question_attempts")
data class QuestionAttemptEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val questionId: String,
    val timestamp: Long,
    val isCorrect: Boolean,
    val confidence: String?, // "Certain", "Likely", "Unsure", "Guessing"
    val timeSpentSeconds: Int,
    val trapFallenInto: String?
)
'''

content += new_entity

with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'w', 'utf-8') as f:
    f.write(content)
