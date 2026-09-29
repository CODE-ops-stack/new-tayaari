import PyPDF2

path = r"c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ccab2-geography.pdf"
try:
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        print(f"CCAB2 Pages: {len(reader.pages)}")
except Exception as e:
    print(f"Error reading PDF: {e}")
