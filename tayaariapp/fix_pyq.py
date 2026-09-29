import codecs
import re

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'r', 'utf-8') as f:
    content = f.read()

questions = re.split(r'- \*\*Topic\*\*: ', content)
valid = 0
real_pyq = 0
unverified = 0
pyq_style = 0
original = 0

new_questions = [questions[0]]

for q in questions[1:]:
    if "- **Question**:" in q:
        valid += 1
        
        # Extract specific exam string
        match = re.search(r'- \*\*Specific-Exam\*\*: ([^\r\n]*)', q)
        specific_exam = match.group(1).strip() if match else ""
        
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', specific_exam))
        has_exam = "UPSC" in specific_exam or "SSC" in specific_exam or "BPSC" in specific_exam or "RRB" in specific_exam or "CDS" in specific_exam or "NDA" in specific_exam or "CAPF" in specific_exam
        
        if "Real-PYQ" in q:
            if has_year and has_exam:
                real_pyq += 1
                new_q = q
            else:
                unverified += 1
                new_q = q.replace("- **Source**: Real-PYQ", "- **Source**: UNVERIFIED")
        elif "PYQ-style" in q or "PYQ-Style" in q:
            pyq_style += 1
            new_q = q
        else:
            original += 1
            new_q = q
            
        new_questions.append(new_q)
    else:
        new_questions.append(q)

new_content = '- **Topic**: '.join(new_questions)

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'w', 'utf-8') as f:
    f.write(new_content)

print(f"REAL_PYQ: {real_pyq}")
print(f"UNVERIFIED: {unverified}")
print(f"PYQ_STYLE: {pyq_style}")
print(f"ORIGINAL: {original}")
