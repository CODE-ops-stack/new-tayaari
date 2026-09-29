import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}

# Part 2: Pages 4-9 (Geomorphology/Landforms continued)
if "MODULE_PHYSICAL_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"] = {}
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_PHYSICAL_GEOGRAPHY"]["TOPIC_GEOMORPHOLOGY_LANDFORMS"] = {
    "CONCEPT_WEATHERING_AND_EROSION": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN_SOURCE_SET",
        "QUESTION_COVERAGE": "CONFIRMING_COVERAGE"
    }
}

# Part 8: Pages 40-45 (Indian Geography - Drainage/Rivers continued)
if "MODULE_INDIAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"] = {}
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_DRAINAGE_SYSTEM"] = {
    "CONCEPT_PENINSULAR_RIVERS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN_SOURCE_SET",
        "QUESTION_COVERAGE": "CONFIRMING_COVERAGE"
    }
}

# Part 16: Pages 86+ (Human Geography / Miscellaneous)
if "MODULE_HUMAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_HUMAN_GEOGRAPHY"] = {}
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_HUMAN_GEOGRAPHY"]["TOPIC_TRANSPORT_AND_DEMOGRAPHICS"] = {
    "CONCEPT_TRANSPORT_AND_DEMOGRAPHICS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN_SOURCE_SET",
        "QUESTION_COVERAGE": "NEW_COVERAGE"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Syllabus map updated with Parts 2, 8, 16.")
