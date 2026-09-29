#!/usr/bin/env python3
"""
Check the last failing provenance record.
"""

import json
from v13_discovery.provenance import verify_provenance_chain

# Load the generated questions
with open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\generated_questions_1200_clean.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Load corpus
corpus_files = [
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted_2.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_physical_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_india_env.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_human_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_india_economy.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_x_geo.txt',
    r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_ix_geo.txt',
]

corpus_dict = {}
for cf in corpus_files:
    with open(cf, 'rb') as f:
        corpus_dict[cf] = f.read().decode('utf-8', errors='replace')

print(f"Checking {len(questions)} questions...")

failed = []
for i, q in enumerate(questions):
    res = verify_provenance_chain(q['provenance'], source_corpus=corpus_dict)
    if not res.is_valid:
        failed.append((i, q, res))
        print(f"FAILED record {i}:")
        print(f"  ID: {q['id']}")
        print(f"  Stem: {q['stem'][:80]}")
        print(f"  Evidence: {q['provenance'].get('evidenceText', '')[:100]}")
        print(f"  Errors: {res.errors}")
        print(f"  Broken link: {res.broken_link}")
        print(f"  Source file: {q['provenance'].get('sourceFile', '')}")
        print()

print(f"Total failed: {len(failed)}")