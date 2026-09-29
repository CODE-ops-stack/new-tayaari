import re

md_path = "/app/applet/source-material/consolidated_grounding.md"
with open(md_path, 'r') as f:
    content = f.read()

q_pattern = re.compile(
    r'- \*\*Topic\*\*: (.*?)\r?\n' +
    r'- \*\*Tier\*\*: (.*?)\r?\n' +
    r'- \*\*Format\*\*: (.*?)\r?\n' +
    r'- \*\*Exam-Relevance\*\*: (.*?)\r?\n' +
    r'- \*\*Source\*\*: (.*?)\r?\n' +
    r'- \*\*Specific-Exam\*\*: (.*?)\r?\n' +
    r'(?:- \*\*Trap-Type\*\*: (.*?)\r?\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (188|189|296|314|354)\r?\n' +
    r'- \*\*Question\*\*:\r?\n```\r?\n(.*?)\r?\n```', re.DOTALL
)

matches = q_pattern.findall(content)
print("=== PROOF ===")
for m in matches:
    print(f"- **Topic**: {m[0]}")
    print(f"- **Tier**: {m[1]}")
    print(f"- **Format**: {m[2]}")
    print(f"- **PDF-Sequence-Number**: {m[7]}")
    print(f"- **Question**:\n```\n{m[8]}\n```")
    print("---")
