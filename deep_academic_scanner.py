import os
import json
import re

topics_dir = r"c:\Users\harsh\Downloads\tayaari\cloud_data_staging\topics"
anomalies = []
scanned = 0

for t in range(1, 31):
    fpath = os.path.join(topics_dir, f"topic_{t}.json")
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    for q in questions:
        scanned += 1
        qid = q.get("id", "unknown")
        stem = q.get("stem", "")
        options = q.get("options", {})
        correct = q.get("correctAnswer", "")
        expl = q.get("explanation", "")
        tier = q.get("tier", "")
        fmt = q.get("format", "")

        # 1. Check for corrupted characters or unparsed placeholders
        for text, field in [(stem, "stem"), (expl, "explanation")] + [(v, f"opt_{k}") for k, v in options.items()]:
            if "\ufffd" in text:
                anomalies.append((qid, t, f"Contains replacement character \\ufffd in {field}: '{text[:40]}'"))
            if re.search(r"\b(TODO|FIXME|LOREM|IPSUM|PLACEHOLDER)\b", text, re.IGNORECASE):
                anomalies.append((qid, t, f"Contains placeholder text in {field}: '{text[:40]}'"))

        # 2. Check for duplicate options in the same question
        opt_texts = [v.strip().lower() for v in options.values()]
        if len(set(opt_texts)) < 4:
            anomalies.append((qid, t, f"Duplicate option values detected: {options}"))

        # 3. Modern Count consistency check
        # If options are "Only one", "Only two", "All three", "None"
        if "only one" in opt_texts and "only two" in opt_texts and "all three" in opt_texts:
            correct_val = options.get(correct, "").lower()
            expl_lower = expl.lower()
            
            # Check if explanation mentions count
            if "all three statements are correct" in expl_lower or "all three statements reflect" in expl_lower or "all three statements accurately" in expl_lower:
                if "all three" not in correct_val:
                    anomalies.append((qid, t, f"Count mismatch: Explanation says all three correct, but answer is '{correct_val}'"))
            elif "statements 1 and 2 are correct. statement 3 is incorrect" in expl_lower or "only two statements" in expl_lower:
                if "only two" not in correct_val:
                    anomalies.append((qid, t, f"Count mismatch: Explanation says only two correct, but answer is '{correct_val}'"))
            elif "only statement 1 is correct" in expl_lower or "only statement 2 is correct" in expl_lower or "only statement 3 is correct" in expl_lower:
                if "only one" not in correct_val:
                    anomalies.append((qid, t, f"Count mismatch: Explanation says only one correct, but answer is '{correct_val}'"))

        # 4. Memory Lock check
        if "RANKER'S MEMORY LOCK" not in expl and "MEMORY LOCK" not in expl:
            anomalies.append((qid, t, "Missing RANKER'S MEMORY LOCK in explanation"))

print(f"Deep scanned {scanned} questions.")
print(f"Found {len(anomalies)} potential anomalies.")
if anomalies:
    print("\nSample anomalies (up to 30):")
    for a in anomalies[:30]:
        print(f"  [{a[0]} in Topic {a[1]}] {a[2]}")
