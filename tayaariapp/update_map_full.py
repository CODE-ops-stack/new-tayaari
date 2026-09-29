import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Update map with new coverage from pages 40-78
s_map["EXAM_UPSC"]["SUBJECT_GEOGRAPHY"]["MODULE_CLIMATOLOGY"] = {
    "TOPIC_ATMOSPHERIC_CIRCULATION": {
        "SUBTOPIC_JET_STREAMS": {
            "CONCEPT_ROSSBY_WAVES_AND_BLOCKING": {
                "THEORY_SUPPORT": "WELL_SUPPORTED",
                "PYQ_SUPPORT": "WELL_SUPPORTED",
                "PATTERN_SUPPORT": "WELL_SUPPORTED",
                "QUESTION_COVERAGE": "FORMAT_GAP"
            }
        },
        "SUBTOPIC_WEATHER_HAZARDS": {
            "CONCEPT_BOMB_CYCLONES_AND_CLOUDBURSTS": {
                "THEORY_SUPPORT": "WELL_SUPPORTED",
                "PYQ_SUPPORT": "WELL_SUPPORTED",
                "QUESTION_COVERAGE": "FORMAT_GAP"
            }
        }
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Syllabus map updated with full CCAB2 coverage.")
