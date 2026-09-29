import json

map_path = "syllabus_knowledge_map.json"
with open(map_path, "r", encoding="utf-8") as f:
    s_map = json.load(f)

# Ensure SSC structures exist
if "EXAM_SSC" not in s_map:
    s_map["EXAM_SSC"] = {"SUBJECT_GEOGRAPHY": {}}
if "MODULE_INDIAN_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"] = {}
if "MODULE_ECONOMIC_GEOGRAPHY" not in s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]:
    s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_ECONOMIC_GEOGRAPHY"] = {}

# Update map with new coverage from Parmar SSC (Batch 6) - Monsoon & Climate
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_CLIMATE"] = {
    "CONCEPT_MONSOON_AND_EL_NINO": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_KOEPPEN_CLASSIFICATION": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

# Update map with new coverage - Vegetation & Soils
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_INDIAN_GEOGRAPHY"]["TOPIC_VEGETATION_AND_SOILS"] = {
    "CONCEPT_FORESTS_AND_GRASSLANDS": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_SOIL_TYPES_AND_CONSERVATION": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

# Update map with new coverage - Agriculture
s_map["EXAM_SSC"]["SUBJECT_GEOGRAPHY"]["MODULE_ECONOMIC_GEOGRAPHY"]["TOPIC_AGRICULTURE"] = {
    "CONCEPT_CROPPING_SEASONS_AND_FARMING_TYPES": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    },
    "CONCEPT_MAJOR_CROPS_AND_IRRIGATION": {
        "THEORY_SUPPORT": "WELL_SUPPORTED",
        "SOURCE": "FATMAN-FRESH-BATCH6-01",
        "QUESTION_COVERAGE": "FORMAT_GAP"
    }
}

with open(map_path, "w", encoding="utf-8") as f:
    json.dump(s_map, f, indent=2)

print("Updated syllabus map for Batch 6.")
