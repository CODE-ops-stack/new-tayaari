import re

def search_in_file(filepath, pattern, max_matches=10):
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
    "definition": r'\b(is called|are called|is known as|refers to|is defined as)\b',
    "comparison": r'\b(whereas|while|as compared to|differs from|unlike)\b',
    "cause_effect": r'\b(because|leads to|results in|due to|caused by|therefore)\b',
    "spatial": r'\b(located in|situated in|flows through|borders|bounded by|lies between)\b',
    "distribution": r'\b(found in|distributed across|widespread in|abundant in|concentration of|density)\b',
    "classification": r'\b(classified into|divided into|types of|categories of|three broad)\b',
    "quantity": r'\b(\d+\s*(percent|%|kilometres|km|meters|degrees|billion|million))\b',
    "sequence": r'\b(followed by|subsequently|first|second|then|stages|cycle)\b',
    "condition": r'\b(provided that|occurs when|only if|depends upon|subject to)\b',
    "exception": r'\b(except|with the exception|uniquely|only planet|rarely)\b',
    "process": r'\b(process of|evaporation|condensation|subduction|weathering|erosion)\b',
    "part_of": r'\b(part of|consists of|composed of|forms the outer|layers of)\b',
    "member_of": r'\b(is an example of|one such|is a tributary of|is one of the)\b'
}

for intent, pat in patterns.items():
    res1 = search_in_file("source-material/geography_extracted.txt", pat, 3)
    res2 = search_in_file("source-material/geography_extracted_2.txt", pat, 3)
    print(f"=== INTENT: {intent} ===")
    for line_no, text in res1:
        print(f"  geo1:{line_no} -> {text[:100]}")
    for line_no, text in res2:
        print(f"  geo2:{line_no} -> {text[:100]}")
