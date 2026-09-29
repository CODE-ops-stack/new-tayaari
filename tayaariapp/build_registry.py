import os
import json

source_dir = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material"
app_assets_dir = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\app\src\main\assets"

files_to_index = [
    {"filename": "Copy of our environmemnt class 7 - .pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "Earth's Magnetic Field, Dynamo theory, Magnetosphere - PMF IAS (1).pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "Environment (Apr 2025 - Nov 2025)_compressed.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Environment", "exam": ["UPSC"]},
    {"filename": "Fundamental of Physical Geography (Class XI) 2.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Physical Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "Fundamentals of Human Geography (Class XII) 1.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Human Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "GEOGRAPHY 4.0 ENGLISH pdf (2)_new 21.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "geography_questions_in_UPSC_Prelims_05c936a1aa(1).pdf", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "Geogrophy.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "Geomagnetism & Geomagnetic Reversal - UPSC - UPSC Notes A LotusArise IAS.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "India People and Economy (Class XII).pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Indian Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "India Physical Environment (Class XI) 2.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Indian Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "NCERT-Class-10-Geography.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC", "RRB"]},
    {"filename": "NCERT-Class-9-Geography-1.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC", "RRB"]},
    {"filename": "newGeography.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "Practical Work in Geography Part 1.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Practical Geography", "exam": ["UPSC"]},
    {"filename": "Practical Work in Geography Part 2.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Practical Geography", "exam": ["UPSC"]},
    {"filename": "question.pdf", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Mixed", "exam": ["SSC"]},
    {"filename": "social science class 8.pdf", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "VisionIAS Research And Analysis January 2025 Geography (10 Years UPSC PYQ Trend Analysis) (1)_compressed (1).pdf", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "fatman Geography 2nd Edition_Part1 new.pdf", "status": "OCR_RECOVERED", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "BPSC"]},
    {"filename": "fatman Geography 2nd Edition_Part2_new 2.pdf", "status": "OCR_RECOVERED", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "BPSC"]},
    {"filename": "fatman Geography 2nd Edition_Part5.pdf", "status": "OCR_RECOVERED", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "BPSC"]},
    {"filename": "ccab2-geography.pdf", "status": "UNRECOVERABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf", "status": "UNRECOVERABLE", "type": "SPECIALIZED", "subject": "Map Work", "exam": ["UPSC"]},
    {"filename": "fatman Geography 2nd Edition_Part3.pdf", "status": "UNRECOVERABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "BPSC"]},
    {"filename": "fatman Geography 2nd Edition_Part4.pdf", "status": "UNRECOVERABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "BPSC"]},
    {"filename": "consolidated_grounding_merged.md", "status": "FULLY_READABLE", "type": "KNOWLEDGE", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "geography-syllabus.md", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "geography-syllabus-gs.md", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "pyq-analysis-prelims.md", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Geography", "exam": ["UPSC"]},
    {"filename": "examiner-pattern-guide.md", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Geography", "exam": ["UPSC", "SSC"]},
    {"filename": "exam-complexity-profiles.md", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Mixed", "exam": ["UPSC", "SSC"]},
    {"filename": "gap_report.txt", "status": "FULLY_READABLE", "type": "PATTERN", "subject": "Mixed", "exam": ["UPSC"]},
    {"filename": "question_extracted.txt", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Mixed", "exam": ["SSC"]},
    {"filename": "extracted_ssc_qs.json", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Mixed", "exam": ["SSC"]},
    {"filename": "geography_extracted.txt", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Geography", "exam": ["SSC"]},
    {"filename": "geography_extracted_2.txt", "status": "FULLY_READABLE", "type": "EXAM", "subject": "Geography", "exam": ["SSC"]},
]

registry = {"sources": []}

for i, src in enumerate(files_to_index):
    # check in source-material
    path = os.path.join(source_dir, src["filename"])
    if not os.path.exists(path):
        # special case for geomagnetism which might have weird characters
        if "Geomagnetism" in src["filename"]:
            path = os.path.join(source_dir, "Geomagnetism & Geomagnetic Reversal - UPSC - UPSC Notes – LotusArise IAS.pdf")
            if not os.path.exists(path): path = ""
        else:
            path = ""
            
    size = os.path.getsize(path) if path else 0
    
    registry["sources"].append({
        "sourceId": f"SRC-{i+1:03d}",
        "filename": src["filename"],
        "sourceType": src["type"],
        "subject": src["subject"],
        "examRelevance": src["exam"],
        "readabilityStatus": src["status"],
        "extractionMethod": "Tesseract_OCR" if src["status"] == "OCR_RECOVERED" else ("PyMuPDF/Native" if src["status"] == "FULLY_READABLE" else "FAILED"),
        "size": size,
        "pageCount": 0, # Will be populated later if needed
        "provenance": "Supplied by User",
        "knownProblems": "Corrupted/Blank" if src["status"] == "UNRECOVERABLE" else ("Requires OCR" if src["status"] == "OCR_RECOVERED" else "None"),
        "priority": 1 if src["status"] == "FULLY_READABLE" else (2 if src["status"] == "OCR_RECOVERED" else 0)
    })

# Add consolidated_grounding.md from assets
path_assets = os.path.join(app_assets_dir, "consolidated_grounding.md")
registry["sources"].append({
    "sourceId": "SRC-ASSETS-001",
    "filename": "consolidated_grounding.md",
    "sourceType": "KNOWLEDGE",
    "subject": "Geography",
    "examRelevance": ["UPSC", "SSC"],
    "readabilityStatus": "FULLY_READABLE",
    "extractionMethod": "Native",
    "size": os.path.getsize(path_assets) if os.path.exists(path_assets) else 0,
    "pageCount": 0,
    "provenance": "Application Assets",
    "knownProblems": "None",
    "priority": 1
})

with open("source_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Created source_registry.json")
