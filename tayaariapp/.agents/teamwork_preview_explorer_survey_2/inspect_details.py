import os
import json
import glob

def inspect_more():
    root = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
    
    # 1. Inspect UTF-8 BOM json files
    bom_files = ["corpus_data.json", "theory_nodes.json", "generic_theory_nodes.json"]
    for bf in bom_files:
        path = os.path.join(root, bf)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            print(f"File {bf}: Type={type(data)}, Length={len(data) if isinstance(data, (list, dict)) else 1}")
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:10]}")
            elif isinstance(data, list) and data:
                print(f"  Sample item 0 keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")

    # 2. Inspect extracted_ssc_qs.json
    ssc_path = os.path.join(root, "source-material", "extracted_ssc_qs.json")
    if os.path.exists(ssc_path):
        with open(ssc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"\nextracted_ssc_qs.json: Length={len(data)}, type={type(data)}")
        if isinstance(data, dict):
            first_k = list(data.keys())[0]
            print(f"  First key: {first_k}")
            print(f"  First val sample: {json.dumps(data[first_k], indent=2)[:300]}")
        elif isinstance(data, list) and data:
            print(f"  Sample item 0: {json.dumps(data[0], indent=2)[:300]}")

    # 3. Inspect consolidated_grounding.md structure
    cg_path = os.path.join(root, "source-material", "consolidated_grounding.md")
    with open(cg_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [next(f) for _ in range(50)]
    print("\nconsolidated_grounding.md first 50 lines:")
    for l in lines[:25]:
        print("  |", l.rstrip())

    # 4. Check previous OCR scripts in root
    ocr_scripts = glob.glob(os.path.join(root, "*ocr*.py")) + glob.glob(os.path.join(root, "*fatman*.py")) + glob.glob(os.path.join(root, "*atlas*.py"))
    print("\nExisting OCR / PDF extraction scripts in repo:")
    for os_script in ocr_scripts:
        print(f"  {os.path.basename(os_script)} ({os.path.getsize(os_script)} bytes)")

if __name__ == "__main__":
    inspect_more()
