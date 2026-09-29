import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Update map with new coverage from Parmar SSC (Batch 2)
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_CLIMATOLOGY"] = {
    "TOPIC_ATMOSPHERE": {
        "CONCEPT_LAYERS_AND_COMPOSITION": {
            "THEORY_SUPPORT": "WELL_SUPPORTED",
            "SOURCE": "FATMAN-FRESH-BATCH2-01",
            "QUESTION_COVERAGE": "FORMAT_GAP"
        }
    },
    "TOPIC_WINDS_AND_CYCLONES": {
        "CONCEPT_LOCAL_WINDS_AND_CYCLONES": {
            "THEORY_SUPPORT": "WELL_SUPPORTED",
            "SOURCE": "FATMAN-FRESH-BATCH2-01",
            "QUESTION_COVERAGE": "FORMAT_GAP"
        }
    }
}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"] = {
    "TOPIC_LOCATION_AND_BORDERS": {
        "CONCEPT_NEIGHBOURS_AND_COASTLINE": {
            "THEORY_SUPPORT": "WELL_SUPPORTED",
            "SOURCE": "FATMAN-FRESH-BATCH2-01",
            "QUESTION_COVERAGE": "FORMAT_GAP"
        }
    },
    "TOPIC_PHYSIOGRAPHY": {
        "CONCEPT_HIMALAYAS_AND_PASSES": {
            "THEORY_SUPPORT": "WELL_SUPPORTED",
            "SOURCE": "FATMAN-FRESH-BATCH2-01",
            "QUESTION_COVERAGE": "FORMAT_GAP"
        }
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 2.")
