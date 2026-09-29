import fitz
import pytesseract
from PIL import Image
def test(path):
    doc = fitz.open(path)
    page = doc[3]
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return len(pytesseract.image_to_string(img))
    
p2 = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\fatman Geography 2nd Edition_Part2_new 2.pdf"
p5 = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\fatman Geography 2nd Edition_Part5.pdf"

print("Part 2:", test(p2))
print("Part 5:", test(p5))
