import re

with open('source-material/consolidated_grounding.md', 'r') as f:
    content = f.read()

qPattern = re.compile(
    r'- \*\*Specific-Exam\*\*: (.*?)\n' +
    r'(?:- \*\*Trap-Type\*\*: (.*?)\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (.*?)\n' +
    r'- \*\*Question\*\*:\n```\n(.*?)\n```', re.DOTALL
)

ssc_seqs = set()
for match in qPattern.finditer(content):
    exam = match.group(1).strip()
    seq = match.group(3).strip()
    if 'SSC' in exam:
        try:
            ssc_seqs.add(int(seq))
        except ValueError:
            pass

print(f"Total SSC: {len(ssc_seqs)}")
if len(ssc_seqs) > 0:
    max_seq = max(ssc_seqs)
    print(f"Max SEQ: {max_seq}")
    missing = [i for i in range(1, max_seq + 1) if i not in ssc_seqs]
    print(f"Missing SSC Sequences: {missing}")
