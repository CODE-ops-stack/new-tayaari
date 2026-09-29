import re

content = """1. The Earth in the Solar System
### UPSC Prelims Data
- **Topic**: 1. The Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General
- **Source**: Real-PYQ
- **Specific-Exam**: SSC
- **PDF-Sequence-Number**: 617
- **Question**:
```
Q617. text
```
"""

m = re.search(r'^(\d+)\. (.*?)\n', content)
print("Topic match:", m.groups() if m else None)

qPattern = re.compile(
    r'- \*\*Topic\*\*: (.*?)\n' +
    r'- \*\*Tier\*\*: (.*?)\n' +
    r'- \*\*Format\*\*: (.*?)\n' +
    r'- \*\*Exam-Relevance\*\*: (.*?)\n' +
    r'- \*\*Source\*\*: (.*?)\n' +
    r'- \*\*Specific-Exam\*\*: (.*?)\n' +
    r'(?:- \*\*Trap-Type\*\*: (.*?)\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (.*?)\n' +
    r'- \*\*Question\*\*:\n```\n(.*?)\n```', re.DOTALL
)

qs = qPattern.findall(content)
print("Questions:", len(qs))
