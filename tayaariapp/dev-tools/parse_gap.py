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

high_yield_topics = [
    "26. Climate",
    "19. World Climate and Climate Change",
    "25. Drainage System",
    "24. Structure and Physiography",
    "4. Maps",
    "23. India - Location",
    "41. Mineral and Energy Resources"
]

def get_quotas(topic):
    if topic in high_yield_topics:
        return {"Basic": 22, "Medium": 15, "Advanced": 12}
    else:
        return {"Basic": 15, "Medium": 10, "Advanced": 8}

counts = {t: {"Basic": 0, "Medium": 0, "Advanced": 0} for t in topics}

with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

blocks = re.split(r"(?m)^## ", content)[1:]
for block in blocks:
    lines = block.split("\n")
    topic_name = lines[0].strip()
    if topic_name not in counts:
        print("Unknown topic:", topic_name)
        continue
    
    # Parse UPSC questions:
    upsc_qs = re.findall(r'- \*\*Tier\*\*: (\w+)\n.*?- \*\*Specific-Exam\*\*: UPSC-Prelims', block, re.DOTALL)
    for t in upsc_qs:
        counts[topic_name][t] += 1
        
    # Parse SSC questions:
    ssc_blocks = re.findall(r'- \*\*Format Type\*\*:.*?\| \*\*Tier\*\*: (\w+) \|.*?\n\s*> Questions: (.*?)\n', block)
    for t, q_str in ssc_blocks:
        qs = [q.strip() for q in q_str.split(',') if q.strip()]
        counts[topic_name][t] += len(qs)

output = "| Topic | Tier | Current Count | Target Quota | Gap | Recommended Source |\n"
output += "|---|---|---|---|---|---|\n"

def get_source(topic, tier):
    if tier == "Basic" or tier == "Medium":
        return f"NCERT chapters related to {topic}"
    else:
        if topic in high_yield_topics:
            return "Coaching Sources (Fatman / ccab2 / PMF IAS / GEOGRAPHY 4.0) + VisionIAS trend notes"
        else:
            return "Coaching Sources (Fatman / ccab2 / PMF IAS / GEOGRAPHY 4.0)"

total_upsc_ssc = 0
for t in topics:
    quotas = get_quotas(t)
    for tier in ["Basic", "Medium", "Advanced"]:
        current = counts[t][tier]
        total_upsc_ssc += current
        target = quotas[tier]
        gap = target - current
        if gap <= 0:
            source = "-"
        else:
            source = get_source(t, tier)
        output += f"| {t} | {tier} | {current} | {target} | {gap} | {source} |\n"

print(f"Total counted: {total_upsc_ssc}")

with open("/app/applet/source-material/gap_report.txt", "w") as f:
    f.write(output)
