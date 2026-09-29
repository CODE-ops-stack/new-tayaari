import re
import json

with open('dev-tools/extracted.txt', 'r') as f:
    content = f.read()

missing_seqs = [50, 74, 188, 189, 296, 314, 354, 406, 438, 489, 613, 766, 802, 838, 915]
recovered = []

for seq in missing_seqs:
    # Look for Q.50. or Q.50 . or Q 50.
    pattern = re.compile(rf'(Q\.?\s*{seq}\s*\..*?)(?=Q\.?\s*\d+\s*\.|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(content)
    if match:
        text = match.group(1).strip()
        # the text ends right before the next Q. We need to truncate at Sol.XXX if there's trailing stuff, or we can just keep it.
        # usually it ends after Sol.<seq>. .... Let's try to capture up to the end of Sol.
        clean_text = re.sub(r'\n+', ' ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        print(f"--- Q{seq} ---")
        print(clean_text[:500] + ("..." if len(clean_text) > 500 else ""))
        recovered.append((seq, clean_text))
    else:
        print(f"NOT FOUND: Q{seq}")

print(f"\nFound {len(recovered)} out of {len(missing_seqs)}")

with open('dev-tools/recovered.json', 'w') as f:
    json.dump([{'seq': s, 'text': t} for s, t in recovered], f)
