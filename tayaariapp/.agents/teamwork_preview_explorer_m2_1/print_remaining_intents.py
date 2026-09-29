import json

with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
    data = json.load(f)

first_set = ["definition", "attribute", "cause/effect", "comparison", "distribution", "classification", "condition", "exception", "part-of", "member-of"]

for ex in data["examples"]:
    if ex["expected_label"] == "positive" and ex["intent"] in first_set:
        pe = ex.get("semantic_entities", {}).get("primary_entity", "N/A")
        pred = ex.get("semantic_entities", {}).get("predicate", "N/A")
        sec = ex.get("semantic_entities", {}).get("secondary_entities", [])
        print(f"[{ex['intent'].upper()}] ({ex['id']}) {ex['text']}")
        print(f"  -> Primary: {pe}")
        print(f"  -> Predicate: {pred}")
        print(f"  -> Secondary: {sec}")
        print()
