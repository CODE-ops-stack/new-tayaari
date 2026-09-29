import re
with open('source-material/consolidated_grounding.md', 'r') as f:
    text = f.read()

relevance = re.findall(r'- \*\*Exam-Relevance\*\*: (.*)', text)
from collections import Counter
print(Counter(relevance))
