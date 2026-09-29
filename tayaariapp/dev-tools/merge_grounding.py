import re

with open('/app/applet/source-material/_backup/consolidated_grounding.md_20260805065828', 'r') as f:
    backup_content = f.read()

with open('/app/applet/source-material/consolidated_grounding.md', 'r') as f:
    current_content = f.read()

# Extract all SSC blocks from backup
ssc_blocks = {}
blocks = re.split(r'\n## (?=\d+\. )', "\n" + backup_content)
for b in blocks:
    if not b.strip(): continue
    topic_match = re.match(r'^(\d+)\.', b)
    if not topic_match: continue
    topic_num = topic_match.group(1)
    
    ssc_idx = b.find("### SSC Stenographer Data")
    if ssc_idx != -1:
        ssc_part = b[ssc_idx:]
        end_idx = ssc_part.find("\n---")
        if end_idx != -1:
            ssc_part = ssc_part[:end_idx]
        ssc_blocks[topic_num] = ssc_part.strip()

# Inject into current
merged_blocks = []
current_blocks = re.split(r'\n## (?=\d+\. )', "\n" + current_content)
for i, b in enumerate(current_blocks):
    if not b.strip(): 
        continue
    m = re.match(r'^(\d+)\.', b)
    if m:
        topic_num = m.group(1)
        ssc_idx = b.find("### SSC Stenographer Data")
        if ssc_idx != -1 and topic_num in ssc_blocks:
            end_idx = b.find("\n---", ssc_idx)
            prefix = b[:ssc_idx]
            suffix = b[end_idx:] if end_idx != -1 else ""
            b = prefix + ssc_blocks[topic_num] + suffix
        merged_blocks.append(b)
    else:
        merged_blocks.append(b)

merged_content = merged_blocks[0]
for b in merged_blocks[1:]:
    merged_content += "\n## " + b
merged_content = merged_content.strip() + "\n"

with open('/app/applet/source-material/consolidated_grounding_merged.md', 'w') as f:
    f.write(merged_content)

# Verify UPSC
upsc_count = merged_content.count("**Question**:")

# Verify SSC
ssc_count = 0
for line in merged_content.split('\n'):
    if line.strip().startswith("> Questions:"):
        ids = line.split("Questions:")[1].split(",")
        ids = [x.strip() for x in ids if x.strip()]
        ssc_count += len(ids)

print(f"UPSC Count: {upsc_count}")
print(f"SSC Count: {ssc_count}")
print(f"Total: {upsc_count + ssc_count}")

