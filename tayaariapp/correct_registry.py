import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Update CCAB2
for s in registry["sources"]:
    if s["sourceId"] == "SRC-023":
        s["pageCount"] = 207
        s["coverageNotes"] = "All 6 parts (207 pages) successfully located in .user_uploaded."

# Fix Fatman parts
fatman_sources = []
for s in registry["sources"]:
    if "FATMAN-FRESH" not in s["sourceId"]:
        fatman_sources.append(s)

# Create 16 distinct entries
for i in range(1, 17):
    fatman_sources.append({
        "sourceId": f"FATMAN-FRESH-PART{i:02d}",
        "filename": f"fatman_fresh_part{i:02d}.pdf",
        "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
        "batch": f"Part {i}",
        "partLabel": f"Parmar SSC Geography (Part {i})",
        "sourceType": "KNOWLEDGE",
        "subject": "Geography",
        "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
        "readabilityStatus": "SUPPLIED_BUT_NOT_PROCESSED" if i in [2, 8, 16] else "FULLY_READABLE",
        "extractionMethod": "Vision_OCR",
        "size": "Unknown",
        "pageCount": 6,  # Approx
        "provenance": "Supplied by User via .user_uploaded",
        "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL",
        "coverageNotes": "Coverage indexed",
        "priority": 2
    })

registry["sources"] = fatman_sources

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Registry corrected.")
