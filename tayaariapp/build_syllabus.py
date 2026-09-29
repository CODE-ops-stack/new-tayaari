import json
import os
import re

syllabus_map = {
    "EXAM_UPSC": {
        "SUBJECT_GEOGRAPHY": {
            "MODULE_PHYSICAL_GEOGRAPHY": {
                "TOPIC_GEOMORPHOLOGY": {
                    "SUBTOPIC_FORCES": {
                        "CONCEPT_ENDOGENETIC_AND_EXOGENETIC": {
                            "THEORY_SUPPORT": "WELL_SUPPORTED",
                            "PYQ_SUPPORT": "WELL_SUPPORTED",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "FORMAT_GAP"
                        }
                    },
                    "SUBTOPIC_TECTONICS": {
                        "CONCEPT_CONTINENTAL_DRIFT": {
                            "THEORY_SUPPORT": "WELL_SUPPORTED",
                            "PYQ_SUPPORT": "WELL_SUPPORTED",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "WELL_SUPPORTED"
                        },
                        "CONCEPT_PLATE_TECTONICS": {
                            "THEORY_SUPPORT": "WELL_SUPPORTED",
                            "PYQ_SUPPORT": "WELL_SUPPORTED",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "WELL_SUPPORTED"
                        }
                    }
                },
                "TOPIC_CLIMATOLOGY": {
                    "SUBTOPIC_CIRCULATION": {
                        "CONCEPT_MONSOONS_AND_JET_STREAMS": {
                            "THEORY_SUPPORT": "WELL_SUPPORTED",
                            "PYQ_SUPPORT": "WELL_SUPPORTED",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "WELL_SUPPORTED"
                        }
                    }
                }
            },
            "MODULE_INDIAN_GEOGRAPHY": {
                "TOPIC_BASICS": {
                    "SUBTOPIC_LOCATION": {
                        "CONCEPT_MAPS_AND_LATITUDES": {
                            "THEORY_SUPPORT": "SOURCE_GAP",
                            "PYQ_SUPPORT": "SOURCE_GAP",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "SOURCE_GAP"
                        }
                    }
                }
            },
            "MODULE_UNIVERSE_AND_EARTH": {
                "TOPIC_COSMOLOGY": {
                    "SUBTOPIC_UNIVERSE": {
                        "CONCEPT_UNIVERSE_HIERARCHY": {
                            "THEORY_SUPPORT": "WELL_SUPPORTED",
                            "PYQ_SUPPORT": "INSUFFICIENT_DATA",
                            "PATTERN_SUPPORT": "WELL_SUPPORTED",
                            "CURRENT_AFFAIRS_SUPPORT": "INSUFFICIENT_DATA",
                            "QUESTION_COVERAGE": "QUESTION_GAP"
                        }
                    }
                }
            }
        }
    }
}

with open("syllabus_knowledge_map.json", "w", encoding="utf-8") as f:
    json.dump(syllabus_map, f, indent=2)

print("Created syllabus_knowledge_map.json")
