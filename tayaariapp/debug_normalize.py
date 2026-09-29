from v13_discovery.normalizer import DocumentNormalizer
import re

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

# Debug: check headings
lines = content.split('\n')
heading_count = 0
for i, line in enumerate(content.split('\n')[:300]):
    stripped = line.strip()
    if re.match(r'^\d+\.\s+[A-Z]', stripped):
        print(f'Line {i}: {line.strip()[:80]} - HEADING')

# Test normalizer
normalizer = DocumentNormalizer()
blocks = normalizer.normalize('test', content)
print(f'Blocks: {len(blocks)}')
for b in blocks[:5]:
    print(f'  {b.type}: {len(b.clean_sentences)} sentences, heading: {b.metadata.get("section_heading", "None")}')
    for s in b.clean_sentences[:2]:
        print(f'  {s[:80]}...')
    print()