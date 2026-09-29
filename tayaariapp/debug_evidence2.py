from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()

corpus_path = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt"
with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
    corpus_text = f.read()

blocks = normalizer.normalize(corpus_path, corpus_text)
raw_nodes = []
for b in blocks:
    raw_nodes.extend(extractor.extract(b))

print(f"Total nodes: {len(raw_nodes)}")

# Check the failing nodes
for i in [14, 18, 36, 52, 62, 63, 90]:
    if i < len(raw_nodes):
        node = raw_nodes[i]
        print(f"\nNode {i}:")
        print(f"  node_id: {getattr(node, 'node_id', 'N/A')}")
        print(f"  primary_entity: {getattr(node, 'primary_entity', 'N/A')}")
        print(f"  raw_evidence: {getattr(node, 'raw_evidence', 'N/A')[:120]}")
        print(f"  source_location: {getattr(node, 'source_location', 'N/A')}")