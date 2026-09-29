import re

def search_in_file(filepath, pattern, max_matches=5):
    matches = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            matches.append((idx + 1, line.strip()))
            if len(matches) >= max_matches:
                break
    return matches

patterns = {
    "definition": r'\b(is known as|refers to|is defined as|called)\b',
    "comparison": r'\b(whereas|differs from|unlike|as compared to|greater than)\b',
    "cause_effect": r'\b(causes|leads to|results in|due to|caused by|because)\b',
    "spatial": r'\b(flows through|originates in|located in|situated in|lies between)\b',
    "distribution": r'\b(abundant in|concentrated in|widely distributed|found in)\b',
    "classification": r'\b(classified into|types of|categories|broad groups)\b',
    "quantity": r'\b(\d+\s*(percent|%|km|kilometers|metres|degrees))\b',
    "sequence": r'\b(first|second|stage|sequence|followed by)\b',
    "condition": r'\b(occurs when|only when|depends on|in the presence of)\b',
    "exception": r'\b(except|uniquely|the only|with the exception of)\b',
    "process": r'\b(weathering|erosion|subduction|deposition|photosynthesis)\b',
    "part_of": r'\b(part of|layer of|component of|constituent of)\b',
    "member_of": r'\b(is an example of|tributary of|is one of the|belongs to)\b',
    "attribute": r'\b(is characterized by|features|consists of|has a high)\b'
}

for intent, pat in patterns.items():
    res = search_in_file("source-material/question_extracted.txt", pat, 3)
    print(f"=== INTENT: {intent} ===")
    for line_no, text in res:
        print(f"  q_ext:{line_no} -> {text[:100]}")
