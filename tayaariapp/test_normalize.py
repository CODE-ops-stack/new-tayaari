from v13_discovery.normalizer import DocumentNormalizer

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

normalizer = DocumentNormalizer()
blocks = normalizer.normalize('test', content[:5000])
print(f'Blocks: {len(blocks)}')
for b in blocks:
    print(f'  {b.type}: {len(b.clean_sentences)} sentences, heading: {b.metadata.get("section_heading", "None")}')
    for s in b.clean_sentences[:2]:
        print(f'  {s[:80]}...')
    print()