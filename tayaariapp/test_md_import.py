from tests.e2e.test_helpers import DataImporterSimulator

md = '''- **Topic**: 1. Test
- **Tier**: Standard
- **Format**: Direct Fact
- **Exam-Relevance**: High
- **Source**: NCERT Physical Geography
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: V13-001
- **Question**: \`\`\`
Which of the following is defined as: test?
(A) A
(B) B
(C) C
(D) D
Explanation: Test explanation
Correct Answer: Option A
\`\`\`'''

result = DataImporterSimulator.parse_markdown(md)
print('totalFound:', result['totalFound'])
print('totalAccepted:', result['totalAccepted'])
print('totalRejected:', result['totalRejected'])
print('rejections:', result['rejections'])