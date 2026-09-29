import re
import os

sources = [
    "source-material/geography_extracted.txt",
    "source-material/geography_extracted_2.txt",
    "source-material/question_extracted.txt",
    "source-material/supplementary_corpus.txt"
]

for src in sources:
    if os.path.exists(src):
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"File: {src} -> {len(lines)} lines, {sum(len(l) for l in lines)} bytes")
