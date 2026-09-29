import fitz
import os

source_dir = r"C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material"
targets = [
    "ccab2-geography.pdf",
    "oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf",
    "fatman Geography 2nd Edition_Part1 new.pdf",
    "fatman Geography 2nd Edition_Part2_new 2.pdf",
    "fatman Geography 2nd Edition_Part3.pdf",
    "fatman Geography 2nd Edition_Part4.pdf",
    "fatman Geography 2nd Edition_Part5.pdf"
]

for t in targets:
    path = os.path.join(source_dir, t)
    print(f"\n--- Testing {t} ---")
    try:
        doc = fitz.open(path)
        print(f"Opened successfully. Page count: {len(doc)}")
        if len(doc) > 0:
            pix = doc[0].get_pixmap()
            print(f"Rendered page 0 successfully: {pix.width}x{pix.height}")
    except Exception as e:
        print(f"Failed to open/render: {e}")
