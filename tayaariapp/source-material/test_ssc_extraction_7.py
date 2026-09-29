import json

with open("source-material/extracted_ssc_qs.json", "r") as f:
    qs = json.load(f)

print("Q1")
print(json.dumps(qs.get("1"), indent=2))
print("Q15")
print(json.dumps(qs.get("15"), indent=2))
print("Q196")
print(json.dumps(qs.get("196"), indent=2))
