import json
from datetime import datetime

registry_path = "source_registry.json"

# Load existing registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Create new source entry for Batch 7 (12 pages)
new_source = {
    "sourceId": "FATMAN-FRESH-BATCH7-01",
    "filename": "fatman_fresh_batch7.pdf",
    "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
    "batch": 7,
    "partLabel": "Parmar SSC Geography (Pages 69-80)",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Vision_OCR",
    "size": "Unknown (12 Images)",
    "pageCount": 12,
    "provenance": "Supplied by User (Fresh Batch 7)",
    "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
    "coverageNotes": "Covers Agricultural Revolutions, Types of Cultures (Sericulture, etc.), Minerals (Iron Belts, Coal types/mines, Petroleum), Energy Resources (Nuclear, Solar, Biomass), Industrial Regions of India, and World Map (Straits, Mountains, Deserts, Rivers globally). Highly factual.",
    "priority": 2,
    "ingestionDate": datetime.now().isoformat()
}

registry["sources"].append(new_source)

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Added BATCH 7 source to registry.")
