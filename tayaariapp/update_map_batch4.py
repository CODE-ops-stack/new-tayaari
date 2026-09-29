import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Update map with new coverage from Parmar SSC (Batch 4)
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}
if "MODULE_PHYSICAL_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"] = {}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"]["TOPIC_SOLAR_SYSTEM"] = {
    "CONCEPT_UNIVERSE_ORIGIN_AND_BODIES": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH4-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_SUN_AND_PLANETS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH4-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 4.")
