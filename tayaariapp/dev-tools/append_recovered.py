import json
import re

with open('dev-tools/recovered.json', 'r') as f:
    recovered = json.load(f)

md_append = "\n## 100. Recovered Questions\n"
for item in recovered:
    seq = item['seq']
    text = item['text']
    
    # Extract question and options and solution
    # Q.50 . In which month ... (a) May (b) August (c) June (d) July Sol.50.(d) July. ...
    
    # Try to separate parts
    opt_match = re.search(r'(?i)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)\s*Sol\.\s*\d+\.\s*\(([a-d])\)', text)
    if not opt_match:
        # Some don't have Sol.\d+. format exactly
        opt_match = re.search(r'(?i)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)\s*Sol\..*?\(([a-d])\)', text)
        
    if opt_match:
        qText = text[:opt_match.start()].strip()
        optA = opt_match.group(1).strip()
        optB = opt_match.group(2).strip()
        optC = opt_match.group(3).strip()
        optD = opt_match.group(4).strip()
        correct = opt_match.group(5).lower()
        
        # fix Q.50 . to Q50.
        qText = re.sub(r'Q\.?\s*\d+\s*\.\s*', f'Q{seq}. ', qText)
        
        formatted = f"{qText}\na) {optA}\nb) {optB}\nc) {optC}\nd) {optD}\nCorrect answer: option {correct}"
    else:
        # Fallback if parsing fails
        formatted = text
        
    md_append += f"""
- **Topic**: 100. Recovered Questions
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: Real-PYQ
- **Specific-Exam**: SSC-Stenographer
- **PDF-Sequence-Number**: {seq}
- **Question**:
```
{formatted}
```
"""

with open('source-material/consolidated_grounding.md', 'a') as f:
    f.write(md_append)
print("Appended 15 questions!")
