import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 3 (Pages 46-51)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH3-01",
    "filename": "fatman_fresh_batch3.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 3,
    "partLabel": "Parmar SSC Geography (Pages 46-51)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (6 Images)",
    "pageCount": 6,
    "provenance": "Supplied by User (Fresh Batch 3)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Indian Islands (A&N, Lakshadweep, coastal/riverine islands), Channels/Passages, Drainage Patterns, and the Himalayan River Systems (Indus, Ganga, Brahmaputra) including tributaries and cities on rivers.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 3 source to registry.")
