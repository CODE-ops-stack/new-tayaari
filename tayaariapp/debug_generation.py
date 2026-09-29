from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor

synth = QuestionSynthesizer()
normalizer = DocumentNormalizer()
extractor = SemanticExtractor()

corpus_text = '''Evidence text statement 0 for geography topic.
Evidence text statement 1 for geography topic.
Evidence text statement 2 for geography topic.
Evidence text statement 3 for geography topic.
Evidence text statement 4 for geography topic.
Evidence text statement 5 for geography topic.
Evidence text statement 6 for geography topic.
Evidence text statement 7 for geography topic.
Evidence text statement 8 for geography topic.
Evidence text statement 9 for geography topic.'''

blocks = normalizer.normalize('test', corpus_text)
all_nodes = []
for b in blocks:
    all_nodes.extend(extractor.extract(b))

print(f'Total nodes: {len(all_nodes)}')

synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
for i, node in enumerate(all_nodes[:10]):
    cq = synth.synthesize(node)
    print(f'Node {i}: valid={cq.valid}, stem={cq.stem[:50] if cq.stem else "EMPTY"}...')