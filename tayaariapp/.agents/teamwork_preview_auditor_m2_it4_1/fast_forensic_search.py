"""
fast_forensic_search.py
Optimized fast forensic substring / n-gram search of all 111 items against:
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

COMMON_STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had',
    'in', 'on', 'at', 'to', 'from', 'by', 'with', 'of', 'and', 'or', 'that',
    'which', 'who', 'whom', 'this', 'these', 'those', 'its', 'their', 'our',
    'can', 'be', 'into', 'for', 'as', 'than', 'more', 'less', 'such', 'not'
}

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
    'can occur only if', 'and are called', 'is considered to be', 'refers to the',
    'plays a vital role', 'plays a major role'
}


def analyze_file(file_path, items):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    matches = []
    file_name = os.path.basename(file_path)

    for lineno, line in enumerate(lines, 1):
        clean_line = line.strip()
        line_lower = clean_line.lower()
        # Skip pure comment lines
        if clean_line.startswith("#") or clean_line.startswith('"""') or clean_line.startswith("'''"):
            continue

        for it in items:
            it_id = it.get("id")
            it_text = it.get("text", "")
            it_label = it.get("expected_label")
            it_intent = it.get("intent")

            # Check full text containment
            if len(it_text) > 15 and it_text.lower() in line_lower:
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

            # Extract 4-grams and 5-grams
            words = [w.lower() for w in re.split(r'[^a-zA-Z0-9]+', it_text) if w]
            found_for_item = False
            for n in [5, 4]:
                for i in range(len(words) - n + 1):
                    ngram_words = words[i:i+n]
                    # If all words in ngram are stop words, skip
                    if all(w in COMMON_STOP_WORDS for w in ngram_words):
                        continue
                    ngram = " ".join(ngram_words)
                    if ngram in COMMON_STOP_PHRASES:
                        continue
                    if len(ngram) < 14:
                        continue
                    if ngram in line_lower:
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
