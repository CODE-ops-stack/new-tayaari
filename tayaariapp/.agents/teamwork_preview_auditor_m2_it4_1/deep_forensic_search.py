"""
deep_forensic_search.py
Performs exhaustive matching of all 111 golden evaluation items against:
1. v13_discovery/semantic_extractor.py
2. v13_discovery/normalizer.py
"""

import json
import re
import os

REPO_ROOT = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
SE_PATH = os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py")
NORM_PATH = os.path.join(REPO_ROOT, "v13_discovery", "normalizer.py")
EVAL_PATH = os.path.join(REPO_ROOT, "data", "golden_eval_set.json")

COMMON_STOP_PHRASES = {
    'is defined as', 'can be divided', 'are classified into', 'is the process',
    'the process of', 'as a result', 'results in the', 'the surface of',
    'in the form', 'is an example', 'is one of', 'of the earth', 'on the basis',
    'which of the', 'one of the', 'a result of', 'is known as', 'are known as',
    'classified as', 'divided into', 'is composed of', 'are composed of',
    'part of the', 'member of the', 'the earth s', 'due to the', 'leads to the',
    'occurs when', 'occurs only', 'can occur', 'develops through', 'is caused by',
    'results from', 'according to', 'in order to', 'such as the', 'such as',
    'for example', 'at the same', 'the rate of', 'the amount of', 'the number of',
    'in terms of', 'with respect to', 'is characterized by', 'characterized by',
    'has a', 'has an', 'have a', 'have an', 'is a', 'is an', 'are the',
    'in the', 'on the', 'at the', 'to the', 'from the', 'by the', 'with the'
}


def analyze_file(file_path, items):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    matches = []
    file_name = os.path.basename(file_path)

    for lineno, line in enumerate(lines, 1):
        clean_line = line.strip()
        # Skip pure comment lines
        if clean_line.startswith("#") or clean_line.startswith('"""') or clean_line.startswith("'''"):
            continue

        for it in items:
            it_id = it.get("id")
            it_text = it.get("text", "")
            it_label = it.get("expected_label")
            it_intent = it.get("intent")

            # Check full text containment
            if len(it_text) > 15 and it_text.lower() in clean_line.lower():
                matches.append({
                    "file": file_name,
                    "line": lineno,
                    "item_id": it_id,
                    "label": it_label,
                    "intent": it_intent,
                    "match_type": "full_sentence_match",
                    "matched_text": it_text,
                    "code_line": clean_line
                })
                continue

            # Extract 3, 4, 5-grams
            words = [w for w in re.split(r'[^a-zA-Z0-9]+', it_text) if w]
            for n in [5, 4, 3]:
                found_for_item = False
                for i in range(len(words) - n + 1):
                    ngram = " ".join(words[i:i+n]).lower()
                    if ngram in COMMON_STOP_PHRASES:
                        continue
                    if len(ngram) < 12:  # skip too short
                        continue
                    # Regex match in clean_line
                    # Don't match inside string identifier if regex
                    pat = r'\b' + re.escape(ngram) + r'\b'
                    if re.search(pat, clean_line.lower()):
                        matches.append({
                            "file": file_name,
                            "line": lineno,
                            "item_id": it_id,
                            "label": it_label,
                            "intent": it_intent,
                            "match_type": f"{n}-gram_match",
                            "matched_text": ngram,
                            "code_line": clean_line
                        })
                        found_for_item = True
                        break
                if found_for_item:
                    break

    return matches


def main():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    items = d.get("examples", d.get("items", []))
    print(f"Total evaluation items: {len(items)}")

    se_matches = analyze_file(SE_PATH, items)
    norm_matches = analyze_file(NORM_PATH, items)

    print(f"\n--- MATCHES IN semantic_extractor.py ({len(se_matches)}) ---")
    for m in se_matches:
        print(f"L{m['line']} | {m['item_id']} ({m['label']}/{m['intent']}) | {m['match_type']}: '{m['matched_text']}'")
        print(f"    Code: {m['code_line'][:100]}")

    print(f"\n--- MATCHES IN normalizer.py ({len(norm_matches)}) ---")
    for m in norm_matches:
        print(f"L{m['line']} | {m['item_id']} ({m['label']}/{m['intent']}) | {m['match_type']}: '{m['matched_text']}'")
        print(f"    Code: {m['code_line'][:100]}")


if __name__ == "__main__":
    main()
