# Check quality of generated questions from the full corpus
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity, verify_provenance_chain
import os

normalizer = DocumentNormalizer()
extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
tracker = ProvenanceTracker()

# Load ALL corpus files with absolute paths as keys
corpus_files = [
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted_2.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_physical_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_india_env.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_human_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_india_economy.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_x_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_ix_geo.txt',
]

corpus_dict = {}
all_nodes = []
for cf in corpus_files:
    try:
        with open(cf, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        corpus_dict[cf] = content
        blocks = normalizer.normalize(cf, content)
        for b in blocks:
            all_nodes.extend(extractor.extract(b))
    except Exception as e:
        print(cf, ': ERROR -', e)

print('Total nodes:', len(all_nodes))

# Try generating questions from all nodes
valid_questions = []
seen_stems = set()
intent_counts = {}
for i, node in enumerate(all_nodes):
    if len(valid_questions) >= 200:  # Reduced for faster testing
        break
    if not node.primary_entity or len(node.primary_entity) < 3:
        continue
    if len(node.raw_evidence) < 25:
        continue
    try:
        cq = synth.synthesize(node)
        if cq.valid:
            norm_stem = cq.stem.strip().lower()
            if norm_stem in seen_stems:
                continue
            seen_stems.add(norm_stem)
            tracker.bind_candidate_question(cq, node)
            valid_questions.append(cq)
            intent = cq.provenance.get('intentType', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    except Exception as e:
        pass

print('Valid questions generated:', len(valid_questions))
print('Intent distribution:', intent_counts)

# Check provenance integrity - find the failing ones
batch_records = [cq.provenance for cq in valid_questions]
failed = []
for i, prov in enumerate(batch_records):
    res = verify_provenance_chain(prov, source_corpus=corpus_dict)
    if not res.is_valid:
        failed.append((i, prov, res))
        print(f'Failed record {i}:')
        print(f'  Source file: {prov.get("sourceFile", "")}')
        print(f'  Evidence: {prov.get("evidenceText", "")[:100]}')
        print(f'  Errors: {res.errors}')
        print(f'  Broken link: {res.broken_link}')
        print()

print('Total failed:', len(failed))

audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)
print('Audit: Tampered=', audit_res['tampered_records'], 'Invalid=', audit_res['invalid_records'], 'Verdict=', audit_res['audit_verdict'], 'Broken links=', audit_res['broken_links'])