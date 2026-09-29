import json
import re

with open('data/golden_eval_set.json', encoding='utf-8') as f:
    eval_set = json.load(f)

with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f:
    se_code = f.read().lower()

with open('v13_discovery/normalizer.py', encoding='utf-8') as f:
    norm_code = f.read().lower()

KNOWN_VIOLATIONS = {"POS-032", "POS-034", "POS-036", "NEG-021", "NEG-030", "NEG-031", "NEG-033"}

items = [item for item in eval_set['examples'] if item['id'] not in KNOWN_VIOLATIONS]

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or',
    'that', 'which', 'with', 'as', 'by', 'from', 'into', 'through', 'between', 'during', 'under',
    'above', 'below', 'can', 'could', 'may', 'might', 'will', 'would', 'shall', 'should', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'not', 'no', 'also', 'such'
}

suspicious = []

for item in items:
    iid = item['id']
    label = item['expected_label']
    text = item['text']
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())

    for n in range(4, min(12, len(words) + 1)):
        for i in range(len(words) - n + 1):
            sub_words = words[i:i+n]
            # Must have at least 2 non-stopwords
            content_words = [w for w in sub_words if w not in STOPWORDS]
            if len(content_words) < 2:
                continue
            
            phrase = ' '.join(sub_words)
            
            # Check if direct phrase in se_code or norm_code
            if phrase in se_code:
                # ignore if in comments or plural entity recognition
                suspicious.append((iid, label, n, phrase, 'semantic_extractor.py'))
            if phrase in norm_code:
                suspicious.append((iid, label, n, phrase, 'normalizer.py'))

print(f"Total non-violation items checked: {len(items)}")
print(f"Suspicious matches found: {len(suspicious)}")

# Group by item
by_item = {}
for iid, label, n, phrase, target in suspicious:
    by_item.setdefault(iid, []).append((label, n, phrase, target))

for iid, matches in by_item.items():
    # Longest phrase
    max_m = max(matches, key=lambda x: x[1])
    print(f"[{iid}] ({max_m[0]}, n={max_m[1]}): '{max_m[2]}' in {max_m[3]}")
