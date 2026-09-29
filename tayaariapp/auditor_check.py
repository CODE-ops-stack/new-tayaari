from v13_discovery.auditors import AdversarialAuditor, MultiAgentAuditingGate
from v13_discovery.question_synthesizer import QuestionSynthesizer, OntologyRegistry
from v13_discovery.semantic_extractor import KnowledgeNode

# Check what the adversarial auditor actually validates
auditor = AdversarialAuditor()

# Create a mock question like Test 3
class MockCQ:
    def __init__(self, stem, options, correctAnswer):
        self.stem = stem
        self.options = options
        self.correctAnswer = correctAnswer
        self.distractorDissections = []

# Test 3 question
cq3 = MockCQ(
    stem="Which of the following is defined as: called The sun, the moon and all those objects shining in the night sky?",
    options={'a': 'Asteroid', 'b': 'Star', 'c': 'Galaxy', 'd': 'Meteoroid'},
    correctAnswer='opt_b'
)

print("Testing AdversarialAuditor on Test 3 question:")
result = auditor.audit(cq3)
print(f'Verdict: {result.verdict}')
print(f'Violations: {result.violations}')

# Now check what the MultiAgentAuditingGate does
gate = MultiAgentAuditingGate()
class MockCQ2:
    def __init__(self):
        self.stem = "Which of the following is defined as: called The sun, the moon and all those objects shining in the night sky?"
        self.options = {'a': 'Asteroid', 'b': 'Star', 'c': 'Galaxy', 'd': 'Meteoroid'}
        self.correctAnswer = 'opt_b'
        self.distractorDissections = []
        self.cognitiveDemand = 'UNDERSTAND'
        self.examTarget = 'UPSC-Prelims'
        self.format = 'Direct Fact'
        self.provenance = {}
        self.id = 'test'

cq2 = MockCQ2()
result2 = gate.audit(cq2)
print(f'\nMultiAgentAuditingGate result:')
print(f'  Cognitive: {result2.cognitiveVerdict}')
print(f'  ExamFit: {result2.examFitVerdict}')
print(f'  Adversarial: {result2.adversarialVerdict}')
print(f'  Overall: {result2.overallGate}')
print(f'  Failures: {result2.failureReasons}')