with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f:
    lines = f.readlines()

import re
terms = [
    'dwarf', 'satellite', 'port', 'longitudinal', 'compressional',
    'mean density', 'rainforest', 'cyclogenesis', 'venus', 'uranus',
    'narmada', 'tapi', 'orion', 'jawaharlal', 'chota nagpur', 'aravalli',
    'syzygy', 'mercury', 'seafloor', 'convectional', 'andaman', 'coriolis',
    'yellow', 'reserves', 'troposphere', 'corona', 'gangetic'
]

for t in terms:
    found = []
    for idx, l in enumerate(lines):
        if re.search(r'\b' + re.escape(t) + r'\b', l, re.IGNORECASE):
            found.append((idx + 1, l.strip()))
    if found:
        print(f"Term '{t}' found in {len(found)} lines:")
        for lineno, line in found:
            print(f"  Line {lineno}: {line[:90]}")
