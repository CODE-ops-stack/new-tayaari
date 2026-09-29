import json, re
orig = json.load(open("classified_questions.json"))
count = 0
for q in orig:
    text = q["text"]
    matches = list(re.finditer(r'(Q\d+\.)', text))
    count += len(matches) if matches else 1
print("Total questions by splitting:", count)
