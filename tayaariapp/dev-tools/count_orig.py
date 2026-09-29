import json
with open("classified_questions.json", "r") as f:
    orig = json.load(f)

formats = [q["format"] for q in orig]
from collections import Counter
print(Counter(formats))
