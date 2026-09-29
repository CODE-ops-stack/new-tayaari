import json
import os

print("Listing all current registry entries for FRESH FATMAN:")
registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

for s in registry["sources"]:
    if "FATMAN-FRESH" in s["sourceId"]:
        print(f"{s['sourceId']} : {s['partLabel']} : {s['pageCount']} pages")

print("\nValidating 50 staged questions:")
staging_path = "staging_batch_1.json"
if os.path.exists(staging_path):
    with open(staging_path, "r", encoding="utf-8") as f:
        staged = json.load(f)
    print(f"File exists. Total questions: {len(staged.get('questions', []))}")
else:
    print("staging_batch_1.json NOT FOUND.")
