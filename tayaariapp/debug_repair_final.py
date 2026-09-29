import copy
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.auditors import SelfRepairPipeline, MultiAgentAuditingGate, FlawClassifier

synth = QuestionSynthesizer()
normalizer = DocumentNormalizer()
extractor = SemanticExtractor()

with open('source-material/geography_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
    corpus_text = f.read()

blocks = normalizer.normalize('source-material/geography_extracted.txt', corpus_text)
all_nodes = []
for b in blocks:
    all_nodes.extend(extractor.extract(b))

raw_candidates = []
for node in all_nodes:
    ent = (getattr(node, 'primary_entity', '') or '').strip()
    ev = (getattr(node, 'raw_evidence', '') or '').strip()
    if len(ent) < 3 or ent.lower() in {'it', 'they', 'we', 'you', 'this', 'these', 'that', 'those', 'there', 'here', 'he', 'she'}:
        continue
    if len(ev) < 20:
        continue
    try:
        cq = synth.synthesize(node, shuffle=True)
        if getattr(cq, 'valid', False):
            raw_candidates.append(cq)
    except Exception as e:
        pass

print("Total raw candidates:", len(raw_candidates))

# Use first 50 candidates for testing
test_candidates = raw_candidates[:50]

from v13_discovery.auditors import MultiAgentAuditingGate
gate = MultiAgentAuditingGate()

# Audit all candidates
failed = 0
failure_types = {}
for cq in test_candidates:
    report = gate.audit(cq)
    if report.overallGate != "PASS":
        failed += 1
        for v in report.failureReasons:
            # Extract category from failure message
            for cat in ["SEMANTIC_TYPE_MISMATCH", "STEM_EVIDENCE_MISMATCH", "WRONG_DEFINIENDUM", "NO_DEFINIENDUM_FOUND", "ANSWER_NOT_IN_EVIDENCE", "SEMANTIC_AMBIGUITY", "STEM_LEAKAGE", "QUOTATION_TEMPLATE", "TRIVIAL_STEM", "UNSUPPORTED_EXAM", "INFORMAL_REGISTER", "OPTION_COUNT", "OPTION_DUPLICATION", "ARTICLE_LEAKAGE", "DISSECTION_LEAK", "INVALID_TRAP_TYPE", "COGNITIVE_MISMATCH", "SHALLOW_RECALL"]:
                if cat in str(v):
                    failure_types[cat] = failure_types.get(cat, 0) + 1
                    break

print(f"Total tested: {len(test_candidates)}")
print(f"Failed: {failed}")
print("Failure types:")
for k, v in sorted(failure_types.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")