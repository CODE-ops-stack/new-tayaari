import re

md_path = "/app/applet/source-material/consolidated_grounding.md"
with open(md_path, 'r') as f:
    content = f.read()

blocks = re.split(r'\r?\n## (?=\d+\. )', content)
print(f"Total blocks: {len(blocks)}")

total_q = 0
for i in range(1, len(blocks)):
    block = blocks[i]
    topic_match = re.search(r'^(\d+)\. (.*?)\r?\n', block)
    if not topic_match:
        continue
    
    q_pattern = re.compile(
        r'- \*\*Topic\*\*: (.*?)\r?\n' +
        r'- \*\*Tier\*\*: (.*?)\r?\n' +
        r'- \*\*Format\*\*: (.*?)\r?\n' +
        r'- \*\*Exam-Relevance\*\*: (.*?)\r?\n' +
        r'- \*\*Source\*\*: (.*?)\r?\n' +
        r'- \*\*Specific-Exam\*\*: (.*?)\r?\n' +
        r'(?:- \*\*Trap-Type\*\*: (.*?)\r?\n)?' +
        r'- \*\*PDF-Sequence-Number\*\*: (.*?)\r?\n' +
        r'- \*\*Question\*\*:\r?\n```\r?\n(.*?)\r?\n```', re.DOTALL
    )
    
    matches = q_pattern.findall(block)
    total_q += len(matches)

print(f"Total extracted: {total_q}")
