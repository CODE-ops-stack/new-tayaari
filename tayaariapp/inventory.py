import os
import glob
import fitz  # PyMuPDF
import json

source_dir = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material"
pdfs = glob.glob(os.path.join(source_dir, "*.pdf"))

report = ["# SOURCE-MATERIAL INVENTORY REPORT\n\n"]
report.append("## 1. PDF Analysis\n\n")

total_pdfs = 0
for pdf_path in pdfs:
    filename = os.path.basename(pdf_path)
    file_size_bytes = os.path.getsize(pdf_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    total_pdfs += 1
    
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        
        # Extract text from up to 20 pages to sample
        text_length = 0
        extracted_text = ""
        sample_pages = min(20, page_count)
        
        for i in range(sample_pages):
            page = doc[i]
            text = page.get_text("text")
            if text:
                extracted_text += text
                text_length += len(text)
        
        extraction_success = "YES" if text_length > 0 else "NO"
        
        # Estimate total readable text
        avg_text_per_page = text_length / sample_pages if sample_pages > 0 else 0
        approx_total_text = int(avg_text_per_page * page_count)
        
        # Determine extraction problems
        problem = "none"
        if extraction_success == "YES" and avg_text_per_page < 50:
            problem = "scanned/image-only"
        elif doc.is_encrypted:
            problem = "password protected"
        
        # Classification
        lower_text = extracted_text.lower()
        lower_name = filename.lower()
        classification = "other"
        
        if "ncert" in lower_name or "class " in lower_name or "chapter" in lower_text[:1000]:
            classification = "textbook"
        elif "pyq" in lower_name or "previous year" in lower_text or "question" in lower_name:
            classification = "PYQ"
        elif "syllabus" in lower_name or "syllabus" in lower_text[:500]:
            classification = "syllabus"
        elif "current affairs" in lower_name or "visionias" in lower_name:
            classification = "current affairs"
        elif "atlas" in lower_name or "map" in lower_name:
            classification = "atlas/map material"
        elif "trend" in lower_name or "analysis" in lower_name:
            classification = "analysis/trend material"
        elif "geography" in lower_name:
            classification = "textbook"
            
        doc.close()
        
    except Exception as e:
        page_count = "Error"
        extraction_success = "NO"
        approx_total_text = 0
        classification = "Unknown"
        problem = f"corrupted/error ({str(e)})"

    report.append(f"### {filename}\n")
    report.append(f"- **File size**: {file_size_mb:.2f} MB\n")
    report.append(f"- **Page count**: {page_count}\n")
    report.append(f"- **Text extraction succeeds**: {extraction_success}\n")
    report.append(f"- **Approx readable text length**: {approx_total_text} characters\n")
    report.append(f"- **Primary classification**: {classification}\n")
    report.append(f"- **Extraction problem**: {problem}\n\n")

report.append("## 2. Supporting Files Inventory\n\n")
supporting_files = []
for ext in ["md", "json", "csv", "txt", "py", "js"]:
    supporting_files.extend(glob.glob(os.path.join(source_dir, f"*.{ext}")))

for sf in supporting_files:
    fname = os.path.basename(sf)
    fsize = os.path.getsize(sf) / 1024
    report.append(f"- `{fname}` ({fsize:.1f} KB)\n")

with open("inventory_report.md", "w", encoding="utf-8") as f:
    f.writelines(report)

print("Inventory generated.")
