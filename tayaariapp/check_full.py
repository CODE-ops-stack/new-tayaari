import json

path = r"c:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

count = text.count("==Start of PDF==")
print(f"Total '==Start of PDF==' occurrences: {count}")
