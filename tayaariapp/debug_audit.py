from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity, verify_provenance_chain

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
tracker = ProvenanceTracker()

corpus_path = r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt'
with open(corpus_path, 'r', encoding='utf-8', errors='ignore') as f:
    corpus_text = f.read()

blocks = normalizer.normalize(corpus_path, corpus_text)
raw_nodes = []
for b in blocks:
    raw_nodes.extend(extractor.extract(b))

corpus_dict = {
    corpus_path: corpus_text,
    'geography_extracted.txt': corpus_text
}

batch_records = []
for i, node in enumerate(raw_nodes[:100]):
    cq = synth.synthesize(node)
    if cq.valid:
        tracker.bind_candidate_question(cq, node)
        batch_records.append(cq.provenance)

print('Total records:', len(batch_records))

# Audit with debug
for i, prov in enumerate(batch_records):
    res = verify_provenance_chain(prov, source_corpus=corpus_dict)
    if not res.is_valid:
        print('FAILED record', i)
        print('  Evidence:', prov.get('evidenceText', '')[:100])
        print('  Errors:', res.errors)
        print('  Broken link:', res.broken_link)
        print()