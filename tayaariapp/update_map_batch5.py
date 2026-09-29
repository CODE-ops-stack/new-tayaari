import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Ensure SSC structures exist
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}
if "MODULE_PHYSICAL_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"] = {}
if "MODULE_INDIAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"] = {}

# Update map with new coverage from Parmar SSC (Batch 5) - Geomorphology Basics
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"]["TOPIC_GEOMORPHOLOGY_BASICS"] = {
    "CONCEPT_EARTHS_INTERIOR_AND_TECTONICS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH5-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_ROCKS_AND_VOLCANOES": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH5-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_EARTHQUAKES": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH5-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

# Update map with new coverage from Parmar SSC (Batch 5) - Indian Drainage and Lakes
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_PENINSULAR_DRAINAGE"] = {
    "CONCEPT_EAST_AND_WEST_FLOWING_RIVERS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH5-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_WATER_BODIES"] = {
    "CONCEPT_DAMS_WATERFALLS_AND_LAKES": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH5-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 5.")
