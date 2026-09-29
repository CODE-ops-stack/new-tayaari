import re

path = r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Just split by "==Start of PDF==" and then find the next "==End of PDF=="
chunks = text.split("==Start of PDF==")[1:]

print(f"Total blocks found: {len(chunks)}")
for i, chunk in enumerate(chunks):
    end_idx = chunk.find("==End of PDF==")
    if end_idx != -1:
        block = chunk[:end_idx]
        screenshots = re.findall(r"==Screenshot for page (\d+)==", block)
        print(f"Block {i+1}: {len(screenshots)} screenshots. Pages: {', '.join(screenshots[:5])}{'...' if len(screenshots)>5 else ''}")
        
        # Try to find some OCR text to identify what this block actually is
        # Just grab the first 100 characters after the first Screenshot tag
        first_screen_idx = block.find("==Screenshot for page 1==")
        if first_screen_idx != -1:
            preview = block[first_screen_idx:first_screen_idx+500].replace('\n', ' ')
            # Use regex to find page numbers in the text
            p_nums = re.findall(r"\s(\d{1,3})\s+(?:www\.visionias\.in|PARMAR SSC|GEOGRAPHY|VISION IAS)", preview)
            if not p_nums:
                 p_nums = re.findall(r"(?:PARMAR SSC|GEOGRAPHY|VISION IAS)\s+(\d{1,3})\s", preview)
            print(f"   Preview numbers detected: {p_nums}")
    else:
        print(f"Block {i+1}: No End of PDF found")
