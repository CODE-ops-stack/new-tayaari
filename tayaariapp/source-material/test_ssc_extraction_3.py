import re
import json

with open("source-material/question_extracted.txt", "r") as f:
    text = f.read()

# Debug first 1000 characters
print("Text Start:", repr(text[:1000]))

# Search for Sol.1
match = re.search(r"Sol\.(\d+)\.", text)
if match:
    print(f"Found Sol: {match.group(0)}")

# Search for options
match = re.search(r"\(a\)\s*(.*?)(\(b\)|$)", text[:1000], re.DOTALL)
if match:
    print(f"Found Option A: {match.group(1)}")
