from v13_discovery.provenance import audit_provenance_integrity, verify_provenance_chain
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.provenance import ProvenanceTracker
import os

corpus_path = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt"
with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
    corpus_text = f.read()

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
tracker = ProvenanceTracker()

blocks = normalizer.normalize(corpus_path, corpus_text)
raw_nodes = []
for b in blocks:
    raw_nodes.extend(extractor.extract(b))

print(f"Total nodes: {len(raw_nodes)}")

batch_records = []
for i, node in enumerate(raw_nodes[:100]):
    cq = synth.synthesize(node)
    tracker.bind_candidate_question(cq, node)
    batch_records.append(cq.provenance)

corpus_dict = {
    corpus_path: corpus_text,
    "geography_extracted.txt": corpus_text
}
audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)

print(f"Tampered: {audit_res['tampered_records']}")
print(f"Invalid: {audit_res['invalid_records']}")
print(f"Broken links: {audit_res['broken_links']}")
print(f"Verdict: {audit_res['audit_verdict']}")
print(f"Integrity rate: {audit_res['integrity_rate']}")

# Check each record individually
for i, prov in enumerate(batch_records):
    res = verify_provenance_chain(prov, source_corpus=corpus_dict)
    if not res.is_valid:
        print(f"\nRecord {i} FAILED:")
        print(f"  Evidence: {prov.get('evidenceText', '')[:80]}")
        print(f"  Errors: {res.errors}")
        print(f"  Broken link: {res.broken_link}")