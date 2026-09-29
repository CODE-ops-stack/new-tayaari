import re
from v13_discovery.normalizer import LayoutDesegmenter

# Test the heading detection on actual NCERT content
with open('source-material/ncert_xi_physical_geo.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

lines = content.split('\n')

# Check which lines are detected as headings
headings = []
for i, line in enumerate(lines[:500]):
    stripped = line.strip()
    if stripped and len(stripped) < 120:
        if LayoutDesegmenter.is_heading(stripped):
            print(f'Line {i}: {stripped[:80]}')