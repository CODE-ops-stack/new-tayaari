import re

path = r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

blocks = re.findall(r"==Start of PDF==(.*?)(?:==End of PDF==)", text, re.DOTALL)
print(f"Total PDF blocks found: {len(blocks)}")

for i, block in enumerate(blocks):
    print(f"\nPDF {i+1} Length: {len(block)}")
    
    # Try to extract "Screenshot for page X" count
    screenshots = re.findall(r"==Screenshot for page (\d+)==", block)
    print(f"Screenshots: {len(screenshots)} (Pages: {', '.join(screenshots[:5])}{'...' if len(screenshots)>5 else ''})")
    
    # Try to extract the first 100 characters of OCR text if present
    ocr_start = block.find("==Start of OCR")
    if ocr_start != -1:
        ocr_text = block[ocr_start:ocr_start+200].replace('\n', ' ')
        print(f"OCR Preview: {ocr_text}")
    else:
        print("No OCR text blocks found in this PDF.")
