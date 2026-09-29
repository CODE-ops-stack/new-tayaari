import re

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

lines = content.split('\n')
for i, line in enumerate(lines[:300]):
    stripped = line.strip()
    if re.match(r'^\d+\.\s+[A-Z]', stripped):
        print(f'Line {i}: {stripped[:80]} - HEADING')
    elif line.strip() and len(line.strip()) < 120:
        from v13_discovery.normalizer import LayoutDesegmenter
        is_h = LayoutDesegmenter.is_heading(stripped)
        if is_h:
            print(f'Line {i}: {line.strip()[:80]} - HEADING')