import json
with open("classified_questions.json") as f:
    orig = json.load(f)
for q in orig:
    text = q['text']
    import re
    matches = list(re.finditer(r'(Q\d+\.)', text))
    if len(matches) > 1:
        print(f"Original Seq: {q['seq_num']} has {len(matches)} questions:")
        for m in matches:
            print(m.group(1))
        print("---")
