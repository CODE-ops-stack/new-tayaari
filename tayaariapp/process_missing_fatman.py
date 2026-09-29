import os
import PyPDF2

directory = r"C:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.user_uploaded"
files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))

fatman_files = files[6:]
target_parts = {
    2: fatman_files[1],
    8: fatman_files[7],
    16: fatman_files[15]
}

for part_num, filename in target_parts.items():
    path = os.path.join(directory, filename)
    print(f"--- FATMAN PART {part_num} : {filename} ---")
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            print(f"Total Pages: {len(reader.pages)}")
            text = ""
            for i in range(min(3, len(reader.pages))):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                print(f"Extracted Text Snippet: {text[:300].replace(chr(10), ' ')}")
            else:
                print("No extractable text layer found (Image-based). Requires Vision/OCR.")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
