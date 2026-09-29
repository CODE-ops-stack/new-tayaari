from tests.e2e.test_helpers import DataImporterSimulator, CandidateQuestion

cq = CandidateQuestion(
    id='q_test',
    stem='Which of the following is defined as: test?',
    options={'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'},
    correctAnswer='opt_a',
    explanation='Test explanation',
    distractorDissections=[],
    provenance={},
    cognitiveDemand='UNDERSTAND',
    examTarget='UPSC-Prelims',
    tier='Standard',
    format='Direct Fact',
    topicId=1,
    topicName='Physical Geography',
    pdfSequenceNumber='V13-001',
    valid=False
)

from tests.e2e.test_helpers import DataImporterSimulator

md = f"## 1. Physical Geography\n\n" + DataImporterSimulator.format_candidate_to_markdown(cq)

print("Markdown:")
print(DataImporterSimulator.format_candidate_to_markdown(cq))

result = DataImporterSimulator.parse_markdown(f"## 1. Physical Geography\n\n{cq.to_room_markdown()}")
print('totalFound:', result['totalFound'])
print('totalAccepted:', result['totalAccepted'])
print('totalRejected:', result['totalRejected'])
print('rejections:', result['rejections'])