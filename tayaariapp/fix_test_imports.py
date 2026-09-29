file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove duplicate imports by splitting to lines, using a set for imports, then rejoining
lines = text.split('\n')
new_lines = []
seen_imports = set()
for line in lines:
    if line.startswith('import '):
        if line in seen_imports:
            continue
        seen_imports.add(line)
    new_lines.append(line)

with open(file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
