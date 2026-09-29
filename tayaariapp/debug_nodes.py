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

print(f'Total nodes: {len(nodes)}')

synth = QuestionSynthesizer()

# Check first 100 nodes
for i, node in enumerate(nodes[:100]):
    cq = synth.synthesize(nodes[i])
    if cq.valid:
        evidence = cq.provenance.get('evidenceText', '')
        in_corpus = evidence[:50] in corpus_text
        if not in_corpus:
            print(f'Node {i}: evidence NOT in corpus')
            print(f'  Evidence: {evidence[:80]}')
            print(f'  In corpus: {evidence[:50]} in corpus: {evidence[:50]} in corpus_text')
            break
else:
    print('All 100 nodes have evidence in corpus')