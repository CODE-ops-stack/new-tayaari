import re
import json

with open('dev-tools/extracted.txt', 'r') as f:
    content = f.read()

missing_seqs = [50, 74, 188, 189, 296, 314, 354, 406, 438, 489, 613, 766, 802, 838, 915]
found_qs = []

for seq in missing_seqs:
    pattern = re.compile(rf'(Q{seq}\..*?Correct answer:.*?)(?=Q\d+\.|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(content)
    if match:
        text = match.group(1).strip()
        found_qs.append((seq, text))
    else:
        pattern_fallback = re.compile(rf'(Q{seq}\..*?)(?=Q\d+\.|$)', re.DOTALL)
        match_fb = pattern_fallback.search(content)
        if match_fb:
            text = match_fb.group(1).strip()
            found_qs.append((seq, text))

recovered = []
for seq, text in found_qs:
    clean_text = re.sub(r'\n+', '\n', text)
    print(f"--- Q{seq} ---")
    print(clean_text)
    recovered.append((seq, clean_text))
    
print(f"\nFound {len(recovered)} out of {len(missing_seqs)}")

with open('dev-tools/recovered.json', 'w') as f:
    json.dump([{'seq': s, 'text': t} for s, t in recovered], f)
