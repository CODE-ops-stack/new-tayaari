import json

with open('data/golden_eval_set.json', encoding='utf-8') as f:
    data = json.load(f)
positives = [p for p in data['examples'] if p['expected_label'] == 'positive']
by_intent = {}
for p in positives:
    by_intent.setdefault(p['intent'], []).append(p)

for intent in ["definition", "attribute", "cause/effect", "comparison", "spatial"]:
    items = by_intent.get(intent, [])
    print(f"=== INTENT: {intent} ({len(items)} items) ===")
    for it in items:
        print(f"  [{it['id']}] {it['text']}")
    print()
