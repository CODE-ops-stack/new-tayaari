import re

with open("source-material/geography_extracted_2.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

headings = re.findall(r'\n([A-Z\s]{4,35})\n', text)
print("Headings found in geography_extracted_2.txt:")
for h in list(set(headings))[:25]:
    if h.strip():
        print(f" - {h.strip()}")
