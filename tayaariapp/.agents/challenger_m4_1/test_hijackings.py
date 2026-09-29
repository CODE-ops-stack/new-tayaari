import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import OntologyRegistry

reg = OntologyRegistry()
mismatches = []
for cid, cat in reg.categories.items():
    for m in cat.members:
        resolved_cat = reg.find_category_for_entity(m)
        if resolved_cat.category_id != cid:
            mismatches.append((m, cid, resolved_cat.category_id))

print(f"Total member category hijackings: {len(mismatches)}")
for m, expected_cid, actual_cid in mismatches:
    print(f"  Entity '{m}' defined in '{expected_cid}' resolves to '{actual_cid}'")
