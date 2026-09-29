from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.semantic_extractor import KnowledgeNode
from v13_discovery.auditors import MultiAgentAuditingGate

synth = QuestionSynthesizer()
auditor = MultiAgentAuditingGate()

# Test 1: Full moon / Poornima
print('='*80)
print('TEST 1: Full moon / Poornima')
print('='*80)
node1 = KnowledgeNode(
    node_id='test_1', intent_type='definition', primary_entity='whole sky',
    predicate='is Full moon night or Poornima.', secondary_entities=[], conditions=[],
    quantitative_data=None, raw_evidence='It is Full moon night or Poornima.',
    source_location={'sourceId': 'test'}, confidence=0.95
)
cq1 = synth.synthesize(node1)
print('Stem:', cq1.stem)
print('Answer:', cq1.correctAnswer, '->', cq1.options.get(cq1.correctAnswer.replace('opt_', ''), ''))
print('Valid:', cq1.valid)
r1 = auditor.audit(cq1)
print('Audit:', r1.overallGate, 'Failures:', r1.failureReasons)
print()

# Test 2: New moon / Amavasya
print('='*80)
print('TEST 2: New moon / Amavasya')
print('='*80)
node2 = KnowledgeNode(
    node_id='test_2', intent_type='definition', primary_entity='whole sky',
    predicate='is a New moon night or Amavasya.', secondary_entities=[], conditions=[],
    quantitative_data=None, raw_evidence='It is a New moon night or Amavasya.',
    source_location={'sourceId': 'test'}, confidence=0.95
)
cq2 = synth.synthesize(node2)
print('Stem:', cq2.stem)
print('Answer:', cq2.correctAnswer, '->', cq2.options.get(cq2.correctAnswer.replace('opt_', ''), ''))
print('Valid:', cq2.valid)
r2 = auditor.audit(cq2)
print('Audit:', r2.overallGate, 'Failures:', r2.failureReasons)
print()

# Test 3: celestial bodies definition
print('='*80)
print('TEST 3: celestial bodies definition')
print('='*80)
node3 = KnowledgeNode(
    node_id='test_3', intent_type='definition', primary_entity='celestial bodies',
    predicate='are called The sun, the moon and all those objects shining in the night sky',
    secondary_entities=[], conditions=[], quantitative_data=None,
    raw_evidence='The sun, the moon and all those objects shining in the night sky are called celestial bodies.',
    source_location={'sourceId': 'test'}, confidence=0.95
)
cq3 = synth.synthesize(node3)
print('Stem:', cq3.stem)
print('Answer:', cq3.correctAnswer, '->', cq3.options.get(cq3.correctAnswer.replace('opt_', ''), ''))
print('Valid:', cq3.valid)
r3 = auditor.audit(cq3)
print('Audit:', r3.overallGate, 'Failures:', r3.failureReasons)