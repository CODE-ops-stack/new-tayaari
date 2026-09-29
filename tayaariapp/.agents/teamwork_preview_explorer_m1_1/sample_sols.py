import re

with open("source-material/question_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

sols = re.findall(r'(Sol\.\d+[\s\S]*?)(?=Q\.\d+|\Z)', text)
print(f"Total Sol blocks: {len(sols)}")
for i, s in enumerate(sols[:5]):
    print(f"--- Sol {i+1} ---")
    print(s[:300].strip())
