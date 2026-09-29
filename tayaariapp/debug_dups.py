import re
import difflib

file_path = "c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/assets/consolidated_grounding.md.bak"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's split by "- **Topic**:"
blocks = content.split("- **Topic**:")[1:]
print(f"Total topics: {len(blocks)}")

qs = []
for i, b in enumerate(blocks):
    # Find the question block between ``` and ```
    parts = b.split("```")
    if len(parts) >= 3:
        q_text = parts[1].strip()
        qs.append(q_text)
    else:
        print(f"Block {i} missing code ticks")

print(f"Total questions extracted: {len(qs)}")

dups = 0
seen = []
for q in qs:
    is_dup = False
    for s in seen:
        if min(len(q), len(s)) / max(len(q), len(s)) > 0.8:
            sm = difflib.SequenceMatcher(None, q, s)
            if sm.quick_ratio() > 0.9 and sm.ratio() > 0.9:
                is_dup = True
                break
    if is_dup:
        dups += 1
    else:
        seen.append(q)

print(f"Duplicates found using difflib >90%: {dups}")
