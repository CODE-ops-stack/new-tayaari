import fitz
import pytesseract
from PIL import Image

doc = fitz.open(r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ccab2-geography.pdf")
page = doc[10]
pix = page.get_pixmap(dpi=150)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

text = pytesseract.image_to_string(img)
print(f"Extracted {len(text)} characters from page 10 via OCR:")
print(text[:200])
