import json

pyq_index = {
    "collections": [
        {
            "collectionId": "PYQ-UPSC-PRELIMS-001",
            "sourceFile": "geography_questions_in_UPSC_Prelims_05c936a1aa(1).pdf",
            "exam": "UPSC",
            "paper": "Prelims GS1",
            "provenanceConfidence": "HIGH",
            "knownFormats": ["Multi-statement", "Assertion-Reasoning", "Map-based"],
            "difficultyProxies": ["High cognitive demand", "Deep elimination"],
            "topicsCovered": ["Geomorphology", "Climatology", "Oceanography", "Indian Geography"]
        },
        {
            "collectionId": "PYQ-SSC-001",
            "sourceFile": "extracted_ssc_qs.json",
            "exam": "SSC CGL",
            "paper": "Tier 1/2",
            "provenanceConfidence": "HIGH",
            "knownFormats": ["Direct Recall", "Single-statement"],
            "difficultyProxies": ["Factual trivia", "Rapid decision"],
            "topicsCovered": ["General Geography", "Indian Rivers", "Dams", "Demographics"]
        }
    ]
}

with open("pyq_index.json", "w", encoding="utf-8") as f:
    json.dump(pyq_index, f, indent=2)

print("Created pyq_index.json")
