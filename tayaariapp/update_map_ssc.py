import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Update map with new coverage from Parmar SSC
s_map["EXAM_SSC"] = {
    "SUBJECT_GEOGRAPHY": {
        "MODULE_GEOMORPHOLOGY": {
            "TOPIC_WEATHERING_AND_EROSION": {
                "CONCEPT_WEATHERING_TYPES": {
                    "THEORY_SUPPORT": "WELL_SUPPORTED",
                    "SOURCE": "FATMAN-FRESH-BATCH1-01",
                    "QUESTION_COVERAGE": "FORMAT_GAP"
                }
            },
            "TOPIC_LANDFORMS": {
                "CONCEPT_FLUVIAL_GLACIAL_KARST": {
                    "THEORY_SUPPORT": "WELL_SUPPORTED",
                    "SOURCE": "FATMAN-FRESH-BATCH1-01",
                    "QUESTION_COVERAGE": "FORMAT_GAP"
                }
            }
        }
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map.")
