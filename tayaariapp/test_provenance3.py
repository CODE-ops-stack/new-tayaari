from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.provenance import verify_provenance_chain

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()

with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    corpus_text = f.read().decode('utf-8', errors='replace')

blocks = DocumentNormalizer().normalize('corpus', '')
all_nodes = []
for b in blocks:
    all_nodes.extend(SemanticExtractor().extract(b))

print(f'Total nodes: {len(all_nodes)}')

synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()

# Test first node
node = all_nodes[0]
cq = synth.synthesize(all_nodes[0])
print(f'Valid: {cq.valid}')
print(f'Stem: {cq.stem[:80]}')
print(f'Provenance evidence: {cq.provenance.get("evidenceText", "MISSING")[:80]}')

# Check verification
from v13_discovery.provenance import verify_provenance_chain
corpus_dict = {'ncert_xi_physical_geo.txt': ''}
res = verify_provenance_chain(cq.provenance, source_corpus=corpus_text)
print(f'Valid: {res.is_valid}, errors: {res.errors}')