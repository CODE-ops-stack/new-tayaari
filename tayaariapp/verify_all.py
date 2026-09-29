import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

fresh_fatman = [s for s in registry["sources"] if "FATMAN-FRESH" in s["sourceId"]]
print(f"Total Fresh Fatman batches successfully registered: {len(fresh_fatman)}")
for s in fresh_fatman:
    print(f"- {s['sourceId']}: {s['partLabel']}")
