import json, re
orig = json.load(open("classified_questions.json"))
for q in orig:
    text = q["text"]
    matches = list(re.finditer(r'(Q\d+\.)', text))
    if len(matches) > 1:
        for m in matches:
            idx = m.start()
            print(text[max(0, idx-10):idx+20].replace('\n', ' '))
