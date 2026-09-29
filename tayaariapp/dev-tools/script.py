import re
with open('source-material/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()
pattern = re.compile(r'- \*\*Topic\*\*: (.*?)
- \*\*Tier\*\*: (.*?)
- \*\*Format\*\*: (.*?)
.*?- \*\*Question\*\*:
(.*?)(?=Correct Answer:)', re.DOTALL)
matches = pattern.findall(content)
print(f'Found {len(matches)} questions')

