import os
import re

root = r"c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material"

def find_evidence():
    evidence = {}
    
    # 1. OCR Noise in question_extracted.txt
    q_file = os.path.join(root, "question_extracted.txt")
    with open(q_file, "r", encoding="utf-8", errors="ignore") as f:
        q_lines = f.readlines()
        
    ocr_noise = []
    watermark_noise = []
    multi_word = []
    for idx, line in enumerate(q_lines, 1):
        if "www.ssccglpinnacle.com" in line or "Download Pinnacle Exam Preparation App" in line:
            if len(watermark_noise) < 3:
                watermark_noise.append((idx, line.strip()))
        if re.search(r'\s{3,}', line) and len(line.strip()) > 30:
            if len(ocr_noise) < 3:
                ocr_noise.append((idx, line.strip()))
        if "Inter-Tropical Convergence Zone" in line or "Jawaharlal Nehru Port" in line or "Indian Meteorological Department" in line:
            if len(multi_word) < 4:
                multi_word.append((idx, line.strip()))

    evidence["watermark_noise"] = watermark_noise
    evidence["ocr_double_space_noise"] = ocr_noise
    evidence["multi_word"] = multi_word

    # 2. Multi-column wrap in geography_extracted_2.txt
    g2_file = os.path.join(root, "geography_extracted_2.txt")
    with open(g2_file, "r", encoding="utf-8", errors="ignore") as f:
        g2_lines = f.readlines()
    evidence["column_wrap"] = [(i, g2_lines[i-1].strip()) for i in range(3, 18)]

    # 3. Tables in consolidated_grounding.md
    cg_file = os.path.join(root, "consolidated_grounding.md")
    with open(cg_file, "r", encoding="utf-8", errors="ignore") as f:
        cg_lines = f.readlines()
    table_lines = []
    for idx, line in enumerate(cg_lines, 1):
        if "|" in line:
            table_lines.append((idx, line.strip()))
            if len(table_lines) >= 5:
                break
    evidence["tables"] = table_lines

    # 4. Non-SVO sentences in geography_extracted.txt (NCERT Class 6)
    g_file = os.path.join(root, "geography_extracted.txt")
    with open(g_file, "r", encoding="utf-8", errors="ignore") as f:
        g_lines = f.readlines()
    g_non_svo = []
    for idx, line in enumerate(g_lines, 1):
        if any(term in line.lower() for term in ["are called", "made up of", "provided it is", "full moon night or poornima"]):
            g_non_svo.append((idx, line.strip()))
            if len(g_non_svo) >= 5:
                break
    evidence["non_svo"] = g_non_svo

    for k, v in evidence.items():
        print(f"=== {k} ===")
        for item in v:
            print(f"  Line {item[0]}: {item[1]}")

if __name__ == "__main__":
    find_evidence()
