from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.semantic_extractor import KnowledgeNode
from v13_discovery.auditors import MultiAgentAuditingGate

synth = QuestionSynthesizer()
auditor = MultiAgentAuditingGate()

# Test 3: celestial bodies definition - deep trace
print('='*80)
print('TEST 3: celestial bodies definition - DEEP TRACE')
print('='*80)
node3 = KnowledgeNode(
    node_id='test_3', intent_type='definition', primary_entity='celestial bodies',
    predicate='are called The sun, the moon and all those objects shining in the night sky',
    secondary_entities=[], conditions=[], quantitative_data=None,
    raw_evidence='The sun, the moon and all those objects shining in the night sky are called celestial bodies.',
    source_location={'sourceId': 'test'}, confidence=0.95
)

# Trace category resolution
from v13_discovery.question_synthesizer import OntologyRegistry
ontology = OntologyRegistry()
cat = ontology.find_category_for_entity('celestial bodies')
print(f'Category from "celestial bodies": {cat.category_id if cat else None}')

cat2 = synth._resolve_category_from_evidence(node3.raw_evidence)
print(f'Category from evidence scan: {cat2.category_id if cat2 else None}')

# Trace _extract_defined_term
defined_term = synth._extract_defined_term(node3.raw_evidence, cat2 if cat2 else cat)
print(f'_extract_defined_term result: {defined_term}')

# Trace predicate extraction
from v13_discovery.question_synthesizer import NaturalStemSynthesizer
pred = NaturalStemSynthesizer.extract_predicate_after_copula(node3.raw_evidence)
print(f'extract_predicate_after_copula: "{pred}"')

# Full synthesis
cq3 = synth.synthesize(node3)
print('Stem:', cq3.stem)
print('Answer:', cq3.correctAnswer, '->', cq3.options.get(cq3.correctAnswer.replace('opt_', ''), ''))
print('Valid:', cq3.valid)
r3 = auditor.audit(cq3)
print('Audit:', r3.overallGate, 'Failures:', r3.failureReasons)

# Check category members
print('Category members:', cat2.members if cat2 else cat.members)