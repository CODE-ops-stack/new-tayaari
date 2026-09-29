import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 4 (Cover, Index, Pages 1-3)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH4-01",
    "filename": "fatman_fresh_batch4.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 4,
    "partLabel": "Parmar SSC Geography (Cover, Index, Pages 1-3)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (6 Images)",
    "pageCount": 6,
    "provenance": "Supplied by User (Fresh Batch 4)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers the Book Cover, comprehensive visual Table of Contents (Flowcharts), and Pages 1-3 detailing the Solar System (Origin theories, Celestial Bodies, The Sun's structure and life cycle, and inner Planets). Highly factual.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 4 source to registry.")
