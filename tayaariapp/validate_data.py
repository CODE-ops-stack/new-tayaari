import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

blocks = re.split(r'\n## (?=\d+\. )', content)
print(f"Total blocks: {len(blocks)}")

formats = {}
traps = {}
exams = {}
topics = {}

q_count = 0

for block in blocks[1:]:
    q_count += 1
    
    topic_match = re.search(r'^\d+\. (.*?)\n', block)
    topic = topic_match.group(1).strip() if topic_match else 'UNKNOWN'
    topics[topic] = topics.get(topic, 0) + 1
    
    format_match = re.search(r'- \*\*Format\*\*: (.*?)\n', block)
    raw_fmt = format_match.group(1).strip() if format_match else ''
    
    trap_match = re.search(r'- \*\*Trap-Type\*\*: (.*?)\n', block)
    raw_trap = trap_match.group(1).strip() if trap_match else ''
    
    exam_match = re.search(r'- \*\*Specific-Exam\*\*: (.*?)\n', block)
    raw_exam = exam_match.group(1).strip() if exam_match else ''
    
    formats[raw_fmt] = formats.get(raw_fmt, 0) + 1
    traps[raw_trap] = traps.get(raw_trap, 0) + 1
    exams[raw_exam] = exams.get(raw_exam, 0) + 1

print(f"Total Questions: {q_count}")
print("\n--- FORMATS ---")
for k, v in sorted(formats.items(), key=lambda x: -x[1]):
    print(f"{k}: {v}")
    
print("\n--- TRAPS ---")
for k, v in sorted(traps.items(), key=lambda x: -x[1]):
    print(f"{k}: {v}")

