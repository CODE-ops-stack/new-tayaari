import json

topics = [
"1. The Earth in the Solar System", "2. Globe: Latitudes and Longitudes", "3. Motions of the Earth", "4. Maps",
"5. Major Domains of the Earth", "6. Major Landforms of the Earth", "7. Our Country - India",
"8. India: Climate, Vegetation and Wildlife", "9. Geography as a Discipline", "10. The Origin and Evolution of the Earth",
"11. Interior of the Earth", "12. Distribution of Oceans and Continents", "13. Geomorphic Processes",
"14. Landforms and their Evolution", "15. Composition and Structure of Atmosphere",
"16. Solar Radiation, Heat Balance and Temperature", "17. Atmospheric Circulation and Weather Systems",
"18. Water in the Atmosphere", "19. World Climate and Climate Change", "20. Water (Oceans)",
"21. Movements of Ocean Water", "22. Biodiversity and Conservation", "23. India - Location",
"24. Structure and Physiography", "25. Drainage System", "26. Climate", "27. Natural Vegetation",
"28. Natural Hazards and Disasters", "29. Human Geography Nature and Scope",
"30. The World Population Distribution, Density and Growth", "31. Human Development", "32. Primary Activities",
"33. Secondary Activities", "34. Tertiary and Quaternary Activities", "35. Transport and Communication",
"36. International Trade", "37. Population: Distribution, Density, Growth and Composition", "38. Human Settlements",
"39. Land Resources and Agriculture", "40. Water Resources", "41. Mineral and Energy Resources",
"42. Planning and Sustainable Development in Indian Context", "43. Transport and Communication (India)",
"44. International Trade (India)", "45. Unclassified (Requires Deeper Mapping)"
]

# Read original file to get SSC blocks
with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

import re
ssc_blocks = {}
topics_split = re.split(r"(?m)^## ", content)
for ts in topics_split[1:]:
    lines = ts.split("\n")
    topic_name = lines[0].strip()
    ssc_idx = -1
    for i, l in enumerate(lines):
        if "SSC Stenographer Data" in l:
            ssc_idx = i
            break
    if ssc_idx != -1:
        ssc_blocks[topic_name] = "\n".join(lines[ssc_idx:])
    else:
        ssc_blocks[topic_name] = ""

# Read the full questions
with open("/app/applet/classified_questions.json", "r") as f:
    questions = json.load(f)

questions_by_topic = {t: [] for t in topics}
for q in questions:
    fmt = q["format"]
    if fmt == "Multi-Statement":
        fmt = "Statement-based"
    tier = "Advanced"
    if fmt == "Direct Fact":
        tier = "Basic"
    elif fmt == "Statement-based":
        tier = "Medium"
    elif fmt == "Matching Pairs":
        tier = "Medium"
    elif fmt == "Assertion-Reason":
        tier = "Advanced"
        
    q["tier"] = tier
    q["format"] = fmt
    topic = q["new_topic"]
    if topic in questions_by_topic:
        questions_by_topic[topic].append(q)
    else:
        questions_by_topic["45. Unclassified (Requires Deeper Mapping)"].append(q)

new_content = "# Master Geography Question Bank & Trend Grounding File\n\n"

for topic in topics:
    new_content += f"## {topic}\n"
    new_content += f"### UPSC Prelims Data (134-Question Set)\n"
    
    topic_qs = questions_by_topic[topic]
    new_content += f"*Total Questions Mapped:* {len(topic_qs)}\n"
    
    topic_qs.sort(key=lambda x: x["seq_num"])
    
    for q in topic_qs:
        new_content += f"- **Topic**: {topic}\n"
        new_content += f"- **Tier**: {q['tier']}\n"
        new_content += f"- **Format**: {q['format']}\n"
        new_content += f"- **Exam-Relevance**: Elite\n"
        new_content += f"- **Source**: Real-PYQ\n"
        new_content += f"- **Specific-Exam**: UPSC-Prelims\n"
        new_content += f"- **Question**:\n"
        new_content += f"```\n{q['text']}\n```\n"
    
    if topic in ssc_blocks and ssc_blocks[topic]:
        new_content += ssc_blocks[topic] + "\n"
        if not ssc_blocks[topic].endswith("\n"):
            new_content += "\n"
    else:
        new_content += "\n"

with open("/app/applet/source-material/consolidated_grounding.md", "w") as f:
    f.write(new_content)

print("Injected successfully.")
