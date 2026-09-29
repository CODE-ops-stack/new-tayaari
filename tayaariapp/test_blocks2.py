from v13_discovery.normalizer import DocumentNormalizer

normalizer = DocumentNormalizer()

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

blocks = DocumentNormalizer().normalize('corpus', '')
print('Blocks:', len(blocks))
for b in blocks[:3]:
    print('  Type:', b.type, 'sentences:', len(b.clean_sentences), 'heading:', b.metadata.get('section_heading', 'None'))
    for s in b.clean_sentences[:2]:
        print('  ', s[:80], '...')
    print()