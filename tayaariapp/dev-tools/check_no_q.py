import json, re
orig = json.load(open("classified_questions.json"))
no_q = []
for q in orig:
    text = q["text"]
    matches = list(re.finditer(r'(Q\d+\.)', text))
    if not matches:
        no_q.append(text)
print("No Q count:", len(no_q))
