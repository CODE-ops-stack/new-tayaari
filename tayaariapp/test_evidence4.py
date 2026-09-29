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

print('Total nodes:', len(all_nodes))

synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()

for i, node in enumerate(all_nodes[:10]):
    cq = synth.synthesize(all_nodes[i])
    if cq.valid:
        evidence = cq.provenance.get('evidenceText', '')
        print('Node', i, 'evidence_len=', len(cq.provenance.get('evidenceText', '')), 'evidence[:80]=', cq.provenance.get('evidenceText', '')[:80])
        print('  In corpus:', cq.provenance.get('evidenceText', '')[:50] in corpus_text)
        print()