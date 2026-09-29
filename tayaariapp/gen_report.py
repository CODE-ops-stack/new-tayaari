import codecs
import re

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'r', 'utf-8') as f:
    content = f.read()

questions = re.split(r'\n## ', content)
valid = 0
invalid = 0
verified_trap = 0
pyq = 0
pyq_style = 0
original = 0

for q in questions[1:]:
    if "- **Question**:" in q:
        valid += 1
        if "- **Trap-Type**:" in q:
            verified_trap += 1
        if "PYQ" in q:
            pyq += 1
        elif "PYQ-style" in q or "PYQ-Style" in q:
            pyq_style += 1
        else:
            original += 1
    else:
        invalid += 1

print(f"TOTAL QUESTIONS: {len(questions)-1}")
print(f"VALID: {valid}")
print(f"INVALID: {invalid}")
print(f"PYQ: {pyq}")
print(f"PYQ_STYLE: {pyq_style}")
print(f"ORIGINAL: {original}")
print(f"VERIFIED_TRAP: {verified_trap}")
print(f"INFERRED_TRAP: 0")
print(f"UNCLASSIFIED_TRAP: {valid - verified_trap}")
