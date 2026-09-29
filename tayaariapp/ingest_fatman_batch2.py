import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 2 (18 pages)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH2-01",
    "filename": "fatman_fresh_batch2.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 2,
    "partLabel": "Parmar SSC Geography (Pages 22-39)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (18 Images)",
    "pageCount": 18,
    "provenance": "Supplied by User (Fresh Batch 2)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Karst/Coastal/Aeolian Landforms, Atmosphere (Layers, Heat Budget, Clouds), Winds & Cyclones, India's Location/Borders, and Himalayas (Ranges, Passes). High density factual content.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 2 source to registry.")
