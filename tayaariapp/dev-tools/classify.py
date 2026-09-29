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

keywords = {
    "1. The Earth in the Solar System": ["solar system", "planet", "asteroid", "meteor", "sun ", "moon ", "eclipse"],
    "2. Globe: Latitudes and Longitudes": ["latitude", "longitude", "equator", "tropic of", "prime meridian", "standard time"],
    "3. Motions of the Earth": ["rotation", "revolution", "solstice", "equinox", "leap year", "seasons", "axial tilt", "coriolis"],
    "4. Maps": ["map", "scale", "projection", "cartography"],
    "5. Major Domains of the Earth": ["lithosphere", "hydrosphere", "atmosphere", "biosphere", "continent", "ocean"],
    "6. Major Landforms of the Earth": ["mountain", "plateau", "plains", "valley", "glacier"],
    "7. Our Country - India": ["india", "states of india", "union territory"],
    "8. India: Climate, Vegetation and Wildlife": ["monsoon", "wildlife sanctuary", "national park", "flora and fauna"],
    "10. The Origin and Evolution of the Earth": ["big bang", "nebular hypothesis", "evolution of earth", "geological time"],
    "11. Interior of the Earth": ["earthquake", "seismic waves", "volcano", "crust", "mantle", "core", "magma"],
    "12. Distribution of Oceans and Continents": ["continental drift", "plate tectonics", "sea floor spreading", "pangaea"],
    "13. Geomorphic Processes": ["weathering", "erosion", "mass movement", "exogenic", "endogenic", "denudation"],
    "14. Landforms and their Evolution": ["river", "wind", "groundwater", "waves", "karst", "depositional", "erosional", "oxbow", "meander", "delta", "gorge", "v-shaped"],
    "15. Composition and Structure of Atmosphere": ["troposphere", "stratosphere", "mesosphere", "ionosphere", "ozone", "greenhouse gas"],
    "16. Solar Radiation, Heat Balance and Temperature": ["insolation", "albedo", "temperature inversion", "isotherm", "heat budget"],
    "17. Atmospheric Circulation and Weather Systems": ["cyclone", "anticyclone", "trade winds", "westerlies", "jet stream", "air mass", "fronts", "pressure belt"],
    "18. Water in the Atmosphere": ["humidity", "condensation", "precipitation", "cloud", "fog", "dew", "rainfall"],
    "19. World Climate and Climate Change": ["koppen", "mediterranean climate", "equatorial climate", "global warming", "climate change"],
    "20. Water (Oceans)": ["salinity", "ocean relief", "continental shelf", "trench", "abyssal plain"],
    "21. Movements of Ocean Water": ["ocean current", "tide", "tsunami", "upwelling", "gulf stream", "el nino", "la nina"],
    "22. Biodiversity and Conservation": ["biodiversity", "conservation", "endangered", "biosphere reserve", "wetland", "ramsar"],
    "24. Structure and Physiography": ["himalaya", "peninsular plateau", "western ghats", "eastern ghats", "indo-gangetic", "thar desert", "islands", "physiography", "pass "],
    "25. Drainage System": ["river system", "ganga", "brahmaputra", "indus", "godavari", "krishna", "cauvery", "narmada", "tapi", "lake", "drainage basin", "tributary", "waterfall"],
    "26. Climate": ["indian monsoon", "western disturbance", "tropical cyclone", "el nino", "indian ocean dipole", "retreating monsoon"],
    "27. Natural Vegetation": ["forest", "tropical evergreen", "deciduous", "mangrove", "thorn forest", "alpine", "shola"],
    "32. Primary Activities": ["agriculture", "farming", "mining", "fishing", "forestry", "pastoralism"],
    "33. Secondary Activities": ["industry", "manufacturing", "cotton textile", "iron and steel"],
    "39. Land Resources and Agriculture": ["crop", "wheat", "rice", "sugarcane", "cotton", "soil", "irrigation", "fertigation", "kharif", "rabi", "zaid"],
    "40. Water Resources": ["groundwater depletion", "water conservation", "rainwater harvesting", "multipurpose project"],
    "41. Mineral and Energy Resources": ["coal", "petroleum", "natural gas", "iron ore", "bauxite", "copper", "uranium", "thorium", "solar energy", "wind energy", "geothermal", "rare earth", "mineral"],
    "43. Transport and Communication (India)": ["railway", "highway", "port", "inland waterway", "nhai"]
}

def classify(text):
    text_lower = text.lower()
    
    # Custom specific rules based on common UPSC questions
    if "ocean current" in text_lower or "el nino" in text_lower or "indian ocean dipole" in text_lower:
        if "indian monsoon" in text_lower or "monsoon" in text_lower:
            return "26. Climate"
        return "21. Movements of Ocean Water"
    
    if "crop" in text_lower or "agriculture" in text_lower or "fertigation" in text_lower or "irrigation" in text_lower or "sugarcane" in text_lower or "wheat" in text_lower or "rice" in text_lower or "cotton" in text_lower:
        return "39. Land Resources and Agriculture"
        
    if "coal" in text_lower or "mineral" in text_lower or "uranium" in text_lower or "thorium" in text_lower or "shale gas" in text_lower or "monazite" in text_lower or "rare earth" in text_lower:
        return "41. Mineral and Energy Resources"
        
    if "river" in text_lower or "lake" in text_lower or "tributary" in text_lower or "drainage" in text_lower:
        if "gorge" in text_lower or "meander" in text_lower and not ("indus" in text_lower or "ganga" in text_lower or "brahmaputra" in text_lower or "godavari" in text_lower):
            # Might be geomorphology, but let's check carefully
            pass
        return "25. Drainage System"
        
    if "national park" in text_lower or "wildlife" in text_lower or "biosphere reserve" in text_lower or "wetland" in text_lower:
        return "22. Biodiversity and Conservation"
        
    if "forest" in text_lower or "vegetation" in text_lower or "mangrove" in text_lower:
        return "27. Natural Vegetation"
        
    if "cyclone" in text_lower or "weather" in text_lower or "climate" in text_lower or "monsoon" in text_lower or "westerlies" in text_lower:
        if "india" in text_lower or "indian" in text_lower:
            return "26. Climate"
        return "17. Atmospheric Circulation and Weather Systems"
        
    if "earthquake" in text_lower or "volcano" in text_lower or "mantle" in text_lower or "crust" in text_lower or "seismic" in text_lower:
        return "11. Interior of the Earth"
        
    if "latitude" in text_lower or "longitude" in text_lower or "equator" in text_lower or "tropic of" in text_lower or "solstice" in text_lower:
        if "rotation" in text_lower or "revolution" in text_lower or "season" in text_lower or "21st june" in text_lower:
            return "3. Motions of the Earth"
        return "2. Globe: Latitudes and Longitudes"
        
    if "temperature" in text_lower or "insolation" in text_lower or "albedo" in text_lower:
        return "16. Solar Radiation, Heat Balance and Temperature"
        
    if "soil" in text_lower:
        return "39. Land Resources and Agriculture"
        
    if "himalaya" in text_lower or "western ghats" in text_lower or "plateau" in text_lower or "hills" in text_lower or "pass" in text_lower or "barren island" in text_lower:
        return "24. Structure and Physiography"
        
    if "ocean" in text_lower and "salinity" in text_lower:
        return "20. Water (Oceans)"
        
    # General keyword matching
    best_match = "45. Unclassified (Requires Deeper Mapping)"
    max_count = 0
    for topic, words in keywords.items():
        count = sum(1 for w in words if w in text_lower)
        if count > max_count:
            max_count = count
            best_match = topic
            
    return best_match

with open("/app/applet/upsc_extracted.json", "r") as f:
    questions = json.load(f)

for i, q in enumerate(questions):
    q["seq_num"] = i + 1
    q["new_topic"] = classify(q["text"])

# Group by Topic -> Format -> Tier -> List[seq_nums]
from collections import defaultdict

grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
for q in questions:
    grouped[q["new_topic"]][q["format"]][q["tier"]].append(q["seq_num"])

with open("/app/applet/classified_report.json", "w") as f:
    json.dump(grouped, f, indent=2)

with open("/app/applet/classified_questions.json", "w") as f:
    json.dump(questions, f, indent=2)
