import fitz
import pytesseract
from PIL import Image

doc = fitz.open(r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\fatman Geography 2nd Edition_Part1 new.pdf")
page = doc[3]
pix = page.get_pixmap(dpi=150)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
text = pytesseract.image_to_string(img)
print("OCR length on Fatman Part 1 Page 3:", len(text))
print(text[:200])
