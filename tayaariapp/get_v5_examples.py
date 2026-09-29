import json
d = json.load(open("v5_discovery_report.json", encoding="utf-8"))
for i, ex in enumerate(d["Examples"]):
    print(f"EXAMPLE {i+1}")
    print(f"SOURCE: {ex['metadata']['provenance'][0]['sourceId']}")
    print(f"-> QUESTION: {ex['text']}")
    print(f"-> CORRECT ANSWER: {ex['options'][ex['correctIndex']]}")
    print(f"-> DISTRACTOR RATIONALE: {ex['validation']['distractorLogic']}")
    print()
for i, ex in enumerate(d["RejectedExamples"]):
    print(f"REJECTED {i+1}: {ex['reason']} | {ex['sentence'][:80]}")
