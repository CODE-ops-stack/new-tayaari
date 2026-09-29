import json

with open(r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()

pdf_count = 0
for line in lines:
    try:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            pdfs_in_prompt = content.count("==Start of PDF==")
            if pdfs_in_prompt > 0:
                print(f"User Input at step {data.get('step_index')}: found {pdfs_in_prompt} PDFs")
                pdf_count += pdfs_in_prompt
    except:
        pass

print(f"Total PDFs found in transcript: {pdf_count}")
