
with open('app/src/main/java/com/example/repository/DataImporter.kt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# check how DataImporter regex is defined:
lines = text.splitlines()
for i, l in enumerate(lines):
    if 'qPattern' in l or (i > 50 and i < 70):
        print(f'{i+1}: {l}')
