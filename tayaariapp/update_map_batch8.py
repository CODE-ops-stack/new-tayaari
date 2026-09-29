import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Ensure SSC structures exist
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}
if "MODULE_WORLD_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_WORLD_GEOGRAPHY"] = {}
if "MODULE_HUMAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_HUMAN_GEOGRAPHY"] = {}

# Update map with new coverage - World Map
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_WORLD_GEOGRAPHY"]["TOPIC_MAPPING"] = {
    "CONCEPT_CONTINENTS_AND_CITIES_ON_RIVERS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH8-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_GEOLOGICAL_TIMESCALE": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH8-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

# Update map with new coverage - Human Geography
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_HUMAN_GEOGRAPHY"]["TOPIC_POPULATION"] = {
    "CONCEPT_DEMOGRAPHIC_TRANSITION_AND_PYRAMIDS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH8-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_HUMAN_GEOGRAPHY"]["TOPIC_SETTLEMENTS"] = {
    "CONCEPT_URBAN_RURAL_CLASSIFICATIONS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH8-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 8.")
