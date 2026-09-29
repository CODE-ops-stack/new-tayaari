import PyPDF2
import sys

def analyze(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            
            # extract text from first few pages
            text = ""
            for i in range(min(5, num_pages)):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + " "
            
            # also extract from middle pages if needed, but first few usually have title/intro
            return num_pages, text[:500].replace('\n', ' ').strip()
    except Exception as e:
        return None, str(e)

files = [
    "/app/applet/source-material/oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf",
    "/app/applet/source-material/Geogrophy.pdf",
    "/app/applet/source-material/GEOGRAPHY 4.0 ENGLISH pdf (2)_new 21.pdf"
]

for fp in files:
    print(f"File: {fp.split('/')[-1]}")
    pages, text = analyze(fp)
    print(f"Pages: {pages}")
    print(f"Content: {text}")
    print("-" * 50)
