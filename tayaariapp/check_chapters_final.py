import re

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

lines = content.split('\n')
for i, line in enumerate(content.split('\n')[:300]):
    stripped = line.strip()
    if re.match(r'^\d+\.\s+[A-Z]', stripped):
        print(f'Line {i}: {line.strip()[:80]} - HEADING')