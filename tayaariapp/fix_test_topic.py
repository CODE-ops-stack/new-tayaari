file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

import1 = 'import com.example.database.Topic'
if import1 not in text:
    text = text.replace('import com.example.database.Question', import1 + '\nimport com.example.database.Question')

# Insert the topic before db.appDao().insertQuestions
insert_stmt = 'db.appDao().insertTopics(listOf(Topic(id = 1, name = "1", source = "Mock")))\n        '
text = text.replace('db.appDao().insertQuestions', insert_stmt + 'db.appDao().insertQuestions')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
