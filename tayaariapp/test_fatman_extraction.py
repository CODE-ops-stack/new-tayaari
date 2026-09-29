from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
import fitz

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()

doc = fitz.open('source-material/fatman Geography 2nd Edition_Part1 new.pdf')
print(f'Pages: {doc.page_count}')

# Read the PDF content
with open('source-material/fatman Geography 2nd Edition_Part1 new.pdf', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

blocks = normalizer.normalize('fatman_part1.pdf', content)
print(f'Normalized blocks: {len(blocks)}')

for b in blocks[:5]:
    print(f'  Block: {b.type}, sentences: {len(b.clean_sentences)}')
    for s in b.clean_sentences[:2]:
        print(f'  Sentence: {s[:100]}...')

# Extract nodes
all_nodes = []
for b in blocks:
    all_nodes.extend(extractor.extract(b))

print(f'Total nodes extracted: {len(all_nodes)}')
for n in all_nodes[:3]:
    print(f'  Entity: {n.primary_entity}, Intent: {n.intent_type}, Predicate: {n.predicate[:80]}...')