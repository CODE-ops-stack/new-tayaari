import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 5 (12 pages)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH5-01",
    "filename": "fatman_fresh_batch5.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 5,
    "partLabel": "Parmar SSC Geography (Pages 10-15 and 52-57)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (12 Images)",
    "pageCount": 12,
    "provenance": "Supplied by User (Fresh Batch 5)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Peninsular Rivers, Dams, Waterfalls, Lakes (Pages 52-57) AND Physical Geography fundamentals: Earth's Interior, Plate Tectonics, Earthquakes, Rocks, Volcanoes, Continental Drift (Pages 10-15). Highly factual.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 5 source to registry.")
