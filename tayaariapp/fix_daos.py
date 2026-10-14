path = 'c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/java/com/example/database/Daos.kt'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'suspend fun deleteUpscQuestions()'
replacement = '@Query("DELETE FROM topics")\n    suspend fun deleteAllTopics()\n\n    ' + target
content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Added deleteAllTopics')
