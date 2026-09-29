import re

with open('source-material/consolidated_grounding.md', 'r') as f:
    content = f.read()

qPattern = re.compile(
    r'- \*\*Specific-Exam\*\*: (.*?)\n' +
    r'(?:- \*\*Trap-Type\*\*: (.*?)\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (.*?)\n' +
    r'- \*\*Question\*\*:\n```\n(.*?)\n```', re.DOTALL
)

missing_count = 0
total_count = 0
for match in qPattern.finditer(content):
    exam = match.group(1).strip()
    seq = match.group(3).strip()
    qText = match.group(4).strip()
    total_count += 1
    
    if len(qText) < 15 or "missing" in qText.lower() or "failed" in qText.lower() or "not extracted" in qText.lower() or "???" in qText:
        print(f"Missing/Short {exam} Q{seq}: {qText}")
        missing_count += 1
        
print(f"Total: {total_count}, Missing: {missing_count}")
