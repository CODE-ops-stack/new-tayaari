import codecs
import re

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read()

content = re.sub(r'@Insert\(onConflict = OnConflictStrategy.REPLACE\)\s*suspend fun insertExamProfiles\(profiles: List<ExamProfile>\)', '', content)
content = re.sub(r'@Query\("SELECT \* FROM exam_profiles"\)\s*suspend fun getAllExamProfiles\(\): List<ExamProfile>', '', content)

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content)
