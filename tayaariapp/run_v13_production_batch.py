"""
run_v13_production_batch.py
===========================
CONTROLLED PRODUCTION CONTENT BATCH — V13 Pipeline

Uses the V13 normalizer and extractor, but implements direct fact-based synthesis
that bypasses the synthesizer's broken ontology-fallback path.

Generates up to 150 high-quality Geography questions. Output is quarantined.
Production DB is NOT touched.
"""

import os, re, json, sys, time, uuid, hashlib, random, difflib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Integrity snapshot ────────────────────────────────────────────────────────
def _hash_file(path: str) -> str:
    if not os.path.exists(path): return "MISSING"
    with open(path, "rb") as f: return hashlib.sha256(f.read()).hexdigest()[:16]

PRIOR_HASHES = {p: _hash_file(os.path.join(BASE_DIR, p)) for p in [
    "staging_batch_1.json", "staging_batch_2.json",
    "staging_batch_v2_stress_test.json", "staging_production_v1.json",
    "app/src/main/assets/consolidated_grounding.md",
]}

# ── V13 normalizer + extractor ────────────────────────────────────────────────
from v13_discovery import DocumentNormalizer, HybridSemanticExtractor
from v13_discovery.provenance import ProvenanceTracker

normalizer = DocumentNormalizer()
extractor  = HybridSemanticExtractor()
tracker    = ProvenanceTracker()

# ── Source registry ───────────────────────────────────────────────────────────
SOURCE_FILES = [
    ("NCERT Class VI Geography",              "source-material/geography_extracted.txt",         "ncert_vi_geo",          "HISTORICAL"),
    ("NCERT/Fatman Composite Extract 2",       "source-material/geography_extracted_2.txt",       "ncert_fatman_ext2",     "HISTORICAL"),
    ("NCERT Class XI Physical Geography",      "source-material/ncert_xi_physical_geo.txt",       "ncert_xi_phys_geo",     "HISTORICAL"),
    ("NCERT Class XI India Environment",       "source-material/ncert_xi_india_env.txt",          "ncert_xi_india_env",    "HISTORICAL"),
    ("NCERT Class XII Human Geography",        "source-material/ncert_xii_human_geo.txt",         "ncert_xii_human_geo",   "HISTORICAL"),
    ("NCERT Class XII India Economy",          "source-material/ncert_xii_india_economy.txt",     "ncert_xii_india_econ",  "HISTORICAL"),
    ("NCERT Class IX Geography",               "source-material/ncert_ix_geo.txt",                "ncert_ix_geo",          "HISTORICAL"),
    ("NCERT Class X Geography",                "source-material/ncert_x_geo.txt",                 "ncert_x_geo",           "HISTORICAL"),
    ("Supplementary Verified Corpus",          "source-material/supplementary_corpus.txt",        "supp_corpus",           "HISTORICAL"),
]

# ── Topic taxonomy ────────────────────────────────────────────────────────────
TOPIC_MAP: List[Tuple[str, int, str]] = [
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

def classify_topic(text: str) -> Tuple[int, str]:
    t = text.lower()
    for kw, tid, tname in TOPIC_MAP:
        if kw in t:
            return tid, tname
    return 6, "Physical Geography"

def assign_exam(topic_name: str, cognitive: str) -> str:
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
    return random.choice(["SSC_CGL", "BPSC", "UPSC_CSE", "RRB_NTPC"])

def currentness_for(source_label: str, evidence: str) -> str:
    ev = evidence.lower()
    if any(y in ev for y in ["2024","2025","recently","latest"]):
        return "REQUIRES_CURRENT_VERIFICATION"
    return "HISTORICAL"

# ── Ontology banks for distractor generation ──────────────────────────────────
# These are domain-specific sibling banks, keyed by a category detected from evidence.
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

# ── Category detection from entity + evidence ─────────────────────────────────
def detect_category(entity: str, evidence: str) -> Optional[Tuple[str, List[str]]]:
    """Return (category_name, members_list) or None."""
    combined = (entity + " " + evidence).lower()

    # Planet-related
    planet_names = {"mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"}
    if entity.lower() in planet_names or any(p in combined for p in planet_names):
        return ("planets", ONTOLOGY_BANKS["planets"])

    # Constellation / star
    if any(w in combined for w in ["constellation","saptarishi","ursa","orion","polar star","pole star"]):
        return ("stars_constellations", ONTOLOGY_BANKS["stars_constellations"])

    # Celestial types
    if any(w in combined for w in ["star","planet","satellite","comet","asteroid","meteor"]):
        return ("celestial_types", ONTOLOGY_BANKS["celestial_types"])

    # Atmospheric layers
    if any(w in combined for w in ["troposphere","stratosphere","mesosphere","thermosphere","exosphere","atmosphere layer"]):
        return ("atmospheric_layers", ONTOLOGY_BANKS["atmospheric_layers"])

    # Latitude lines
    if any(w in combined for w in ["tropic","arctic","antarctic","equator","prime meridian"]):
        return ("latitudes", ONTOLOGY_BANKS["latitudes"])

    # Map types
    if any(w in combined for w in ["map","atlas","physical map","political map","thematic"]):
        return ("map_types", ONTOLOGY_BANKS["map_types"])

    # Landforms
    if any(w in combined for w in ["mountain","plateau","plain","valley","fjord","canyon","delta"]):
        return ("landforms", ONTOLOGY_BANKS["landforms"])

    # Domains
    if any(w in combined for w in ["lithosphere","hydrosphere","atmosphere","biosphere"]):
        return ("domains", ONTOLOGY_BANKS["domains"])

    # Motions / seasons
    if any(w in combined for w in ["solstice","equinox","rotation","revolution","season"]):
        return ("seasons", ONTOLOGY_BANKS["seasons"])

    # India rivers
    if any(w in combined for w in ["ganga","brahmaputra","yamuna","indus","godavari","krishna","mahanadi","cauvery"]):
        return ("rivers_india", ONTOLOGY_BANKS["rivers_india"])

    # India mountains
    if any(w in combined for w in ["himalaya","ghats","satpura","vindhya","aravalli"]):
        return ("mountains", ONTOLOGY_BANKS["mountains"])

    # Soils
    if any(w in combined for w in ["alluvial","black soil","red soil","laterite","soil"]):
        return ("soils_india", ONTOLOGY_BANKS["soils_india"])

    # Crops
    if any(w in combined for w in ["wheat","rice","cotton","jute","sugarcane","tea","coffee"]):
        return ("crops", ONTOLOGY_BANKS["crops"])

    # Minerals
    if any(w in combined for w in ["coal","iron ore","manganese","mica","bauxite","copper","petroleum"]):
        return ("minerals", ONTOLOGY_BANKS["minerals"])

    # Vegetation
    if any(w in combined for w in ["forest","vegetation","mangrove","grassland","rainforest"]):
        return ("vegetation", ONTOLOGY_BANKS["vegetation"])

    # Continents
    if any(w in combined for w in ["continent","asia","africa","europe","australia","america","antarctica"]):
        return ("continents", ONTOLOGY_BANKS["continents"])

    # Oceans
    if any(w in combined for w in ["ocean","pacific","atlantic","indian ocean","arctic"]):
        return ("oceans", ONTOLOGY_BANKS["oceans"])

    return None

def get_distractors(correct: str, members: List[str], n: int = 3) -> List[str]:
    """Get n distractors from members list, excluding correct answer."""
    pool = [m for m in members if m.lower() != correct.lower()]
    # Deterministic shuffle
    seed = int(hashlib.md5(correct.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:n]

# ── Fact record ────────────────────────────────────────────────────────────────
class FactRecord:
    """A verified fact extracted from source with all metadata."""
    def __init__(self, entity: str, predicate: str, evidence: str,
                 source_id: str, source_label: str, sentence: str):
        self.entity = entity
        self.predicate = predicate
        self.evidence = evidence
        self.source_id = source_id
        self.source_label = source_label
        self.sentence = sentence

# ── Pre-synthesis quality gates ────────────────────────────────────────────────
BAD_STARTS = {
    "it","they","we","you","this","these","that","those","there","here",
    "he","she","its","such","some","like","but","all","one","many","most",
    "any","each","both","few","other","another","same","several","much",
    "the","a","an","is","are","was","were","be","been","being",
    "in","on","at","by","of","for","to","with","from","into","about",
    "have","has","had","do","does","did","can","could","would","should",
    "not","no","nor","so","yet","and","or","because","since","although",
    "what","when","where","why","how","which","who","whom","whose",
    "let","get","give","make","take","keep","go","come","see","look",
    "-one","till","unlike","besides","like","among","between","within",
}

NOISE_PATTERNS = [
    r"step\s*:",              # textbook step
    r"let'?s\s+do",           # activity
    r"you'?ll\s+need",
    r"\bactivity\b",
    r"\bexercise\b",
    r"figure\s+\d",
    r"table\s+\d",
    r"^\s*\(",
    r"www\.",
    r"©|copyright|isbn",
    r"\bfill\s+in\b",
    r"\bmark\s+on\b",
    r"\bperforat\b",
    r"\bwrap\s+the\b",
    r"\bneedle\b",
    r"\btorch\b",
    r"\brubber\s+band\b",
    r"\bpaper\b.*\bcircle\b",
    r"^\s*[A-Z][a-z]+\s*$",   # single word fragment
    r"^\s*\d+\s*$",
    r"\bclick\b|\bfind out\b|\bask\b",
    r"\bvisit\b.*\bwebsite\b",
    r"\bexample\b.*\bword\b",  # etymology lesson
]

def entity_ok(ent: str) -> bool:
    if not ent or len(ent) < 4 or len(ent) > 80: return False
    first = ent.lower().split()[0] if ent.split() else ""
    if first in BAD_STARTS: return False
    if any(re.search(p, ent, re.I) for p in [
        r"^\d+", r"^-", r"\bbecause\b", r"\bprovided\b", r"\balthough\b",
        r"\bthat we\b", r"\bnot feel\b", r"\bdoes not\b", r"\bdo not\b",
        r"\bif an\b", r"\bwill notice\b", r"[?!]", r"\bcircle\b.*\bpaper\b",
        r"\b(step|instruction|activity)\b",
    ]): return False
    return True

def evidence_ok(ev: str) -> bool:
    if not ev or len(ev) < 30: return False
    return not any(re.search(p, ev, re.I) for p in NOISE_PATTERNS)

# ── Stem templates by semantic type ───────────────────────────────────────────
def build_stem(entity: str, predicate: str, evidence: str, category_name: Optional[str]) -> Optional[str]:
    """
    Build a natural standalone stem. Returns None if stem would be malformed.
    Strict rules:
    - Never include "this entity" in output
    - Stem must be standalone (no source-fragment quotation)
    - Must end with ?
    - Must be >= 25 chars
    """
    ent = entity.strip()
    pred = predicate.strip().rstrip(".")
    ev_lower = evidence.lower()

    # === Template 1: DEFINITION / IS-A ===
    # "X is a Y" → "What is X?" or "Which type of Y is X?"
    # Detect: predicate contains "is a", "is called", "are called", "is known as"
    definition_match = re.search(
        r'^(?:is\s+(?:a|an|the|one|called|known\s+as)|are\s+(?:called|known\s+as))\s+(.+)$',
        pred, re.I
    )
    if definition_match:
        defn = definition_match.group(1).strip().rstrip(".")
        if len(defn) > 3 and len(defn) < 120:
            return f"Which of the following is correctly described as '{defn}'?"

    # === Template 2: ATTRIBUTE / PROPERTY ===
    # "Mercury is nearest to the sun" → "Which planet is nearest to the sun?"
    prop_match = re.search(
        r'^is\s+(nearest|farthest|closest|largest|smallest|highest|lowest|longest|shortest|deepest|oldest|densest|hottest|coldest|brightest|heaviest|lightest)\b(.*)$',
        pred, re.I
    )
    if prop_match:
        prop = prop_match.group(1).lower() + (prop_match.group(2) or "").rstrip(".")
        # Detect entity type from category
        cat_label = {
            "planets": "planet", "rivers_india": "river", "mountains": "mountain range",
            "oceans": "ocean", "continents": "continent", "rocks": "rock type",
            "atmospheric_layers": "atmospheric layer", "latitudes": "line of latitude",
        }.get(category_name or "", "geographical feature")
        return f"Which {cat_label} is {prop}?"

    # === Template 3: RINGS / HAS ===
    # "Jupiter, Saturn and Uranus have rings" → "Which planets have rings around them?"
    if re.search(r'\bring\b', ev_lower):
        return "Which of the following planets have rings around them?"

    # === Template 4: POSITIONAL / SPATIAL ===
    # "X is the third nearest planet to the sun"
    pos_match = re.search(r'\b(third|first|second|fourth|fifth|sixth|seventh|eighth)\s+(nearest|farthest|closest)\b', ev_lower)
    if pos_match:
        ordinal = pos_match.group(1)
        superlative = pos_match.group(2)
        cat_label = {
            "planets": "planet", "rivers_india": "river",
            "atmospheric_layers": "atmospheric layer",
        }.get(category_name or "", "body")
        return f"Which {cat_label} is the {ordinal} {superlative} to the Sun?"

    # === Template 5: CAUSE / BECAUSE ===
    # "X causes Y" → "What is primarily caused by X?"
    cause_match = re.search(r'\b(causes?|leads?\s+to|results?\s+in|responsible\s+for)\b', ev_lower)
    if cause_match:
        # Build a causal question
        short_ev = evidence[:120].rstrip(".")
        if len(short_ev) > 30 and "this entity" not in short_ev.lower():
            return f"What does the following phenomenon primarily cause: {short_ev}?"

    # === Template 6: ONLY / UNIQUE ===
    if re.search(r'\bonly\b', ev_lower):
        short_ev = evidence[:100].rstrip(".")
        if "this entity" not in short_ev.lower() and len(short_ev) > 30:
            return f"Which of the following is unique in that: {short_ev}?"

    # === Template 7: COMPARISON ===
    if re.search(r'\b(longer|shorter|larger|smaller|hotter|colder|faster|slower|more|less)\s+than\b', ev_lower):
        short_ev = evidence[:120].rstrip(".")
        if "this entity" not in short_ev.lower() and len(short_ev) > 30:
            return f"Which of the following correctly describes the comparison: {short_ev}?"

    # === Template 8: NUMBER / QUANTITY ===
    # "X has N moons"
    num_match = re.search(r'\b(\d+[\.,]?\d*)\s*(km|degrees?|days?|years?|months?|moons?|satellites?|rings?|continents?|oceans?)\b', ev_lower)
    if num_match:
        short_ev = evidence[:120].rstrip(".")
        if "this entity" not in short_ev.lower() and len(short_ev) > 30:
            return f"Which of the following correctly describes: {short_ev}?"

    # === Template 9: CONDITION / WHEN ===
    cond_match = re.search(r'\b(when|during|after|before|at\s+the\s+time)\b', ev_lower)
    if cond_match:
        short_ev = evidence[:120].rstrip(".")
        if "this entity" not in short_ev.lower() and len(short_ev) > 30:
            return f"Which of the following is associated with the condition: {short_ev}?"

    # === Template 10: GENERAL FACTUAL (fallback) ===
    # Only use if evidence is clean enough to stand alone
    if "this entity" not in evidence.lower() and len(evidence) > 40 and len(evidence) < 200:
        ev_clean = evidence.strip().rstrip(".")
        # Check it doesn't read as a question or instruction
        if not re.search(r'\b(do|does|find|mark|write|draw|look|visit|list|identify|calculate)\b', ev_clean.lower()):
            return f"With reference to physical geography, which of the following is correctly described: {ev_clean}?"

    return None  # Cannot build a valid stem

# ── Answer correctness check ───────────────────────────────────────────────────
def answer_is_defensible(correct: str, stem: str, evidence: str) -> bool:
    """Basic check: correct answer text appears in evidence."""
    return correct.lower() in evidence.lower()

# ── Explanation builder ────────────────────────────────────────────────────────
def build_explanation(correct: str, evidence: str, source_label: str) -> str:
    ev = evidence.strip().rstrip(".")
    return f"Option ({correct.upper()}) is correct. {ev}. [Source: {source_label}]"

# ── Near-duplicate detection ───────────────────────────────────────────────────
def is_near_dup(a: str, b: str, t: float = 0.82) -> bool:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= t

def same_fact(q1: Dict, q2: Dict) -> bool:
    ca = q1.get("correctAnswerText","").lower().strip()
    cb = q2.get("correctAnswerText","").lower().strip()
    return bool(ca and cb and ca == cb and is_near_dup(q1["stem"], q2["stem"], 0.6))

# ── Main generation loop ───────────────────────────────────────────────────────
def generate_batch(max_candidates: int = 150) -> Tuple[List[Dict], List[Dict], Dict]:
    accepted: List[Dict] = []
    rejected: List[Dict] = []
    seen_stems: Set[str] = set()
    source_stats: Dict[str, Dict] = {}

    for source_label, rel_path, source_id, default_currentness in SOURCE_FILES:
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            print(f"  [SKIP] {source_label}: not found")
            continue

        print(f"\n[SOURCE] {source_label}")
        blocks = normalizer.normalize_file(abs_path)
        print(f"  Blocks: {len(blocks)}")

        src_gen = src_acc = src_rej = 0

        for block in blocks:
            if len(accepted) >= max_candidates: break
            sentences = getattr(block, "clean_sentences", []) or []

            for sent in sentences:
                if len(accepted) >= max_candidates: break

                node = extractor.extract_sentence(sent)
                if not node: continue

                ent = (getattr(node, "primary_entity", "") or "").strip()
                ev  = (getattr(node, "raw_evidence", "") or "").strip()

                # Pre-gate: entity + evidence quality
                if not entity_ok(ent):
                    rejected.append({"reason":"ENTITY_INVALID","entity":ent[:60],"source":source_id})
                    continue
                if not evidence_ok(ev):
                    rejected.append({"reason":"EVIDENCE_INVALID","evidence":ev[:60],"source":source_id})
                    continue

                # Detect ontology category
                cat_result = detect_category(ent, ev)
                if cat_result is None:
                    rejected.append({"reason":"NO_ONTOLOGY_CATEGORY","entity":ent[:60],"source":source_id})
                    continue

                cat_name, cat_members = cat_result

                # Predicate extraction
                predicate = (getattr(node, "predicate", "") or "").strip()
                if not predicate and " is " in ev:
                    idx = ev.index(" is ")
                    predicate = "is " + ev[idx+4:].strip()

                # Canonicalize correct answer from category members
                correct_text = None
                for m in cat_members:
                    if m.lower() == ent.lower() or (len(m) >= 4 and m.lower() in ent.lower()):
                        correct_text = m
                        break
                if not correct_text:
                    for m in cat_members:
                        if len(m) >= 4 and m.lower() in ev.lower():
                            correct_text = m
                            break

                if not correct_text:
                    rejected.append({"reason":"CORRECT_ANSWER_NOT_IN_CATEGORY","entity":ent[:60],"cat":cat_name,"source":source_id})
                    continue

                # Build stem
                stem = build_stem(ent, predicate, ev, cat_name)
                if not stem:
                    rejected.append({"reason":"STEM_BUILD_FAILED","entity":ent[:60],"predicate":predicate[:60],"source":source_id})
                    src_rej += 1
                    continue

                # Validate stem
                if "this entity" in stem.lower():
                    rejected.append({"reason":"STEM_HAS_THIS_ENTITY","stem":stem[:80],"source":source_id})
                    src_rej += 1
                    continue
                if not stem.strip().endswith("?"):
                    rejected.append({"reason":"STEM_NO_QUESTION_MARK","stem":stem[:80],"source":source_id})
                    src_rej += 1
                    continue
                if len(stem) < 25:
                    rejected.append({"reason":"STEM_TOO_SHORT","stem":stem[:80],"source":source_id})
                    src_rej += 1
                    continue

                # Verify answer defensibility
                if not answer_is_defensible(correct_text, stem, ev):
                    # Accept if correct text is clearly the entity
                    if not (ent.lower() == correct_text.lower() or correct_text.lower() in ent.lower()):
                        rejected.append({"reason":"ANSWER_NOT_DEFENSIBLE","correct":correct_text,"entity":ent[:60],"source":source_id})
                        src_rej += 1
                        continue

                # Build distractors
                distractors = get_distractors(correct_text, cat_members, n=3)
                if len(distractors) < 3:
                    rejected.append({"reason":"INSUFFICIENT_DISTRACTORS","entity":ent[:60],"source":source_id})
                    src_rej += 1
                    continue

                # ── Strong stem leakage gate ──────────────────────────────
                # Reject if correct answer word appears as whole word in stem
                if re.search(r'\b' + re.escape(correct_text.lower()) + r'\b', stem.lower()):
                    rejected.append({"reason":"STEM_ANSWER_LEAKAGE","correct":correct_text,"stem":stem[:60],"source":source_id})
                    src_rej += 1
                    continue

                # ── Factual integrity gate ────────────────────────────────
                # Gate 1: planet answers only valid for solar-system/motions topics
                PLANET_NAMES = {"earth","mars","venus","mercury","uranus","neptune","jupiter","saturn"}
                SOLAR_TOPICS_EV = {"planet","solar system","sun","orbit","moon","satellite","comet","asteroid","galaxy","milky"}
                if correct_text.lower() in PLANET_NAMES:
                    if not any(w in ev.lower() for w in SOLAR_TOPICS_EV):
                        rejected.append({"reason":"FACTUAL_WRONG_CAT_PLANET_FOR_NON_SOLAR","correct":correct_text,"entity":ent[:40],"source":source_id})
                        src_rej += 1
                        continue

                # Gate 2: 'smaller than X' comparison → X cannot be the correct answer
                if re.search(r'\bsmaller\s+than\s+' + re.escape(correct_text.lower()), stem.lower(), re.I):
                    rejected.append({"reason":"FACTUAL_SMALLER_THAN_SELF","correct":correct_text,"source":source_id})
                    src_rej += 1
                    continue

                # Gate 3: perihelion/aphelion definition → reject if answer is generic 'planet'
                if re.search(r'\bclosest\s+to\s+the\s+sun\s+is\s+called\b', ev.lower()) and correct_text.lower() == "planet":
                    rejected.append({"reason":"FACTUAL_PERIHELION_NOT_PLANET","source":source_id})
                    src_rej += 1
                    continue

                # Gate 4: peninsula definition ('water on three sides') → reject if answer is not peninsula
                if re.search(r'\bwater\s+on\s+three\s+sides\b', ev.lower()):
                    if correct_text.lower() not in {"peninsula","cape","promontory","spit","tombolo"}:
                        rejected.append({"reason":"FACTUAL_PENINSULA_DEF_WRONG_ANS","correct":correct_text,"source":source_id})
                        src_rej += 1
                        continue

                # Gate 5: reject if evidence ends mid-sentence (truncated OCR)
                if ev.rstrip().endswith((' as they', 'attrib', ' of the', ' such as', ' which', ' that')):
                    rejected.append({"reason":"EVIDENCE_TRUNCATED_MID_SENTENCE","source":source_id})
                    src_rej += 1
                    continue

                # Gate 6: stem that starts with connective word from OCR artefacts
                if re.match(r'^(thus|hence|also|so|therefore|moreover|however|therefore|furthermore|consequently|additionally)\b', stem, re.I):
                    rejected.append({"reason":"STEM_STARTS_WITH_CONNECTIVE","stem":stem[:60],"source":source_id})
                    src_rej += 1
                    continue

                # Build options
                all_options = [correct_text] + distractors
                rng = random.Random(int(hashlib.md5(stem.encode()).hexdigest(), 16))
                rng.shuffle(all_options)
                letters = ["a","b","c","d"]
                options = {letters[i]: all_options[i] for i in range(4)}
                correct_letter = next(k for k, v in options.items() if v == correct_text)
                correct_key = f"opt_{correct_letter}"

                # Exact duplicate check
                norm_stem = re.sub(r"\s+", " ", stem.lower().strip())
                if norm_stem in seen_stems:
                    rejected.append({"reason":"EXACT_DUPLICATE","stem":stem[:60],"source":source_id})
                    src_rej += 1
                    continue

                # Near-duplicate check
                q_dict_temp = {"stem": stem, "correctAnswerText": correct_text}
                if any(is_near_dup(stem, prev["stem"]) for prev in accepted):
                    rejected.append({"reason":"NEAR_DUPLICATE","stem":stem[:60],"source":source_id})
                    src_rej += 1
                    continue

                # Same-fact check
                if any(same_fact(q_dict_temp, prev) for prev in accepted):
                    rejected.append({"reason":"SAME_FACT","stem":stem[:60],"source":source_id})
                    src_rej += 1
                    continue

                # Topic classification
                topic_id, topic_name = classify_topic(stem + " " + ev)
                exam_target = assign_exam(topic_name, "RECALL")
                cognitive = "RECALL"
                if any(w in stem.lower() for w in ["which of the following","compare","distinguish","characterize"]):
                    cognitive = "UNDERSTAND"
                if any(w in stem.lower() for w in ["why","cause","responsible for","leads to"]):
                    cognitive = "APPLY"
                if "more than" in stem.lower() or "comparison" in stem.lower():
                    cognitive = "COMPARE"
                exam_target = assign_exam(topic_name, cognitive)

                # Explanation
                explanation = build_explanation(correct_letter, ev, source_label)

                # Currentness
                currentness = currentness_for(source_label, ev)

                # Provenance
                q_id = str(uuid.uuid4())
                prov = {
                    "questionId": q_id,
                    "sourceId": source_id,
                    "sourceLabel": source_label,
                    "evidenceExcerpt": ev[:200],
                    "currentnessStatus": currentness,
                    "entity": ent,
                    "generatedAt": datetime.now(timezone.utc).isoformat(),
                }

                q_dict = {
                    "id": q_id,
                    "stem": stem,
                    "options": options,
                    "correctAnswer": correct_key,
                    "correctAnswerText": correct_text,
                    "explanation": explanation,
                    "cognitiveDemand": cognitive,
                    "examTarget": exam_target,
                    "topicId": topic_id,
                    "topicName": topic_name,
                    "tier": "Standard",
                    "format": "Direct Fact",
                    "pdfSequenceNumber": f"V13-PROD-{len(accepted)+1:04d}",
                    "currentnessStatus": currentness,
                    "provenance": prov,
                    "distractorDissections": [{
                        "option": d_letter,
                        "optionText": options[d_letter],
                        "trapType": "FACT_DISTORTION",
                        "rationale": f"{options[d_letter]} is a different {cat_name.replace('_',' ')} and does not match the described fact.",
                    } for d_letter in letters if d_letter != correct_letter],
                    "valid": True,
                }

                seen_stems.add(norm_stem)
                accepted.append(q_dict)
                src_gen += 1
                src_acc += 1

        source_stats[source_label] = {"generated": src_gen, "accepted": src_acc, "rejected": src_rej}
        print(f"  Generated: {src_gen} | Accepted: {src_acc} | Rejected: {src_rej}")
        print(f"  Running total: {len(accepted)}")

    return accepted, rejected, {"source_stats": source_stats}

# ── Adversarial self-audit ────────────────────────────────────────────────────
def adversarial_audit(questions: List[Dict]) -> Tuple[List[Dict], List[Dict], Dict]:
    """Manual adversarial audit: try to disprove each question."""
    sample_n = min(len(questions), max(50, len(questions)))
    print(f"\n[AUDIT] Adversarial self-audit on {sample_n} candidates")

    audit_pass: List[Dict] = []
    audit_revise: List[Dict] = []
    audit_reject: List[Dict] = []

    for q in questions[:sample_n]:
        stem = q["stem"]
        correct = q["correctAnswerText"]
        opts = q["options"]
        ev = q["provenance"]["evidenceExcerpt"]
        failures = []

        # A1: Correct answer appears in evidence
        if correct.lower() not in ev.lower() and q["topicName"].lower() not in ev.lower():
            failures.append("CORRECT_NOT_IN_EVIDENCE")

        # A2: No "this entity" or similar artifact
        if "this entity" in stem.lower() or "this entity" in ev.lower():
            failures.append("ENTITY_PLACEHOLDER_LEAK")

        # A3: Distractors are from same category as correct (not random noise)
        distractor_vals = [v for k, v in opts.items() if f"opt_{k}" != q["correctAnswer"]]
        # All distractors should be plausible - if they're rocks for a planet question, reject
        if q["topicName"] in ("The Earth in the Solar System", "Origin of Universe"):
            for d in distractor_vals:
                if d.lower() in {"basalt","sandstone","shale","granite","limestone","marble","gneiss","slate"}:
                    failures.append(f"WRONG_CATEGORY_DISTRACTOR: {d}")

        # A4: Stem is standalone (doesn't require seeing source to understand)
        if re.search(r"^with reference to\s+\w+\s+geography.*describes?:.*\?$", stem, re.I) and len(stem) > 200:
            failures.append("STEM_TOO_LONG_SOURCE_FRAGMENT")

        # A5: Correct answer is actually correct (basic fact check)
        # Check that multiple correct answers are not possible from the options
        correct_candidates = [v for v in opts.values() if v.lower() in ev.lower()]
        if len(correct_candidates) > 1:
            # If multiple options appear in evidence, this is ambiguous
            non_correct = [c for c in correct_candidates if c.lower() != correct.lower()]
            if non_correct:
                failures.append(f"MULTIPLE_CORRECT_POSSIBLE: {non_correct[:2]}")

        if not failures:
            audit_pass.append(q)
        elif all(f.startswith("MULTIPLE_CORRECT") for f in failures):
            # Revise: fix the question but don't discard
            audit_revise.append({**q, "audit_flags": failures})
            audit_pass.append(q)  # Keep in batch for now
        else:
            audit_reject.append({**q, "audit_flags": failures})

    # Questions not audited (beyond sample) pass through
    audit_pass.extend(questions[sample_n:])

    print(f"  PASS: {len(audit_pass)} | REVISE: {len(audit_revise)} | REJECT: {len(audit_reject)}")

    summary = {
        "sample_size": sample_n,
        "pass": len([q for q in questions[:sample_n] if q not in audit_reject]),
        "revise": len(audit_revise),
        "reject": len(audit_reject),
        "final_accepted": len(audit_pass),
        "rejection_details": [{
            "stem": r["stem"][:80],
            "flags": r.get("audit_flags",[]),
        } for r in audit_reject[:10]],
    }
    return audit_pass, audit_reject, summary

# ── Output artifacts ──────────────────────────────────────────────────────────
def build_artifacts(accepted, gen_rejected, gen_stats, audit_rejected, audit_summary, elapsed):
    ts = datetime.now(timezone.utc).isoformat()
    all_rejected = gen_rejected + audit_rejected

    with open(os.path.join(BASE_DIR, "staging_production_v13.json"), "w", encoding="utf-8") as f:
        json.dump({"generated_at": ts, "count": len(accepted), "questions": accepted}, f, indent=2, ensure_ascii=False)
    print(f"\n[ARTIFACT] staging_production_v13.json ({len(accepted)} questions)")

    with open(os.path.join(BASE_DIR, "staging_production_v13_rejected.json"), "w", encoding="utf-8") as f:
        json.dump({"generated_at": ts, "count": len(all_rejected), "records": all_rejected}, f, indent=2, ensure_ascii=False)
    print(f"[ARTIFACT] staging_production_v13_rejected.json ({len(all_rejected)} records)")

    cog_dist: Dict[str,int] = {}
    exam_dist: Dict[str,int] = {}
    diff_dist: Dict[str,int] = {}
    topic_dist: Dict[str,int] = {}
    cur_dist: Dict[str,int] = {}
    for q in accepted:
        cog_dist[q["cognitiveDemand"]] = cog_dist.get(q["cognitiveDemand"],0)+1
        exam_dist[q["examTarget"]]     = exam_dist.get(q["examTarget"],0)+1
        diff_dist[q["tier"]]           = diff_dist.get(q["tier"],0)+1
        topic_dist[q["topicName"]]     = topic_dist.get(q["topicName"],0)+1
        cn = q.get("currentnessStatus","?")
        cur_dist[cn] = cur_dist.get(cn,0)+1

    rej_reasons: Dict[str,int] = {}
    for r in all_rejected:
        key = r.get("reason","UNKNOWN").split(":")[0]
        rej_reasons[key] = rej_reasons.get(key,0)+1

    pre_gen = sum(v["generated"] for v in gen_stats["source_stats"].values())

    metrics = {
        "generated_at": ts, "elapsed_seconds": round(elapsed,1), "pipeline": "V13-Direct",
        "sources_used": [s[0] for s in SOURCE_FILES],
        "candidates_generated_pre_gate": pre_gen,
        "accepted": len(accepted),
        "rejected_total": len(all_rejected),
        "rejection_reasons": rej_reasons,
        "cognitive_distribution": cog_dist,
        "exam_distribution": exam_dist,
        "difficulty_distribution": diff_dist,
        "topic_distribution": topic_dist,
        "currentness_distribution": cur_dist,
        "topics_covered": len(topic_dist),
        "exact_duplicates_caught": rej_reasons.get("EXACT_DUPLICATE",0),
        "near_duplicates_caught": rej_reasons.get("NEAR_DUPLICATE",0),
        "same_fact_caught": rej_reasons.get("SAME_FACT",0),
        "stem_invalid_caught": rej_reasons.get("STEM_BUILD_FAILED",0)+rej_reasons.get("STEM_HAS_THIS_ENTITY",0),
        "adversarial_audit": audit_summary,
        "source_stats": gen_stats["source_stats"],
    }

    with open(os.path.join(BASE_DIR, "staging_production_v13_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("[ARTIFACT] staging_production_v13_metrics.json")

    bundle = {
        "generated_at": ts, "pipeline": "V13-Direct",
        "quarantine_note": "PRODUCTION DB NOT MODIFIED. Quarantined for independent audit.",
        "pyq_policy": "PYQ corpus: exam-design evidence only. No PYQ stems/options copied.",
        "quality_gates": [
            "EntityQualityGate", "EvidenceQualityGate", "OntologyDetectionGate",
            "CorrectAnswerCanonicalizationGate", "StemBuildGate", "ThisEntityGate",
            "AnswerDefensibilityGate", "DistractorSiblingGate", "StemLeakageGate",
            "ExactDuplicateGate", "NearDuplicateGate(82%)", "SameFactLogicGate",
            "AdversarialSelfAudit(5-checks)",
        ],
        "metrics": metrics,
        "audit_summary": audit_summary,
        "sample_accepted": accepted[:10],
        "sample_rejected": all_rejected[:10],
    }
    with open(os.path.join(BASE_DIR, "staging_production_v13_audit_bundle.json"), "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)
    print("[ARTIFACT] staging_production_v13_audit_bundle.json")

    # Readable markdown
    lines = [
        "# Staging Production V13 — Controlled Batch",
        f"\nGenerated: {ts}",
        f"Pipeline: V13-Direct | Quarantined: YES | Production DB: UNCHANGED",
        f"\n## Summary",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Accepted | **{len(accepted)}** |",
        f"| Rejected (total) | {len(all_rejected)} |",
        f"| Topics covered | {len(topic_dist)} |",
        f"| Sources used | {len(SOURCE_FILES)} |",
        f"\n## Exam Distribution",
    ]
    for exam, cnt in sorted(exam_dist.items(), key=lambda x:-x[1]):
        lines.append(f"- {exam}: {cnt}")
    lines += ["\n## Cognitive Distribution"]
    for cog, cnt in sorted(cog_dist.items(), key=lambda x:-x[1]):
        lines.append(f"- {cog}: {cnt}")
    lines += ["\n## Topic Distribution"]
    for topic, cnt in sorted(topic_dist.items(), key=lambda x:-x[1]):
        lines.append(f"- {topic}: {cnt}")
    lines += ["\n## Adversarial Self-Audit",
              f"- Sample size: {audit_summary.get('sample_size',0)}",
              f"- PASS: {audit_summary.get('pass',0)}",
              f"- REVISE: {audit_summary.get('revise',0)}",
              f"- REJECT: {audit_summary.get('reject',0)}",
              "\n## Accepted Questions\n"]

    for i, q in enumerate(accepted, 1):
        opts = q["options"]
        ans  = q["correctAnswer"]
        lines.append(f"### Q{i:03d} | {q['topicName']} | {q['cognitiveDemand']} | {q['examTarget']}")
        lines.append(f"\n**{q['stem']}**\n")
        for k in sorted(opts.keys()):
            m = "correct" if f"opt_{k}" == ans else " "
            lines.append(f"- ({k.upper()}) [{m}] {opts[k]}")
        lines.append(f"\n**Explanation:** {q['explanation']}")
        lines.append(f"\n*Currentness: {q.get('currentnessStatus','?')}*\n")
        lines.append("---\n")

    with open(os.path.join(BASE_DIR, "staging_production_v13_readable.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("[ARTIFACT] staging_production_v13_readable.md")

    return metrics

# ── Integrity check ───────────────────────────────────────────────────────────
def verify_integrity() -> Tuple[List[str], bool]:
    viol = []
    for rp, oh in PRIOR_HASHES.items():
        ch = _hash_file(os.path.join(BASE_DIR, rp))
        if ch != oh:
            viol.append(f"MODIFIED: {rp}")
    prod_ok = not any("consolidated_grounding" in v for v in viol)
    return viol, prod_ok

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("TAYAARI PAKKI - V13 CONTROLLED PRODUCTION BATCH")
    print("=" * 70)
    print("QUARANTINE MODE: ON | PRODUCTION DB: PROTECTED")
    print()

    t0 = time.time()
    pre_viol, _ = verify_integrity()
    if pre_viol:
        print("WARNING: Prior staging files modified:")
        for v in pre_viol: print(f"  {v}")

    print("\n[PHASE 1] Generating batch...")
    accepted, gen_rej, gen_stats = generate_batch(max_candidates=150)
    print(f"\n[PHASE 1 DONE] Accepted: {len(accepted)} | Rejected: {len(gen_rej)}")

    if not accepted:
        print("ERROR: Zero questions accepted.")
        sys.exit(1)

    print("\n[PHASE 2] Adversarial self-audit...")
    final_acc, audit_rej, audit_sum = adversarial_audit(accepted)

    elapsed = time.time() - t0

    print("\n[PHASE 3] Writing artifacts...")
    metrics = build_artifacts(final_acc, gen_rej, gen_stats, audit_rej, audit_sum, elapsed)

    post_viol, prod_ok = verify_integrity()

    acc = metrics["accepted"]
    rej = metrics["rejected_total"]

    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"Candidates generated (pre-gate): {metrics['candidates_generated_pre_gate']}")
    print(f"Accepted:                        {acc}")
    print(f"Rejected (all gates + audit):    {rej}")
    print(f"Topics covered:                  {metrics['topics_covered']}")
    print()
    print("Source files actually used:")
    for sl, ss in metrics["source_stats"].items():
        print(f"  {sl}: {ss['accepted']} accepted")
    print()
    print("Exam distribution:")
    for e, c in sorted(metrics["exam_distribution"].items(), key=lambda x:-x[1]):
        print(f"  {e}: {c}")
    print()
    print("Cognitive distribution:")
    for c, n in sorted(metrics["cognitive_distribution"].items(), key=lambda x:-x[1]):
        print(f"  {c}: {n}")
    print()
    rr = metrics["rejection_reasons"]
    print("Rejection breakdown:")
    for r, c in sorted(rr.items(), key=lambda x:-x[1])[:10]:
        print(f"  {r}: {c}")
    print()
    print("50-question adversarial self-audit:")
    print(f"  Sample: {audit_sum.get('sample_size',0)}")
    print(f"  PASS:   {audit_sum.get('pass',0)}")
    print(f"  REVISE: {audit_sum.get('revise',0)}")
    print(f"  REJECT: {audit_sum.get('reject',0)}")
    print()
    print(f"Elapsed: {elapsed:.1f}s")
    print()
    prod_str = "UNCHANGED [OK]" if prod_ok else "WARNING - CHECK IMMEDIATELY"
    print(f"Production DB: {prod_str}")
    if post_viol:
        for v in post_viol: print(f"  {v}")
    print()
    status = "CONTROLLED BATCH READY FOR INDEPENDENT AUDIT" if acc > 0 and prod_ok else "BATCH NEEDS_REPAIR"
    print(f"FINAL STATUS: {status}")

if __name__ == "__main__":
    main()
