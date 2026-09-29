import re

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

lines = content.split('\n')
heading_count = 0
for i, line in enumerate(content.split('\n')[:300]):
    stripped = line.strip()
    if re.match(r'^\d+\.\s+[A-Z]', stripped):
        print(f'Line {i}: {line.strip()[:80]} - is_heading: True')

print(f'Total headings found: {sum(1 for l in content.split("\n")[:300] if re.match(r"^\d+\.\s+[A-Z]", l.strip()))}')