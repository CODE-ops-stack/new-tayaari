import json
import os

pdf_count = 0
supp_count = 0
for root, dirs, files in os.walk(r"c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material"):
    for f in files:
        if f.endswith('.pdf'):
            pdf_count += 1
        elif f.endswith('.md') or f.endswith('.json') or f.endswith('.txt'):
            supp_count += 1

print(f"Total PDFs in directory: {pdf_count}")
print(f"Total supporting files in directory: {supp_count}")

with open("source_registry.json", "r", encoding="utf-8") as f:
    reg = json.load(f)

ccab_count = sum(1 for s in reg['sources'] if 'ccab2' in s['filename'].lower())
fresh_fatman_count = sum(1 for s in reg['sources'] if 'FATMAN-FRESH' in s['sourceId'])
historical_fatman_count = sum(1 for s in reg['sources'] if 'fatman' in s['filename'].lower() and 'FATMAN-FRESH' not in s['sourceId'])
unrecoverable_count = sum(1 for s in reg['sources'] if s['readabilityStatus'] == 'UNRECOVERABLE')

print(f"CCAB2 Count: {ccab_count}")
print(f"Fresh Fatman Count: {fresh_fatman_count}")
print(f"Historical Fatman Count: {historical_fatman_count}")
print(f"Unrecoverable Count: {unrecoverable_count}")
