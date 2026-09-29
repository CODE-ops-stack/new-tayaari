import json
import os

registry_path = "source_registry.json"

# 1. Update source_registry.json
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

for src in registry["sources"]:
    if "ccab2" in src["filename"].lower():
        src["readabilityStatus"] = "FULLY_READABLE"
        src["extractionMethod"] = "Native Replacement"
        src["knownProblems"] = "None"
        src["priority"] = 1
        src["coverageNotes"] = "Comprehensive UPSC Mains GS1 Geography VAM. Covers Geomorphology, Climatology, Oceanography, Indian Physiography, Resources, and Industries. Includes PYQ Analysis."
        src["sourceType"] = "KNOWLEDGE + PATTERN"

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

# 2. Update source_gap_report.md
gap_report_path = "source_gap_report.md"
with open(gap_report_path, "r", encoding="utf-8") as f:
    gap_report = f.read()

# Add a section for the newly recovered material
new_gap_report = gap_report + "\n\n## 4. Indian Physiography & Economic Geography\n- **Evidence Status:** WELL_SUPPORTED\n- **Contributing Sources:** ccab2-geography.pdf (Replacement VAM).\n- **Format Gaps:** Needs to be integrated into question pipeline.\n- **Action:** Approved for question generation."

with open(gap_report_path, "w", encoding="utf-8") as f:
    f.write(new_gap_report)

# 3. Update exam_question_design_profiles.md
profile_path = "exam_question_design_profiles.md"
with open(profile_path, "r", encoding="utf-8") as f:
    profiles = f.read()

if "ccab2-geography.pdf" not in profiles:
    profiles += "\n\n## Updates from CCAB2 Recovery\n- **UPSC PYQ Insights**: UPSC GS questions go beyond textbook location theories (e.g., 'why industries are moving' rather than just 'where they are'). Questions demand structural & geomorphic logic, human-landform interaction, and ecosystem linkages."
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(profiles)

print("Artifacts updated.")
