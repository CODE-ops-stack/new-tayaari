import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH1-01",
    "filename": "fatman_fresh_batch1.pdf", # Assigned based on batch context
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 1,
    "partLabel": "Parmar SSC Geography (Pages 16-21)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (6 Images/Pages)",
    "pageCount": 6,
    "provenance": "Supplied by User (Fresh Batch 1)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Corals, Geomorphology basics (Davis, Weathering types), Mass Movements, and Landforms (Fluvial, Glacial, Karst). Highly factual, tailored for SSC.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added new source to registry.")
