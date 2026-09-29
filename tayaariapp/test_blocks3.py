from v13_discovery.normalizer import DocumentNormalizer

normalizer = DocumentNormalizer()

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

# Test with first 5000 chars
sample = content[:5000]
blocks = normalizer.normalize('test', sample)
print('Blocks from sample:', len(blocks))
for b in blocks:
    print(f'  {b.type}: {len(b.clean_sentences)} sentences, heading: {b.metadata.get("section_heading", "None")}')
    for s in b.clean_sentences[:2]:
        print(f'  {s[:80]}...')
    print()

# Full content
blocks = normalizer.normalize('test', content)
print(f'Blocks from full content: {len(blocks)}')
for b in blocks[:5]:
    print(f'  {b.type}: {len(b.clean_sentences)} sentences, heading: {b.metadata.get("section_heading", "None")}')
    for s in b.clean_sentences[:2]:
        print(f'  {s[:80]}...')
    print()