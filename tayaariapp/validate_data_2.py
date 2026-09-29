import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

q_pattern = re.compile(
    r"- \*\*Topic\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Tier\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Format\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Exam-Relevance\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Source\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Specific-Exam\*\*: ([^\r\n]*?)\s*\n"
    r"(?:- \*\*Trap-Type\*\*: ([^\r\n]*?)\s*\n)?"
    r"- \*\*PDF-Sequence-Number\*\*: ([^\r\n]*?)\s*\n"
    r"- \*\*Question\*\*:\s*\s*(.*?)\s*",
    re.DOTALL
)

matches = q_pattern.finditer(content)

q_count = 0
formats = {}
traps = {}

for m in matches:
    q_count += 1
    raw_fmt = m.group(3).strip()
    raw_trap = m.group(7).strip() if m.group(7) else ''
    
    formats[raw_fmt] = formats.get(raw_fmt, 0) + 1
    traps[raw_trap] = traps.get(raw_trap, 0) + 1

print(f"Total Questions: {q_count}")
print("\n--- FORMATS ---")
for k, v in sorted(formats.items(), key=lambda x: -x[1]):
    print(f"{k}: {v}")
    
print("\n--- TRAPS ---")
for k, v in sorted(traps.items(), key=lambda x: -x[1]):
    print(f"{k}: {v}")

