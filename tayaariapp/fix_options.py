import os

path = 'c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/java/com/example/repository/JsonQuestionImporter.kt'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'options = gson.toJson(q.options),'
replacement = '''options = gson.toJson(q.options.map { mapEntry -> 
                        mapOf("id" to mapEntry.key, "text" to mapEntry.value)
                    }),'''

content = content.replace(target, replacement)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed JSON options structure!')
