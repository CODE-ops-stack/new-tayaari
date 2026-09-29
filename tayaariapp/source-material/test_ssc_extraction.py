import re

with open("source-material/geography_extracted_2.txt", "r") as f:
    text = f.read()

# Let's just find anything matching Q1., 1., Q.1., etc.
for match in re.finditer(r"\n\s*(Q?\.?\s*1\s*\..{0,50})", text, re.IGNORECASE):
    print("Match for 1:", match.group(1))

for match in re.finditer(r"\n\s*(Q?\.?\s*2\s*\..{0,50})", text, re.IGNORECASE):
    print("Match for 2:", match.group(1))

