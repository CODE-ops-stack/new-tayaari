from typing import Dict, List, Optional
import re

ONTOLOGY_BANKS: Dict[str, List[str]] = {
    "planets":         ["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"],
    "moons":           ["Moon","Phobos","Deimos","Ganymede","Europa","Callisto","Titan","Charon"],
    "stars_constellations": ["Saptarishi","Orion","Cassiopeia","Ursa Major","Ursa Minor","Scorpius","Gemini","Leo"],
    "celestial_types": ["Star","Planet","Satellite","Asteroid","Comet","Meteoroid","Galaxy","Nebula"],
    "atmospheric_layers": ["Troposphere","Stratosphere","Mesosphere","Thermosphere","Exosphere","Ionosphere"],
    "latitudes":       ["Tropic of Cancer","Tropic of Capricorn","Arctic Circle","Antarctic Circle","Equator","Prime Meridian"],
    "ocean_currents":  ["Gulf Stream","Labrador Current","Kuroshio","Benguela Current","Humboldt Current","Agulhas Current"],
    "landforms":       ["Mountain","Plateau","Plain","Valley","Delta","Canyon","Fjord","Archipelago"],
    "seasons":         ["Summer Solstice","Winter Solstice","Vernal Equinox","Autumnal Equinox"],
    "map_types":       ["Political Map","Physical Map","Thematic Map","Topographic Map","Road Map"],
    "domains":         ["Lithosphere","Hydrosphere","Atmosphere","Biosphere"],
    "rock_types":      ["Basalt","Granite","Sandstone","Limestone","Marble","Shale","Gneiss","Slate"],
    "rivers_india":    ["Ganga","Brahmaputra","Yamuna","Indus","Godavari","Krishna","Mahanadi","Cauvery"],
    "mountains":       ["Himalayas","Western Ghats","Eastern Ghats","Satpura Range","Vindhya Range","Aravalli Range"],
    "soils_india":     ["Alluvial soil","Black soil","Red soil","Laterite soil","Desert soil","Mountain soil"],
    "crops":           ["Wheat","Rice","Cotton","Jute","Sugarcane","Tea","Coffee","Rubber"],
    "minerals":        ["Coal","Iron ore","Manganese","Mica","Bauxite","Copper","Gold","Petroleum"],
    "energy_sources":  ["Coal","Petroleum","Natural Gas","Solar","Wind","Hydro","Nuclear","Geothermal"],
    "transport":       ["Railways","Roadways","Waterways","Airways","Pipelines"],
    "industries":      ["Iron and Steel","Cotton Textile","Jute","Cement","Sugar","Fertilizer","Automobile","IT"],
    "vegetation":      ["Tropical Rainforest","Deciduous Forest","Coniferous Forest","Grassland","Desert Scrub","Mangrove"],
    "continents":      ["Asia","Africa","North America","South America","Antarctica","Europe","Australia"],
    "oceans":          ["Pacific Ocean","Atlantic Ocean","Indian Ocean","Arctic Ocean","Southern Ocean"],
}

def detect_semantic_type(entity: str, context: str) -> Optional[str]:
    """
    STRICT semantic type detection.
    Matches must be whole words, avoiding substring collision (e.g. 'indus' in 'industrial').
    Also checks context to ensure the entity is used in that sense.
    """
    for category, members in ONTOLOGY_BANKS.items():
        for member in members:
            # Must exactly match the member name as a whole word/phrase
            # Handle case-insensitive whole word match
            pattern = r'\b' + re.escape(member.lower()) + r'\b'
            
            # The entity must exactly match the member OR the member must be in the entity
            if member.lower() == entity.lower() or re.search(pattern, entity.lower()):
                # Avoid the "Indus" -> "Rivers" match if context is purely about "Industries" and not rivers.
                # If the matched member is Indus, check if "river" is in context or "Indus" is capitalized appropriately.
                # To be absolutely safe, let's just make sure the matched member is standalone in context too.
                if re.search(pattern, context.lower()):
                    
                    # Specific guards:
                    if member.lower() == "indus":
                        if "river" not in context.lower() and "valley" not in context.lower() and "water" not in context.lower():
                            continue # probably "industrial" was truncated or bad OCR
                    if member.lower() == "star":
                        if "sky" not in context.lower() and "sun" not in context.lower() and "galaxy" not in context.lower() and "planet" not in context.lower():
                            continue # probably "started"

                    return category
    return None
