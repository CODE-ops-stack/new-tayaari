import re

with open('/app/applet/source-material/consolidated_grounding.md', 'r') as f:
    mdContent = "\n" + f.read()

blocks = re.split(r'\n## (?=\d+\. )', mdContent)
print(f"Blocks: {len(blocks)}")
for i in range(1, min(len(blocks), 5)):
    match = re.search(r'^(\d+)\. (.*?)\n', blocks[i])
    if match:
        print(match.group(1), match.group(2))
    else:
        print("No match", repr(blocks[i][:50]))
