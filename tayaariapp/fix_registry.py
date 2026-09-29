import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

# Keep non-fresh fatman records
new_sources = [s for s in registry["sources"] if "FATMAN-FRESH" not in s["sourceId"]]

# Add the 13 present parts explicitly
parts_data = [
    (1, "Cover, Index, Pages 1-3", "FATMAN-FRESH-PART01", "Vision_OCR", "FULLY_READABLE"),
    (3, "Pages 10-15", "FATMAN-FRESH-PART03", "Vision_OCR", "FULLY_READABLE"),
    (4, "Pages 16-21", "FATMAN-FRESH-PART04", "Vision_OCR", "FULLY_READABLE"),
    (5, "Pages 22-27", "FATMAN-FRESH-PART05", "Vision_OCR", "FULLY_READABLE"),
    (6, "Pages 28-33", "FATMAN-FRESH-PART06", "Vision_OCR", "FULLY_READABLE"),
    (7, "Pages 34-39", "FATMAN-FRESH-PART07", "Vision_OCR", "FULLY_READABLE"),
    (9, "Pages 46-51", "FATMAN-FRESH-PART09", "Vision_OCR", "FULLY_READABLE"),
    (10, "Pages 52-57", "FATMAN-FRESH-PART10", "Vision_OCR", "FULLY_READABLE"),
    (11, "Pages 58-63", "FATMAN-FRESH-PART11", "Vision_OCR", "FULLY_READABLE"),
    (12, "Pages 64-68", "FATMAN-FRESH-PART12", "Vision_OCR", "FULLY_READABLE"),
    (13, "Pages 69-74", "FATMAN-FRESH-PART13", "Vision_OCR", "FULLY_READABLE"),
    (14, "Pages 75-80", "FATMAN-FRESH-PART14", "Vision_OCR", "FULLY_READABLE"),
    (15, "Pages 81-85", "FATMAN-FRESH-PART15", "Vision_OCR", "FULLY_READABLE"),
]

for p_num, label, s_id, method, status in parts_data:
    new_sources.append({
        "sourceId": s_id,
        "filename": f"fatman_fresh_part{p_num}.pdf",
        "sourceSet": "FATMAN_GEOGRAPHY_FRESH_SPLIT",
        "batch": "N/A",
        "partLabel": f"Parmar SSC Geography ({label})",
        "sourceType": "KNOWLEDGE",
        "subject": "Geography",
        "examRelevance": ["SSC CGL", "SSC CHSL", "RRB"],
        "readabilityStatus": status,
        "extractionMethod": method,
        "size": "Unknown",
        "pageCount": 6 if p_num not in [12, 15] else 5,
        "provenance": "Supplied by User",
        "relationshipToOld": "RELATED_BUT_NOT_IDENTICAL (Identifies as PARMAR SSC)",
        "coverageNotes": f"Coverage for Part {p_num}",
        "priority": 2
    })

registry["sources"] = new_sources

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Registry reformatted to 16-part structure.")
