import re

with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

# Find all SSC blocks
ssc_blocks = {}
current_topic = None
for line in content.split("\n"):
    if line.startswith("## "):
        current_topic = line.strip()
    if "SSC Stenographer Data" in line:
        pass # We'll need a better way to extract SSC blocks per topic

# Let's just extract topics and their SSC data using regex
topics_split = re.split(r"(?m)^## ", content)
for ts in topics_split[1:]:
    lines = ts.split("\n")
    topic_name = lines[0].strip()
    # Find SSC part
    ssc_idx = -1
    for i, l in enumerate(lines):
        if "SSC Stenographer Data" in l:
            ssc_idx = i
            break
    if ssc_idx != -1:
        ssc_blocks[topic_name] = "\n".join(lines[ssc_idx:])

print(f"Found SSC data for {len(ssc_blocks)} topics")
