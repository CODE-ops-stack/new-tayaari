import json
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import SemanticExtractor, canonicalize_intent

def main():
    se = SemanticExtractor()
    with open("data/golden_eval_set.json", encoding="utf-8") as f:
        data = json.load(f)
    pos = [x for x in data["examples"] if x["expected_label"] == "positive"]

    mismatches = 0
    for p in pos:
        res = se.extract(p["text"])
        ext_intent = canonicalize_intent(res[0].intent_type) if res else "NONE"
        exp_intent = canonicalize_intent(p["intent"])
        if ext_intent != exp_intent:
            mismatches += 1
            print(f"[{p['id']}] Expected: {exp_intent:14} | Extracted: {ext_intent:14} | Text: {p['text'][:70]}...")
    print(f"Total positive: {len(pos)}, Mismatches on Golden: {mismatches}")

if __name__ == "__main__":
    main()
