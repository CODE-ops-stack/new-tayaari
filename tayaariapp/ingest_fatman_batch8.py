import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 8 (5 pages)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH8-01",
    "filename": "fatman_fresh_batch8.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 8,
    "partLabel": "Parmar SSC Geography (Pages 81-85)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (5 Images)",
    "pageCount": 5,
    "provenance": "Supplied by User (Fresh Batch 8)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers World Map (European capitals, Oceania, Highest peaks, Cities on rivers, Tropic/Equator countries, Geological Timescale) and Human Geography (Population distribution, Demographic Transition Model, Population pyramids, Settlements). Highly factual.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 8 source to registry.")
