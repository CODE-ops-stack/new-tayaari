import json
d = json.load(open("advanced_discovery_report.json", encoding="utf-8"))
for i, ex in enumerate(d["Examples"][:5]):
    print(f"EXAMPLE {i+1}")
    print(f"SOURCE: {ex['metadata']['provenance'][0]['sourceId']}")
    print(f"-> CLEAN NODE: {ex['metadata']['concept']}")
    print(f"-> EVIDENCE: {ex['metadata']['provenance'][0]['evidenceExcerpt']}")
    print(f"-> QUESTION: {ex['text']}")
    print(f"-> CORRECT ANSWER: {ex['options'][ex['correctIndex']]}")
    print(f"-> DISTRACTOR RATIONALE: {ex['validation']['distractorLogic']}")
    print(f"-> COGNITIVE MODE: {ex['metadata']['cognitiveDemand']}")
    print(f"-> EXAM: {ex['metadata']['examTarget'][0]}")
    print()
