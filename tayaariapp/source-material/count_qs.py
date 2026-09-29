import re
from collections import Counter

file_path = "c:/Users/harsh/Downloads/tayaari/tayaari files/source-material/consolidated_grounding.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

questions = re.findall(r"- \*\*Question\*\*:", content)
total_questions = len(questions)

formats = re.findall(r"- \*\*Format\*\*:\s*(.*)", content)
format_counts = Counter(formats)

print(f"Total questions found: {total_questions}")
print("Format breakdown:")
for fmt, count in format_counts.items():
    print(f"  - {fmt}: {count}")

# Let's also verify topics and other counts just to be sure
topics = re.findall(r"- \*\*Topic\*\*:\s*(.*)", content)
print(f"Total Topic tags: {len(topics)}")
