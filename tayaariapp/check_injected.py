"""
Fix: Topics 3, 5, 6, 7, 18 have only Elite questions. 
We add General-Competitive Basic questions so GROUP_B and GROUP_C users see them.
Topic 45 is 'Unclassified' - we'll fix its exam-relevance tags too.
"""

# Read file
with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Change all GEN-xxx questions that were tagged as "General-Competitive" 
# but we just need to verify the GEN questions we added are correct
# Actually let's check what we inserted for topic 3

import re

# Check topic 3 questions
blocks = re.split(r'\n## (?=\d+\. )', content)
for b in blocks:
    if b.startswith('3. Motions of the Earth'):
        qPattern = re.compile(
            r'- \*\*Topic\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Tier\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Format\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Exam-Relevance\*\*: ([^\r\n]*?)\s*\n',
            re.DOTALL
        )
        for m in qPattern.finditer(b):
            print('Topic 3 question: tier=' + m.group(2).strip() + ', relevance=' + m.group(4).strip())
        break

for b in blocks:
    if b.startswith('7. Our Country'):
        qPattern = re.compile(
            r'- \*\*Topic\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Tier\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Format\*\*: ([^\r\n]*?)\s*\n'
            r'- \*\*Exam-Relevance\*\*: ([^\r\n]*?)\s*\n',
            re.DOTALL
        )
        for m in qPattern.finditer(b):
            print('Topic 7 question: tier=' + m.group(2).strip() + ', relevance=' + m.group(4).strip())
        break
