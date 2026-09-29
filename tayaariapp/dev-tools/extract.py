import re
import json

with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

questions = []
# Match blocks of questions
pattern = r"- \*\*Topic\*\*: (.*?)\n- \*\*Tier\*\*: (.*?)\n- \*\*Format\*\*: (.*?)\n- \*\*Exam-Relevance\*\*: (.*?)\n- \*\*Source\*\*: (.*?)\n- \*\*Specific-Exam\*\*: UPSC-Prelims\n- \*\*Question\*\*:\n```\n(.*?)\n```"
matches = re.findall(pattern, content, re.DOTALL)

for m in matches:
    questions.append({
        "old_topic": m[0],
        "tier": m[1],
        "format": m[2],
        "exam_rel": m[3],
        "source": m[4],
        "text": m[5].strip()
    })

print(f"Extracted {len(questions)} questions")
with open("/app/applet/upsc_extracted.json", "w") as f:
    json.dump(questions, f, indent=2)
