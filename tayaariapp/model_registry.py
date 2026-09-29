import json

registry_path = "source_registry.json"
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

new_sources = [s for s in registry["sources"] if "FATMAN-FRESH" not in s["sourceId"] and "SRC-023" not in s["sourceId"]]

# Add CCAB2 Parent + 6 Children
ccab2_files = [
    "media_1787474758984.pdf", "media_1787474759161.pdf", "media_1787474759426.pdf",
    "media_1787474759728.pdf", "media_1787474760067.pdf", "media_1787474874929.pdf"
]
pages = [20, 27, 41, 40, 40, 39]

for i in range(6):
    new_sources.append({
        "sourceId": f"CCAB2_PART{i+1:02d}",
        "parentSourceId": "CCAB2_SOURCE_SET",
        "filename": ccab2_files[i],
        "pageCount": pages[i],
        "readabilityStatus": "FULLY_READABLE",
        "extractionMethod": "Native Text",
        "provenance": "Replacement source via .user_uploaded",
        "subject": "Geography",
        "sourceType": "KNOWLEDGE"
    })

# Add Fatman Parent + 16 Children
fatman_labels = [
    "Cover, Index, Pages 1-3", "Pages 4-9", "Pages 10-15", "Pages 16-21",
    "Pages 22-27", "Pages 28-33", "Pages 34-39", "Pages 40-45",
    "Pages 46-51", "Pages 52-57", "Pages 58-63", "Pages 64-68",
    "Pages 69-74", "Pages 75-80", "Pages 81-85", "Pages 86-90"
]

for i in range(16):
    new_sources.append({
        "sourceId": f"FATMAN-FRESH-PART{i+1:02d}",
        "parentSourceId": "FATMAN_SOURCE_SET",
        "filename": f"media_fatman_{i+1}.pdf",
        "pageCount": 6 if i not in [11, 14, 15] else 5,
        "readabilityStatus": "FULLY_READABLE",
        "extractionMethod": "Vision_OCR",
        "partLabel": f"Parmar SSC Geography ({fatman_labels[i]})",
        "provenance": "Supplied by User via .user_uploaded",
        "subject": "Geography",
        "sourceType": "KNOWLEDGE"
    })

registry["sources"] = new_sources

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Registry successfully modeled with Parent/Child structures.")
