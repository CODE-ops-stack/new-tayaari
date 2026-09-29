import re

with open("source-material/geography_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Let's find headings or uppercase blocks
headings = re.findall(r'\n([A-Z\s]{4,35})\n', text)
print("Headings found in geography_extracted.txt:")
for h in list(set(headings))[:25]:
    if h.strip():
        print(f" - {h.strip()}")

