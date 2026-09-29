import json

path = r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

count = text.count("==Start of PDF==")
print(f"Total '==Start of PDF==' occurrences: {count}")

blocks = text.split("==Start of PDF==")[1:]
for i, block in enumerate(blocks):
    end_idx = block.find("==End of PDF==")
    if end_idx != -1:
        pdf_content = block[:end_idx]
        screenshots = pdf_content.count("==Screenshot for page")
        print(f"PDF Block {i+1}: {screenshots} screenshots")
    else:
        print(f"PDF Block {i+1}: No End of PDF found")
