import copy
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.auditors import SelfRepairPipeline, MultiAgentAuditingGate

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

flawed_candidates = [copy.deepcopy(c) for c in raw_candidates[:4]]

flawed_candidates[0].stem = 'Why is Granite an intrusive rock?'
flawed_candidates[1].stem = 'What is a direct consequence of solar energy?'
flawed_candidates[2].stem = 'What is Earth?'
flawed_candidates[3].examTarget = 'Kindergarten-Quiz'

pipeline = SelfRepairPipeline()
results = pipeline.run_cycle(flawed_candidates)

from v13_discovery.auditors import MultiAgentAuditingGate
gate = MultiAgentAuditingGate()

print('Regenerated count:', len(results['regenerated_questions']))
for i, q in enumerate(results['regenerated_questions']):
    report = gate.audit(q)
    if report.overallGate != 'PASS':
        print(f'Question {i} FAILED:')
        print('  Stem:', q.stem[:100])
        print('  Failures:', report.failureReasons)
        print()