import sys
sys.path.insert(0, ".")

from v13_discovery.question_synthesizer import OntologyRegistry
from collections import defaultdict

reg = OntologyRegistry()
member_cats = defaultdict(list)
for cid, cat in reg.categories.items():
    for m in cat.members:
        member_cats[m.lower()].append(cid)

collisions = {m: cats for m, cats in member_cats.items() if len(cats) > 1}
print(f"Total duplicate member collisions: {len(collisions)}")
for m, cats in collisions.items():
    print(f"  '{m}': {cats}")
