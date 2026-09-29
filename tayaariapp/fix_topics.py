import re

md_path = "/app/applet/source-material/consolidated_grounding.md"
with open(md_path, 'r') as f:
    content = f.read()

# Split into blocks by "## "
parts = re.split(r'(\r?\n## )', content)

# parts[0] is everything before the first "## "
# parts[1] is "\n## "
# parts[2] is the first block content, etc.

topic_blocks = {}
for i in range(2, len(parts), 2):
    header_and_content = parts[i]
    m = re.match(r'^(\d+)\. (.*)', header_and_content)
    if m:
        tNum = int(m.group(1))
        topic_blocks[tNum] = parts[i]

if 100 not in topic_blocks:
    print("Block 100 not found!")
    exit(1)

block_100 = topic_blocks[100]

# Regex to match each question block within 100.
q_pattern = re.compile(
    r'(- \*\*Topic\*\*: 100\. Recovered Questions\r?\n' +
    r'- \*\*Tier\*\*: .*?\r?\n' +
    r'- \*\*Format\*\*: .*?\r?\n' +
    r'- \*\*Exam-Relevance\*\*: .*?\r?\n' +
    r'- \*\*Source\*\*: .*?\r?\n' +
    r'- \*\*Specific-Exam\*\*: .*?\r?\n' +
    r'(?:- \*\*Trap-Type\*\*: .*?\r?\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (.*?)\r?\n' +
    r'- \*\*Question\*\*:\r?\n```\r?\n.*?\r?\n```)', re.DOTALL
)

mapping = {
    '50': 26,
    '74': 20,
    '188': 25,
    '189': 13,
    '296': 41,
    '314': 39,
    '354': 39,
    '406': 27,
    '438': 27,
    '489': 17,
    '613': 43,
    '766': 11,
    '802': 14,
    '838': 11,
    '915': 22
}

topic_names = {
    11: "11. Interior of the Earth",
    13: "13. Geomorphic Processes",
    14: "14. Landforms and their Evolution",
    17: "17. Atmospheric Circulation and Weather Systems",
    20: "20. Water (Oceans)",
    22: "22. Biodiversity and Conservation",
    25: "25. Drainage System",
    26: "26. Climate",
    27: "27. Natural Vegetation",
    39: "39. Land Resources and Agriculture",
    41: "41. Mineral and Energy Resources",
    43: "43. Transport and Communication (India)"
}

matches = q_pattern.findall(block_100)
print(f"Found {len(matches)} questions in block 100")

questions_to_add = {k: [] for k in topic_names.keys()}

for full_match, seq_num in matches:
    seq = seq_num.strip()
    target_topic = mapping.get(seq)
    if target_topic:
        # replace the topic line
        new_topic_line = f"- **Topic**: {topic_names[target_topic]}"
        modified_match = re.sub(r'- \*\*Topic\*\*: 100\. Recovered Questions', new_topic_line, full_match)
        questions_to_add[target_topic].append(modified_match)
        print(f"Moved Q{seq} to Topic {target_topic}")
    else:
        print(f"WARNING: No mapping for Q{seq}")

# Now build the new content
new_parts = [parts[0]]

for i in range(2, len(parts), 2):
    header_and_content = parts[i]
    m = re.match(r'^(\d+)\. (.*)', header_and_content)
    if m:
        tNum = int(m.group(1))
        if tNum == 100:
            continue # skip the 100 block
        
        block_text = header_and_content
        if tNum in questions_to_add and len(questions_to_add[tNum]) > 0:
            # Append the questions to this block
            # First, check if block ends with \n or not
            if not block_text.endswith("\n"):
                block_text += "\n"
            
            for q in questions_to_add[tNum]:
                block_text += q + "\n"
        
        new_parts.append(parts[i-1]) # "\n## "
        new_parts.append(block_text)

with open(md_path, 'w') as f:
    f.write("".join(new_parts))

print("Successfully written to", md_path)
