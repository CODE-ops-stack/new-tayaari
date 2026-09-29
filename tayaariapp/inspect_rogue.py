import codecs
import re

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    daos_content = f.read()
print("Daos.kt length:", len(daos_content))

with codecs.open('app/src/main/java/com/example/model/TestModels.kt', 'r', 'utf-8') as f:
    models_content = f.read()
print("TestModels.kt length:", len(models_content))

with codecs.open('app/src/main/java/com/example/database/Entities.kt', 'r', 'utf-8') as f:
    entities_content = f.read()
print("Entities.kt length:", len(entities_content))

