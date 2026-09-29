import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("data/golden_eval_set.json", encoding="utf-8") as f:
    d = json.load(f)

print("Total examples:", len(d["examples"]))
negs = [x for x in d["examples"] if x.get("expected_label") == "negative"]
print("Negatives:", len(negs))
for x in negs:
    print(f"{x['id']} | {x.get('rejection_category')} | {repr(x['text'])}")

