import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from v13_discovery.semantic_extractor import SemanticExtractor, canonicalize_intent

se = SemanticExtractor()
with open('data/golden_eval_set.json', encoding='utf-8') as f:
    data = json.load(f)

positives = [p for p in data['examples'] if p['expected_label'] == 'positive']
print(f'Total positives: {len(positives)}')
correct_intent = 0
extracted_count = 0
for p in positives:
    nodes = se.extract(p['text'])
    if not nodes:
        print(f"FAIL DROPPED: {p['id']} | expected: {p['intent']} | text: {p['text']}")
    else:
        node = nodes[0]
        extracted_count += 1
        expected = canonicalize_intent(p['intent'])
        actual = canonicalize_intent(node.intent_type)
        if actual == expected:
            correct_intent += 1
        else:
            print(f"INTENT MISMATCH: {p['id']} | expected: {expected} | got: {actual} | text: {p['text']}")

print(f"Extracted: {extracted_count}/{len(positives)}")
print(f"Correct Intent: {correct_intent}/{len(positives)}")
