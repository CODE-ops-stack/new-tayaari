import json
d = json.load(open("v8_discovery_report.json", encoding="utf-8"))
for i, ex in enumerate(d["RejectedExamples"]):
    print(f"REJECTED {i+1}: {ex['reason']} | {ex['sentence'][:80]}")
