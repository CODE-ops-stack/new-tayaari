import random
from typing import Tuple

TOPIC_MAP = [
    ("solar system",    1,  "The Earth in the Solar System"),
    ("planet",          1,  "The Earth in the Solar System"),
    (" sun ",           1,  "The Earth in the Solar System"),
    ("moon",            1,  "The Earth in the Solar System"),
    (" star ",          1,  "The Earth in the Solar System"),
    ("constellation",   1,  "The Earth in the Solar System"),
    ("comet",           1,  "The Earth in the Solar System"),
    ("asteroid",        1,  "The Earth in the Solar System"),
    ("galaxy",          1,  "The Earth in the Solar System"),
    ("milky way",       1,  "The Earth in the Solar System"),
    ("universe",        20, "Origin of Universe"),
    ("big bang",        20, "Origin of Universe"),
    ("latitude",        2,  "Globe: Latitudes and Longitudes"),
    ("longitude",       2,  "Globe: Latitudes and Longitudes"),
    ("tropic of",       2,  "Globe: Latitudes and Longitudes"),
    ("equator",         2,  "Globe: Latitudes and Longitudes"),
    ("prime meridian",  2,  "Globe: Latitudes and Longitudes"),
    ("international date", 2, "Globe: Latitudes and Longitudes"),
    ("rotation",        3,  "Motions of the Earth"),
    ("revolution",      3,  "Motions of the Earth"),
    ("season",          3,  "Motions of the Earth"),
    ("solstice",        3,  "Motions of the Earth"),
    ("equinox",         3,  "Motions of the Earth"),
    ("leap year",       3,  "Motions of the Earth"),
    ("map",             4,  "Maps"),
    ("atlas",           4,  "Maps"),
    ("contour",         4,  "Maps"),
    ("scale",           4,  "Maps"),
    ("continent",       5,  "Major Domains of the Earth"),
    ("ocean",           5,  "Major Domains of the Earth"),
    ("lithosphere",     5,  "Major Domains of the Earth"),
    ("hydrosphere",     5,  "Major Domains of the Earth"),
    ("atmosphere",      5,  "Major Domains of the Earth"),
    ("biosphere",       5,  "Major Domains of the Earth"),
    ("mountain",        6,  "Major Landforms of the Earth"),
    ("plateau",         6,  "Major Landforms of the Earth"),
    ("plain",           6,  "Major Landforms of the Earth"),
    ("valley",          6,  "Major Landforms of the Earth"),
    ("glacier",         6,  "Major Landforms of the Earth"),
    ("fjord",           6,  "Major Landforms of the Earth"),
    ("india",           7,  "Our Country — India"),
    ("himalaya",        7,  "Our Country — India"),
    ("thar desert",     7,  "Our Country — India"),
    ("deccan",          7,  "Our Country — India"),
    ("monsoon",         25, "Indian Monsoon and Climate"),
    ("rainfall",        25, "Indian Monsoon and Climate"),
    ("ganga",           26, "Drainage and Rivers of India"),
    ("brahmaputra",     26, "Drainage and Rivers of India"),
    ("river",           26, "Drainage and Rivers of India"),
    ("climate",         8,  "India: Climate, Vegetation and Wildlife"),
    ("vegetation",      8,  "India: Climate, Vegetation and Wildlife"),
    ("wildlife",        8,  "India: Climate, Vegetation and Wildlife"),
    ("forest",          28, "Forests and Wildlife"),
    ("soil",            27, "Soils of India"),
    ("agriculture",     17, "Agriculture"),
    ("crop",            17, "Agriculture"),
    ("mineral",         16, "Mineral and Power Resources"),
    ("energy",          33, "Energy Resources"),
    ("industry",        18, "Industries"),
    ("transport",       29, "Transport and Communication"),
    ("trade",           30, "International Trade"),
    ("population",      31, "Population"),
    ("settlement",      32, "Human Settlements"),
    ("rock",            22, "Rocks and Minerals"),
    ("tide",            24, "Oceanography"),
    ("ocean current",   24, "Oceanography"),
    ("wave",            24, "Oceanography"),
    ("erosion",         21, "Geomorphology and Landform Processes"),
    ("deposition",      21, "Geomorphology and Landform Processes"),
    ("volcano",         23, "Earthquakes and Volcanoes"),
    ("earthquake",      23, "Earthquakes and Volcanoes"),
]

import re
def exact_word_match(target: str, text: str) -> bool:
    pattern = r'\b' + re.escape(target.strip()) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))

def classify_topic_strict(text: str) -> Tuple[int, str]:
    t = text.lower()
    for kw, tid, tname in TOPIC_MAP:
        if exact_word_match(kw, t):
            return tid, tname
    return -1, "UNKNOWN"

def assign_exam_strict(topic_name: str, cognitive: str) -> str:
    tn = topic_name.lower()
    upsc_topics = {"monsoon","mineral","agriculture","geomorphology","oceanography","trade","erosion","volcano","earthquake"}
    ssc_topics   = {"solar system","planet","galaxy","map","landform","globe","latitude","longitude"}
    bpsc_topics  = {"india","river","climate","crop","forest"}
    
    if any(k in tn for k in upsc_topics) and cognitive in ("UNDERSTAND","APPLY","INFER","COMPARE"):
        return "UPSC_CSE"
    if any(k in tn for k in bpsc_topics):
        return random.choice(["BPSC", "UPSC_CSE"])
    if any(k in tn for k in ssc_topics) and cognitive == "RECALL":
        return random.choice(["SSC_CGL", "RRB_NTPC", "SSC_CHSL"])
    return "SSC_CGL" # Default fallback
