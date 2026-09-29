import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Update map with new coverage from Parmar SSC (Batch 3)
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}
if "MODULE_INDIAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"] = {}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_ISLANDS"] = {
    "CONCEPT_ANDAMAN_LAKSHADWEEP_CHANNELS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH3-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_DRAINAGE_SYSTEM"] = {
    "CONCEPT_HIMALAYAN_RIVERS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH3-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_CITIES_ON_RIVERS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH3-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 3.")
