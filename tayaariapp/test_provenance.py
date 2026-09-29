from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.provenance import ProvenanceTracker

# Setup
normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    corpus_text = f.read().decode('utf-8', errors='replace')

blocks = DocumentNormalizer().normalize('corpus', '')
all_nodes = []
for b in blocks:
    all_nodes.extend(extractor.extract(b))

print(f'Total nodes: {len(all_nodes)}')

synth = QuestionSynthesizer()
tracker = ProvenanceTracker()

for i, node in enumerate(all_nodes[:5]):
    cq = synth.synthesize(node)
    print(f'Node {i}: valid={cq.valid}, entity={node.primary_entity}, evidence={node.raw_evidence[:60]}...')
    if cq.valid:
        tracker.bind_candidate_question(cq, node)
        print(f'  Valid: {cq.valid}, evidence in provenance: {cq.provenance.get("evidenceText", "MISSING")[:50]}')