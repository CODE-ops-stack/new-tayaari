import json
d = json.load(open("v9_discovery_report.json", encoding="utf-8"))
for i, ex in enumerate(d["EXAMPLES"]):
    print(f"EXAMPLE {i+1}")
    print(f"-> STEM: {ex['text']}")
    print(f"-> ANS: {ex['options'][ex['correctIndex']]}")
    print(f"-> DISTRACTOR 1: {ex['options'][(ex['correctIndex']+1)%4]}")
    print(f"-> COGNITIVE: {ex['metadata']['cognitiveDemand']}")
    print(f"-> EXPLANATION: {ex['explanation']}")
    print()
