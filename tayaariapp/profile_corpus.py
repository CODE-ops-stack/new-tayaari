import json
import glob
import re

def profile_corpus():
    files = glob.glob("source-material/*.txt")
    
    profile = {
        "files_analyzed": len(files),
        "total_lines": 0,
        "total_characters": 0,
        "unit_counts": {
            "PROSE": 0,
            "HEADING": 0,
            "MCQ_STEM": 0,
            "MCQ_OPTION": 0,
            "TABLE_ROW": 0,
            "METADATA": 0,
            "EXPLANATION": 0,
            "OCR_FRAGMENT": 0
        },
        "approximate_relations": {
            "COMPARISON": 0,
            "CAUSE_EFFECT": 0,
            "DEFINITION": 0,
            "SPATIAL": 0,
            "DISTRIBUTION": 0,
            "NUMERICAL": 0
        }
    }
    
    for fn in files:
        with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            profile["total_lines"] += len(lines)
            
            for line in lines:
                line = line.strip()
                if not line: continue
                profile["total_characters"] += len(line)
                
                # Classification
                if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line):
                    profile["unit_counts"]["MCQ_STEM"] += 1
                elif re.match(r'^\([a-e]\)', line, re.IGNORECASE):
                    profile["unit_counts"]["MCQ_OPTION"] += 1
                elif re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
                    profile["unit_counts"]["EXPLANATION"] += 1
                elif "|" in line:
                    profile["unit_counts"]["TABLE_ROW"] += 1
                elif line.startswith("http") or line.startswith("www") or "Page" in line:
                    profile["unit_counts"]["METADATA"] += 1
                elif len(line.split()) < 4 and line.istitle():
                    profile["unit_counts"]["HEADING"] += 1
                elif len(line) < 15 and not line.endswith("."):
                    profile["unit_counts"]["OCR_FRAGMENT"] += 1
                else:
                    profile["unit_counts"]["PROSE"] += 1
                    
                    # Relation counting
                    lower = line.lower()
                    if any(w in lower for w in ["while", "whereas", "compared to", "unlike", "differs"]):
                        profile["approximate_relations"]["COMPARISON"] += 1
                    if any(w in lower for w in ["because", "due to", "causes", "results in", "leads to"]):
                        profile["approximate_relations"]["CAUSE_EFFECT"] += 1
                    if any(w in lower for w in ["is known as", "refers to", "is defined as"]):
                        profile["approximate_relations"]["DEFINITION"] += 1
                    if any(w in lower for w in ["located in", "borders", "flows through", "originates"]):
                        profile["approximate_relations"]["SPATIAL"] += 1
                    if any(w in lower for w in ["found in", "distributed", "abundant in"]):
                        profile["approximate_relations"]["DISTRIBUTION"] += 1
                    if re.search(r'\d+(\.\d+)?\s*(%)', lower):
                        profile["approximate_relations"]["NUMERICAL"] += 1

    with open("docs/corpus_profile.json", "w", encoding="utf-8") as out:
        json.dump(profile, out, indent=2)

if __name__ == "__main__":
    profile_corpus()
