import json
from datetime import datetime

# 1. Update source_gap_report.md
gap_content = """# SOURCE GAP REPORT
Updated: {}

## CURRENT GAPS (Real Gaps Only)
1. **Oxford Atlas Missing Pages (Pages 25-45):** 
   - The verified cumulative Atlas coverage is ~110 pages (Reported 101 previously).
   - Pages 25-45 (India States Political & specific regional Indian maps) remain NOT SUPPLIED / UNVERIFIED.
   - Atlas Corpus is NOT 100% complete.
2. **Current Statistical Data:**
   - The 35th Ed. Oxford Atlas uses 2011 Census and 2015 HDR data.
   - J&K is shown as a state, not UTs. 
   - Gaps exist for *current* 2024/2026 political/economic stats.
3. **Historical Unrecoverable Sources:**
   - The original corrupted `oxford-student-atlas-35...` zip and Old Fatman Parts 3 & 4 remain permanently unrecoverable.
"""
with open("source_gap_report.md", "w", encoding="utf-8") as f:
    f.write(gap_content.format(datetime.now().isoformat()))

# 2. Audit staging_batch_1.json
with open("staging_batch_1.json", "r", encoding="utf-8") as f:
    staged = json.load(f)

for q in staged.get("questions", []):
    q["status"] = "REVIEW_REQUIRED"
    q["audit_note"] = "Awaiting cross-source integrity check against Fatman/Atlas. Do not publish."

with open("staging_batch_1.json", "w", encoding="utf-8") as f:
    json.dump(staged, f, indent=2)

print("Artifacts audited and updated.")
