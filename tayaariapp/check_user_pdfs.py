import os
import PyPDF2

directory = r"C:\Users\harsh\.gemini\antigravity\brain\5bf0eb04-a07a-444d-95e7-619fe2564e21\.user_uploaded"

pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))

for f in pdf_files:
    path = os.path.join(directory, f)
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            first_page_text = reader.pages[0].extract_text()
            preview = first_page_text[:100].replace('\n', ' ')
            print(f"{f} : {num_pages} pages : {preview}")
    except Exception as e:
        print(f"{f} : Error - {e}")
