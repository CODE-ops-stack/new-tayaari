import json
import re
import os

def check_banned_phrases():
    extractor_path = os.path.join("v13_discovery", "semantic_extractor.py")
    with open(extractor_path, "r", encoding="utf-8") as f:
        extractor_src = f.read()

    banned = [
        'longitudinal compressional',
        'lowest mean density',
        'very big and hot',
        'comprises immense reserves',
        'yellow dwarf',
        'satellite container port',
        'nearly all planets in',
        'denudational process in which',
        'tectonic process of',
        'plunges beneath',
        'transported and deposited by',
        'Geologists|Scientists|Geographers|Plate tectonics'
    ]

    found_banned = []
    for b in banned:
        if b.lower() in extractor_src.lower():
            found_banned.append(b)

    print("=== BANNED PHRASES CHECK ===")
    print(f"Total banned phrases checked: {len(banned)}")
    print(f"Banned phrases found: {found_banned}")

    # Check golden eval set n-grams
    with open(os.path.join("data", "golden_eval_set.json"), "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    
    examples = eval_data.get("examples", [])
    print(f"Total golden examples to check: {len(examples)}")

    # Strip comments from extractor source
    code_lines = [l for l in extractor_src.splitlines() if not l.strip().startswith('#') and not l.strip().startswith('"""')]
    code_text = "\n".join(code_lines).lower()

    # Look for any verbatim phrases of length >= 4 words from eval_set in code_text
    matches = []
    for item in examples:
        text = item.get("source_text", "")
        # Get word sequences
        words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        for i in range(len(words) - 3):
            phrase = " ".join(words[i:i+4])
            # Filter generic english grammatical sequences
            if phrase in [
                "defined the process", "is defined as", "the process which",
                "can divided into", "are classified into two", "the result",
                "located the", "can classified into", "are known the",
                "are called the", "the process whereby", "the process through",
                "the process which", "the form", "the surface the", "the rate",
                "and are called", "the point the", "the total amount",
                "are composed three", "forms part the", "the case",
                "the atmosphere and", "such that the", "the presence",
                "can defined", "refers the", "the following"
            ]:
                continue
            if phrase in code_text:
                matches.append((item.get("id"), phrase))

    print(f"Golden dataset 4-word n-gram matches in extractor code: {len(matches)}")
    for m in matches:
        print(f"  Match: {m}")

    # Also check normalizer.py
    normalizer_path = os.path.join("v13_discovery", "normalizer.py")
    with open(normalizer_path, "r", encoding="utf-8") as f:
        norm_src = f.read()

    norm_banned = [b for b in banned if b.lower() in norm_src.lower()]
    print(f"Banned phrases in normalizer.py: {norm_banned}")

if __name__ == "__main__":
    check_banned_phrases()
