import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 6 (12 pages)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH6-01",
    "filename": "fatman_fresh_batch6.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 6,
    "partLabel": "Parmar SSC Geography (Pages 58-68)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (12 Images)",
    "pageCount": 12,
    "provenance": "Supplied by User (Fresh Batch 6)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Monsoons (ENSO, IOD, Koeppen), Forests & Grasslands (Types, Global names, ISFR), Soils (Types, USDA, Conservation), and Agriculture (Farming types, Shifting cultivation regional names, Major Crops, Irrigation). High density factual tables.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 6 source to registry.")
