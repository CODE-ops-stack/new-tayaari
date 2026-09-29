import codecs
import re

# 1. TestModels.kt
with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    content = f.read().replace('\r\n', '\n')
    
if 'enum class AttemptOutcome' not in content:
    content += '\n\nenum class AttemptOutcome {\n    CORRECT, INCORRECT, ABSTAINED, UNANSWERED\n}\n'
with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'w', 'utf-8') as f:
    f.write(content.replace('\n', '\r\n'))

# 2. Entities.kt
with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'r', 'utf-8') as f:
    content = f.read().replace('\r\n', '\n')
content = content.replace('val isCorrect: Boolean,', 'val outcome: String,')
with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'w', 'utf-8') as f:
    f.write(content.replace('\n', '\r\n'))

# 3. Daos.kt
with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read().replace('\r\n', '\n')
content = content.replace('COUNT(*) as totalAttempts', "SUM(CASE WHEN outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as totalAttempts")
content = content.replace('SUM(CASE WHEN isCorrect THEN 1 ELSE 0 END)', "SUM(CASE WHEN outcome = 'CORRECT' THEN 1 ELSE 0 END)")
content = content.replace('qa.isCorrect', "qa.outcome = 'CORRECT'")
content = content.replace("AND qa.outcome = 'CORRECT' THEN 1 ELSE 0 END) as simpleTotal", "AND qa.outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as simpleTotal")
content = content.replace("THEN 1 ELSE 0 END) as simpleTotal", "AND qa.outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as simpleTotal")
content = content.replace("THEN 1 ELSE 0 END) as complexTotal", "AND qa.outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as complexTotal")
# ensure it didn't get double replaced
content = content.replace("AND qa.outcome IN ('CORRECT', 'INCORRECT') AND qa.outcome IN ('CORRECT', 'INCORRECT')", "AND qa.outcome IN ('CORRECT', 'INCORRECT')")

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content.replace('\n', '\r\n'))

