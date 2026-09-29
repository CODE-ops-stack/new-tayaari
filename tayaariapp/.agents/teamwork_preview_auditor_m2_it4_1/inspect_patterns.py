"""
inspect_patterns.py
Maps each positive golden evaluation item to its matching pattern in LinguisticSemanticExtractor.PATTERNS.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
from v13_discovery.semantic_extractor import LinguisticSemanticExtractor

def main():
    with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
        d = json.load(f)

    lse = LinguisticSemanticExtractor()
    pos_items = [it for it in d["examples"] if it["expected_label"] == "positive"]

    print(f"Total positive items: {len(pos_items)}")
    for it in pos_items:
        t = it["text"]
        matched = []
        for idx, (intent, pat) in enumerate(lse.PATTERNS):
            if pat.search(t):
                matched.append((idx, intent))
        
        node = lse.extract(t)
        final_intent = node.intent_type if node else "NONE"
        matches_str = ", ".join(f"#{idx}:{intent}" for idx, intent in matched)
        print(f"{it['id']} [{it['intent']} -> {final_intent}]: matches [{matches_str}]")

if __name__ == "__main__":
    main()
