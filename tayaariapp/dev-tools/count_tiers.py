import re

with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

tiers = re.findall(r'- \*\*Tier\*\*: (\w+)', content)
format_types = re.findall(r'- \*\*Format\*\*: ([\w\- ]+)', content)

print(f"Total Tiers found: {len(tiers)}")
print(f"Total Formats found: {len(format_types)}")

from collections import Counter
print("Tiers:", Counter(tiers))
print("Formats:", Counter(format_types))
