import fitz
import pytesseract
from PIL import Image

doc = fitz.open(r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\fatman Geography 2nd Edition_Part3.pdf")
try:
    page = doc[5]
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img)
    print("OCR length on Fatman Part 3 Page 5:", len(text))
    print(text[:200])
except Exception as e:
    print(f"Error: {e}")
