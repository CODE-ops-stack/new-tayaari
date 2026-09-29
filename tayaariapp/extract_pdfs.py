import json
import re

path = r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

pdf_blocks = []
for line in lines:
    data = json.loads(line)
    if data.get("type") == "USER_INPUT":
        content = data.get("content", "")
        blocks = re.findall(r"==Start of PDF==.*?==End of PDF==", content, re.DOTALL)
        pdf_blocks.extend(blocks)

print(f"Total PDF blocks found: {len(pdf_blocks)}")

for i, block in enumerate(pdf_blocks):
    # Extract page numbers from the footer (e.g. "160 www.visionias.in", "16 PARMAR SSC")
    # Let's just find all numbers at the beginning of a line that look like page numbers
    pages = re.findall(r"\n(\d{1,3})\s+(?:www\.visionias\.in|PARMAR SSC|GEOGRAPHY)", block)
    if not pages:
        pages = re.findall(r"\n(?:PARMAR SSC)\s+(\d{1,3})", block)
    
    # Let's extract the first 200 chars to see what it is
    preview = block[100:300].replace('\n', ' ').strip()
    print(f"PDF {i+1}:")
    print(f"  Preview: {preview}")
    print(f"  Pages detected: {list(set(pages))[:5]} ... (Total {len(pages)})")
