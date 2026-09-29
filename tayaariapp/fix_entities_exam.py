import codecs
import re

with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'r', 'utf-8') as f:
    content = f.read()

# Remove ExamProfile data class
content = re.sub(r'@Entity\(tableName = "exam_profiles"\)\s*data class ExamProfile\(\s*@PrimaryKey val name: String,\s*val allowedTiers: String.*?\)', '', content, flags=re.DOTALL)

with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'w', 'utf-8') as f:
    f.write(content)
