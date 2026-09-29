import os
import json

directory = r"C:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.user_uploaded"
files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))

ccab2_files = files[:6]
fatman_files = files[6:]

print(f"CCAB2 Files Found: {len(ccab2_files)}")
print(f"Fatman Files Found: {len(fatman_files)}")
