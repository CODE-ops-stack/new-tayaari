import json
import re

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

split_questions = []
global_seq_num = 1

for q in questions:
    text = q['text'].strip()
    
    matches = list(re.finditer(r'(Q\d+\.)', text))
    
    if not matches:
        split_q = q.copy()
        split_q['text'] = text
        split_q['seq_num'] = global_seq_num
        global_seq_num += 1
        split_questions.append(split_q)
    else:
        for i, match in enumerate(matches):
            start = match.start()
            if i + 1 < len(matches):
                end = matches[i+1].start()
            else:
                end = len(text)
                
            q_text = text[start:end].strip()
            # Clean trailing whitespace / newlines
            q_text = re.sub(r'[\n\s]+$', '', q_text)
            
            split_q = q.copy()
            split_q['text'] = q_text
            split_q['seq_num'] = global_seq_num
            global_seq_num += 1
            
            # Special case for sugar industry
            if "by-products of sugar industry" in q_text:
                split_q['new_topic'] = "39. Land Resources and Agriculture"
            elif "length of daytime and nighttime" in q_text:
                split_q['new_topic'] = "3. Motions of the Earth"
            
            if "Consider the following statements" in q_text or "Which of the following statements" in q_text or "Which of the statements given above" in q_text or "How many of the statements" in q_text:
                fmt = "Statement-based"
            elif "Consider the following pairs" in q_text or "How many of the above pairs" in q_text:
                fmt = "Matching Pairs"
            elif ("Assertion" in q_text and "Reason" in q_text) or ("Statement-I" in q_text and "Statement-II" in q_text):
                fmt = "Assertion-Reason"
            else:
                fmt = "Direct Fact"
                
            tier = "Advanced"
            if fmt == "Direct Fact":
                tier = "Basic"
            elif fmt == "Statement-based" or fmt == "Matching Pairs":
                tier = "Medium"
                
            split_q['format'] = fmt
            split_q['tier'] = tier
            
            split_questions.append(split_q)

questions_by_topic = {t: [] for t in topics}
for q in split_questions:
    topic = q["new_topic"]
    if topic in questions_by_topic:
        questions_by_topic[topic].append(q)
    else:
        questions_by_topic["45. Unclassified (Requires Deeper Mapping)"].append(q)

new_content = "# Master Geography Question Bank & Trend Grounding File\n\n"

for topic in topics:
    new_content += f"## {topic}\n"
    new_content += f"### UPSC Prelims Data (150-Question Set)\n"
    
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

print(f"Injected successfully. Total {len(split_questions)} questions.")
