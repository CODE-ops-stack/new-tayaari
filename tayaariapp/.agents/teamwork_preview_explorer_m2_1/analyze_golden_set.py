import json
from collections import defaultdict

with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total examples: {len(data['examples'])}")
intents = defaultdict(list)
negatives = defaultdict(list)

for ex in data["examples"]:
    if ex["expected_label"] == "positive":
        intents[ex["intent"]].append(ex)
    else:
        negatives[ex.get("rejection_category", "unknown")].append(ex)

print(f"\n--- POSITIVE INTENTS ({len(intents)} intents, {sum(len(v) for v in intents.values())} examples) ---")
for intent, examples in sorted(intents.items()):
    print(f"\n[Intent: {intent}] ({len(examples)} examples)")
    for i, ex in enumerate(examples):
        pe = ex.get("semantic_entities", {}).get("primary_entity", "N/A") if ex.get("semantic_entities") else "N/A"
        pred = ex.get("semantic_entities", {}).get("predicate", "N/A") if ex.get("semantic_entities") else "N/A"
        print(f"  ({ex['id']}) {ex['text']}")
        print(f"       Primary: {pe} | Pred: {pred}")

print(f"\n--- NEGATIVE CATEGORIES ({len(negatives)} categories, {sum(len(v) for v in negatives.values())} examples) ---")
for cat, examples in sorted(negatives.items()):
    print(f"\n[Category: {cat}] ({len(examples)} examples)")
    for ex in examples[:2]:
        print(f"  ({ex['id']}) {ex['text'][:100]}... [Reason: {ex.get('rejection_reason')}]")
