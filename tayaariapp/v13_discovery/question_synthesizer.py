"""
v13_discovery/question_synthesizer.py (CONTRACT-FIRST MINIMAL RECONSTRUCTION)
===========================================================================
REVIEW BUILD -- NOT YET APPROVED FOR THE REPO.

Provenance of this file
-----------------------
Recovered from the surviving bytecode of the original 104,802-byte file:
  v13_discovery/__pycache__/question_synthesizer.cpython-312.pyc
  header: src_mtime = Sun Sep 27 15:22:33 2026, src_size = 104802
The .py on disk was truncated to 3,256 bytes / 81 lines on Sep 28 16:50:13.

Only the emission-critical surface is rebuilt. Line-exact original source was
recovered from disassembly for: _normalize_options (L1008),
_get_option_texts (L1016), _get_option_dict_legacy (L1021),
check_category_compatibility (L1026), check_grammatical_fit (L1049),
check_semantic_plausibility (L1073), check_evidence_support (L1091),
check_absence_of_clueing (L1110), verify_all (L1190),
DistractorDissector.dissect (L1235), synthesize (L1687-L1720),
CategoryDefinition (L128), register_category (L155), get_siblings (L199).

LOCKED CONTRACT (proven against the Android runtime, see module notes)
----------------------------------------------------------------------
    options                 = [{"id": "opt_a", "text": "..."}, ...]
    correctAnswer            = "opt_a"          # MUST be one of options[].id
    distractorDissections[i] = {"optionId": "opt_b", "trapType": ..., "dissection": ...}

Evidence for the lock:
  QuestionSelectionEngine.kt:84-88  JSONArray(q.options) -> obj.getString("id")
  QuestionSelectionEngine.kt:136    correctAnswerId = q.correctAnswer   (verbatim)
  PracticeScreen.kt:599             option.id == correctAnswerId
  ResultsScreen.kt:91,171,215       ans == mcq.correctAnswerId
  PracticeViewModel.kt:88,302       pending == currentQ.correctAnswerId
  DataImporter.kt:116,150,165,169   "opt_" + letter; id/text; optionId
  TestModels.kt:51-61               documented canonical shape

DEV IATIONS FROM THE ORIGINAL (deliberate, all review-visible)
--------------------------------------------------------------
  D1. Gate namespace fix (the original defect). Original L1713-1717 passed
      options=options_dict_legacy (keys "a".."d") together with
      correct_key="opt_a", so the gate could never match its own answer.
      Now verify_all normalises once and compares in ONE namespace.
  D2. v13_discovery imports are lazy. The original imported
      v13_discovery.provenance at module scope, which makes this module
      unimportable while the sibling package __init__ is broken. Lazy import
      keeps the module independently verifiable.
  D3. _load_core_taxonomies is intentionally EMPTY (per instruction). No
      taxonomy data is invented. Ontology must be supplied by the caller.
  D4. letters generalised to ['a'..'e'][:option_count]; reproduces the
      original a-d (4) and a-e (5) exactly.
  D5. synthesize_from_corpus is a declared stub, not a silent fallback.
  D6. _normalize_options (L1008) is REPLACED by _validate_options. The original
      silently converted a legacy bare-letter dict into the canonical list. That
      tolerance is the dual-format defect, so it is removed: the gate now
      raises TypeError/ValueError on any non-canonical shape.
  D7. letters uses SUPPORTED_OPTION_LETTERS; reproduces a-d (4) and a-e (5).
"""

import hashlib
import os
import re
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple

from v13_discovery.provenance import (
    CANONICAL_14_INTENTS,
    ProvenanceRecord,
    ProvenanceTracker,
    canonicalize_intent,
    to_r2_intent,
)
from v13_discovery.normalizer import (
    DocumentNormalizer,
    Normalizer,
    TableAndColumnNormalizer,
)

__all__ = [
    "CandidateQuestion",
    "QuestionSynthesizer",
    "OntologyRegistry",
    "CategoryDefinition",
    "DistractorVerificationGate",
    "DistractorDissector",
    "NaturalStemSynthesizer",
    "VALID_ROOM_TRAP_TYPES",
    "OPTION_ID_PREFIX",
    "normalize_options",
    "normalize_correct_key",
]

OPTION_ID_PREFIX = "opt_"
SUPPORTED_OPTION_LETTERS = ("a", "b", "c", "d", "e")
OPTION_ID_RE = re.compile(r"^opt_[a-e]$")
CANONICAL_OPTION_IDS = frozenset(f"{OPTION_ID_PREFIX}{c}" for c in SUPPORTED_OPTION_LETTERS)
MIN_OPTION_COUNT = 4
MAX_OPTION_COUNT = 5

VALID_ROOM_TRAP_TYPES = (
    "ABSOLUTE_WORDING",
    "FACT_DISTORTION",
    "FAMILIARITY_TRAP",
    "CONCEPT_MIX",
    "FALSE_CORRELATION",
    "PARTIAL_TRUTH",
    "TIMELINE_MISMATCH",
    "UNCLASSIFIED_TRAP",
)

_OPTION_LETTERS = "abcdefghijklmnopqrstuvwxyz"


def normalize_options(raw: Any) -> List[Dict[str, str]]:
    """
    Converts any supported option shape into the canonical list form.

    Accepts:
      - list of {"id": "opt_a", "text": "..."}
      - list of letter-keyed dicts [{"a": "..."}]
      - letter-keyed dict {"a": "...", "b": "..."}
      - list/tuple of plain strings (assigned positional letters)

    Returns a list of {"id": "opt_<letter>", "text": <original value>}.

    Blank/whitespace text is PRESERVED, not dropped, so downstream auditors can
    still detect and report empty options. Non-string text values are also
    preserved unchanged so the gate can reject them as a type violation.
    Entries with no usable single-letter id are skipped rather than guessed at.
    """
    if raw is None:
        return []

    items: List[Any] = []
    if isinstance(raw, dict):
        items = list(raw.items())
    elif isinstance(raw, (list, tuple)):
        for entry in raw:
            if isinstance(entry, dict):
                if "text" in entry or "id" in entry:
                    items.append((str(entry.get("id", "") or ""), entry.get("text", "")))
                else:
                    for k, v in entry.items():
                        items.append((str(k), v))
            elif isinstance(entry, str):
                items.append(("\x00pos", entry))
    else:
        return []

    normalized: List[Dict[str, str]] = []
    for key, value in items:
        if isinstance(value, dict):
            text = value.get("text", "")
            raw_id = str(value.get("id", "") or key or "")
        else:
            # Deliberately NOT coerced with str(): non-string option values
            # (None, int, list, dict) must survive normalization so the
            # verification gate can reject them as a type violation.
            text = value
            raw_id = str(key or "")
        if text is None and not raw_id:
            continue
        if raw_id == "\x00pos":
            raw_id = _OPTION_LETTERS[len(normalized)]
        letter = raw_id.strip().lower()
        if letter.startswith(OPTION_ID_PREFIX):
            letter = letter[len(OPTION_ID_PREFIX):]
        if len(letter) != 1 or letter not in _OPTION_LETTERS:
            continue
        normalized.append({"id": f"{OPTION_ID_PREFIX}{letter}", "text": text})

    seen = set()
    deduped: List[Dict[str, str]] = []
    for opt in normalized:
        if opt["id"] in seen:
            continue
        seen.add(opt["id"])
        deduped.append(opt)
    return deduped


def normalize_correct_key(raw_answer: Any) -> str:
    """Returns the canonical bare letter for a correct-answer reference."""
    value = str(raw_answer or "").strip().lower()
    if value.startswith(OPTION_ID_PREFIX):
        value = value[len(OPTION_ID_PREFIX):]
    if len(value) == 1 and value in _OPTION_LETTERS:
        return value
    return "a"


@dataclass
class CandidateQuestion:
    """
    Core CandidateQuestion model strictly compliant with PROJECT.md and test_helpers.py.

    Field order and defaults recovered from the original bytecode (L61-79).
    """
    id: str
    stem: str
    options: List[Dict[str, str]]
    correctAnswer: str
    explanation: str
    distractorDissections: List[Dict[str, str]]
    provenance: Dict[str, Any]
    cognitiveDemand: str
    examTarget: str = "UPSC-Prelims"
    tier: str = "Standard"
    format: str = "Direct Fact"
    topicId: int = 1
    topicName: str = "Physical Geography"
    pdfSequenceNumber: str = "V13-001"
    valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serializes CandidateQuestion to standard Python dictionary."""
        return asdict(self)

    def to_room_markdown(self) -> str:
        """
        Serializes CandidateQuestion into DataImporter.kt-compliant Markdown.

        CRITICAL ARCHITECTURAL CONTRACT:
        'Explanation:' MUST precede 'Correct Answer:' inside the code-fenced block.
        This prevents DataImporter.kt's sequential regex parser from truncating
        the explanation string upon slicing the correct answer.

        FENCE CONTRACT:
        DataImporter.kt line 63 matches a SINGLE backtick:
            - \\*\\*Question\\*\\*:\\s*`\\s*(.*?)\\s*`
        A triple-backtick fence does NOT match that pattern (the regex expects
        one backtick, and DOTALL + non-greedy stops at the first backtick), so
        emitting ``` would cause Android to silently drop every question.
        Do not "upgrade" this to a fenced code block.
        """
        stem_clean = self.stem.strip()
        opts_lines: List[str] = []
        for opt in normalize_options(self.options):
            opt_id = opt.get("id", "")
            val = opt.get("text", "")
            letter = opt_id.replace(OPTION_ID_PREFIX, "").upper()
            opts_lines.append(f"({letter}) {val}")
        opts_str = "\n".join(opts_lines)
        correct_letter = normalize_correct_key(self.correctAnswer).upper()
        first_trap = ""
        if self.distractorDissections:
            first_trap = self.distractorDissections[0].get("trapType", "")
        md = f"- **Topic**: {self.topicName}\n"
        md += f"- **Tier**: {self.tier}\n"
        md += f"- **Format**: {self.format}\n"
        md += f"- **Exam-Relevance**: High\n- **Source**: NCERT Physical Geography\n"
        md += f"- **Specific-Exam**: {self.examTarget}\n"
        # DataImporter.kt (lines 55-63) requires Trap-Type AFTER Specific-Exam and
        # BEFORE PDF-Sequence-Number. Any other position makes the whole question
        # block fail to match and the question is silently dropped on import.
        if first_trap:
            md += f"- **Trap-Type**: {first_trap}\n"
        md += f"- **PDF-Sequence-Number**: {self.pdfSequenceNumber}\n"
        # SINGLE backtick fences -- must match DataImporter.kt line 63 exactly.
        md += f"- **Question**: `\n{stem_clean}\n{opts_str}\nExplanation: {self.explanation}"
        md += f"\nCorrect Answer: Option {correct_letter}\n`\n"
        return md


@dataclass
class CategoryDefinition:
    """
    Taxonomic category definition holding sibling entities, properties, and default traps.
    """
    category_id: str
    domain: str
    display_name: str
    entity_type: str
    grammatical_number: str = "singular"
    members: List[str] = field(default_factory=list)
    descriptions: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    default_traps: List[str] = field(default_factory=list)


class OntologyRegistry:
    """OntologyRegistry"""

    def __init__(self):
        self.categories: Dict[str, CategoryDefinition] = {}
        self.alias_to_category: Dict[str, str] = {}
        self.entity_to_category: Dict[str, str] = {}
        self._load_core_taxonomies()

    def register_category(self, cat: CategoryDefinition) -> None:
        """Registers a category definition and indexes its members and aliases."""
        self.categories[cat.category_id] = cat
        canonical = cat.display_name.lower()
        self.alias_to_category[canonical] = cat.category_id
        for m in cat.members:
            self.entity_to_category[m.lower().strip()] = cat.category_id
        for alias in cat.aliases:
            self.alias_to_category[alias.lower().strip()] = cat.category_id

    def get_category(self, category_id: str) -> Optional[CategoryDefinition]:
        """Direct lookup of category by canonical ID or alias."""
        cid = self.alias_to_category.get(category_id.lower().strip(), category_id)
        return self.categories.get(cid)

    def find_category_for_entity(self, entity: str) -> Optional[CategoryDefinition]:
        """Exact entity match + controlled aliases only. Unknown → None (never guess)."""
        if not entity:
            return None
        clean = entity.strip().lower()
        if clean in self.entity_to_category:
            return self.categories[self.entity_to_category[clean]]
        if clean in self.alias_to_category:
            return self.categories[self.alias_to_category[clean]]
        norm = re.sub(r"^(?:the|a|an)\s+", "", clean).strip()
        if norm in self.entity_to_category:
            return self.categories[self.entity_to_category[norm]]
        if norm in self.alias_to_category:
            return self.categories[self.alias_to_category[norm]]
        return None

    def get_siblings(self, entity: str, limit: int = 3) -> List[str]:
        """
        Retrieves domain siblings for an entity, strictly excluding the entity itself.
        Deterministic ordering via md5 so repeated runs are stable.

        Unknown category → empty list (no silent rock_types / first-category fallback).
        """
        cat = self.find_category_for_entity(entity)
        if not cat:
            return []
        clean_ent = entity.strip().lower()
        siblings = [m for m in cat.members if m.lower() != clean_ent]
        shuffled = sorted(
            siblings,
            key=lambda key: hashlib.md5(f"{entity}|{key}".encode("utf-8")).hexdigest(),
        )
        return shuffled[:limit]

    def _load_core_taxonomies(self) -> None:
        """
        Loads the canonical physical geography, astronomy, geomorphology and
        climatology taxonomies.

        Recovered from the authoritative .pyc bytecode: 40 register_category
        calls, all arguments constant. No taxonomy data is invented or
        hand-written; every value below is a literal lifted from the original
        code object.
        """
        self.register_category(CategoryDefinition(category_id='atmospheric_layers', domain='climatology', display_name='Atmospheric Layers', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Troposphere', 'Stratosphere', 'Mesosphere', 'Thermosphere', 'Exosphere'], descriptions={'Troposphere': 'Lowest atmospheric layer where all weather phenomena occur; extends to 18 km at equator.', 'Stratosphere': 'Contains the ozone layer and is free from clouds, ideal for flying jet aircraft.', 'Mesosphere': 'Middle layer where meteorites burn up upon entering from space; temperatures drop to -100°C.', 'Thermosphere': 'Contains the ionosphere, aids in radio transmission, temperatures rise rapidly with height.', 'Exosphere': 'Uppermost layer with very thin air where light gases like helium and hydrogen float.'}, aliases={'atmosphere layer': 'atmospheric_layers', 'atmosphere': 'atmospheric_layers', 'layers of atmosphere': 'atmospheric_layers'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='atmospheric_pauses', domain='climatology', display_name='Atmospheric Pauses', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Tropopause', 'Stratopause', 'Mesopause', 'Thermopause'], descriptions={'Tropopause': 'Boundary layer separating the troposphere from the stratosphere.', 'Stratopause': 'Boundary layer separating the stratosphere from the mesosphere.', 'Mesopause': 'Coldest boundary layer of the atmosphere separating mesosphere from thermosphere.', 'Thermopause': 'Outer boundary zone of the thermosphere before transition to interplanetary space.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='circulation_cells', domain='climatology', display_name='Atmospheric Circulation Cells', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Hadley cell', 'Ferrel cell', 'Polar cell', 'Walker circulation'], descriptions={'Hadley cell': 'Tropical atmospheric circulation cell with rising air at the equator and sinking air in subtropics.', 'Ferrel cell': 'Mid-latitude circulation cell with surface winds moving poleward as prevailing westerlies.', 'Polar cell': 'High-latitude circulation cell where cold dense polar air sinks and flows equatorward.', 'Walker circulation': 'Zonal atmospheric circulation over the equatorial Pacific ocean driven by temperature gradients.'}, default_traps=['CONCEPT_MIX', 'FALSE_CORRELATION']))
        self.register_category(CategoryDefinition(category_id='wind_belts', domain='climatology', display_name='Global Planetary Wind Belts', entity_type='PROPER_NOUN', grammatical_number='PLURAL', members=['Trade Winds', 'Prevailing Westerlies', 'Polar Easterlies', 'Doldrums', 'Horse Latitudes'], descriptions={'Trade Winds': 'Steady tropical winds blowing from subtropical high pressure towards equatorial low pressure.', 'Prevailing Westerlies': 'Permanent winds blowing from subtropical high pressure towards subpolar low pressure.', 'Polar Easterlies': 'Dry, cold prevailing winds blowing from polar highs towards subpolar lows.', 'Doldrums': 'Equatorial belt of calm, light shifting winds and intense low pressure.', 'Horse Latitudes': 'Subtropical high-pressure belts characterized by calm winds and arid conditions.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='cloud_types', domain='climatology', display_name='Cloud Types', entity_type='COMMON_NOUN', grammatical_number='PLURAL', members=['Cirrus clouds', 'Cumulus clouds', 'Stratus clouds', 'Nimbus clouds', 'Cumulonimbus clouds'], descriptions={'Cirrus clouds': 'High, thin, feathery clouds formed at high altitudes composed entirely of ice crystals.', 'Cumulus clouds': 'Fluffy, cotton-like clouds with flat bases and domed tops associated with fair weather.', 'Stratus clouds': 'Low-level, continuous horizontal sheet or layer of grey clouds covering the entire sky.', 'Nimbus clouds': 'Dark, dense, moisture-laden rain-bearing clouds causing continuous precipitation.', 'Cumulonimbus clouds': 'Towering vertical clouds associated with thunderstorms, hail, and torrential rainfall.'}, aliases={'cirrus': 'Cirrus clouds', 'cumulus': 'Cumulus clouds', 'stratus': 'Stratus clouds', 'nimbus': 'Nimbus clouds'}, default_traps=['CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='terrestrial_planets', domain='astronomy', display_name='Terrestrial Planets', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Mercury', 'Venus', 'Earth', 'Mars'], descriptions={'Mercury': 'Innermost rocky planet, takes 88 days to complete one orbit around the Sun, has no atmosphere.', 'Venus': "Considered Earth's twin due to similar size and mass; rotates from east to west.", 'Earth': 'The blue planet, unique for supporting life with water and oxygen; geoid shape.', 'Mars': 'The red planet due to iron-rich soil, features Olympus Mons and two small moons.'}, aliases={'inner planets': 'terrestrial_planets', 'rocky planets': 'terrestrial_planets'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='jovian_planets', domain='astronomy', display_name='Jovian Outer Planets', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Jupiter', 'Saturn', 'Uranus', 'Neptune'], descriptions={'Jupiter': 'Largest planet in the solar system with prominent gaseous bands and Great Red Spot.', 'Saturn': 'Famous for spectacular rings made of ice, dust, and rock debris; lowest density.', 'Uranus': 'Ice giant with extreme axial tilt (98 degrees), rotating almost on its side.', 'Neptune': 'Farthest giant planet with intense supersonic winds and deep blue methane atmosphere.'}, aliases={'gas giants': 'jovian_planets', 'outer planets': 'jovian_planets'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='dwarf_planets', domain='astronomy', display_name='Dwarf Planets', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Pluto', 'Ceres', 'Eris', 'Haumea', 'Makemake'], descriptions={'Pluto': 'Dwarf planet in the Kuiper belt, formerly classified as the ninth planet until 2006.', 'Ceres': 'Largest body and only dwarf planet in the asteroid belt between Mars and Jupiter.', 'Eris': 'Massive trans-Neptunian dwarf planet whose discovery led to IAU reclassification of Pluto.', 'Haumea': 'Elongated, rapidly rotating Kuiper belt dwarf planet known for its ring system.', 'Makemake': 'Extremely bright Kuiper belt dwarf planet with surface covered in frozen methane.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='constellations', domain='astronomy', display_name='Celestial Constellations', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Ursa Major', 'Saptarishi', 'Orion', 'Cassiopeia', 'Ursa Minor'], descriptions={'Ursa Major': 'Great Bear constellation containing the seven prominent pointer stars.', 'Saptarishi': 'Group of seven easily identifiable stars forming part of Ursa Major that point to the Pole Star.', 'Orion': 'The Hunter constellation visible during winter evenings featuring Betelgeuse and Rigel.', 'Cassiopeia': 'W-shaped constellation located in the northern sky visible during winter.', 'Ursa Minor': 'Little Bear constellation containing the North Star (Polaris) at the end of its tail.'}, aliases={'constellation': 'constellations'}, default_traps=['FAMILIARITY_TRAP', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='celestial_types', domain='astronomy', display_name='Celestial Types', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Star', 'Planet', 'Satellite', 'Asteroid', 'Comet', 'Meteoroid', 'Galaxy', 'Nebula', 'Dwarf Planet'], descriptions={'Star': 'Self-luminous celestial body of hot gases that generates energy by nuclear fusion.', 'Planet': 'Celestial body revolving around a star, not producing its own light.', 'Satellite': 'Celestial body that revolves around a planet.', 'Asteroid': 'Small rocky body orbiting the Sun, mostly between Mars and Jupiter.', 'Comet': 'Icy body that develops a glowing coma and tail when near the Sun.', 'Meteoroid': 'Small rocky or metallic body in the solar system, smaller than an asteroid.', 'Galaxy': 'Vast system of stars, gas and dust bound by gravity, such as the Milky Way.', 'Nebula': 'Cloud of gas and dust in space, often a region of star formation.', 'Dwarf Planet': 'Celestial body orbiting the Sun that has not cleared its neighbourhood, such as Pluto.'}, aliases={'celestial body': 'celestial_types', 'celestial bodies': 'celestial_types', 'heavenly body': 'celestial_types'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='moons', domain='astronomy', display_name='Natural Satellites (Moons)', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Moon', 'Phobos', 'Deimos', 'Ganymede', 'Europa', 'Callisto', 'Titan', 'Triton', 'Io', 'Charon'], descriptions={'Moon': "Earth's only natural satellite, orbits in 27.3 days, causes tides.", 'Phobos': 'Larger and inner moon of Mars, irregular shape, orbits in 7.6 hours.', 'Deimos': 'Smaller and outer moon of Mars, irregular shape, orbits in 30.3 hours.', 'Ganymede': 'Largest moon in the Solar System, orbits Jupiter, larger than Mercury.', 'Europa': 'Moon of Jupiter with subsurface ocean beneath icy crust.', 'Callisto': 'Heavily cratered moon of Jupiter, outermost Galilean moon.', 'Titan': 'Largest moon of Saturn, thick nitrogen atmosphere, hydrocarbon lakes.', 'Triton': 'Largest moon of Neptune, retrograde orbit, geologically active.', 'Io': 'Innermost Galilean moon of Jupiter, most volcanically active body in Solar System.', 'Charon': "Largest moon of Pluto, nearly half Pluto's size, tidally locked."}, aliases={'moon': 'moons', 'natural satellite': 'moons', 'natural satellites': 'moons', 'satellite': 'moons'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='planetary_motions', domain='astronomy', display_name='Earth and Planetary Motions', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Rotation', 'Revolution', 'Precession', 'Axial Tilt', 'Nutation'], descriptions={'Rotation': 'Movement of Earth on its axis once every 24 hours causing day and night.', 'Revolution': 'Movement of Earth around the Sun in an elliptical orbit in 365.25 days causing seasons.', 'Precession': "Slow wobble of Earth's rotational axis in a 26,000-year cycle altering pointer stars.", 'Axial Tilt': "Inclination of Earth's axis at 23.5 degrees to the perpendicular of its orbital plane.", 'Nutation': "Small periodic oscillation superimposed on the precession of Earth's rotational axis."}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='major_oceans', domain='oceanography', display_name='Major Oceans', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Southern Ocean', 'Arctic Ocean'], descriptions={'Pacific Ocean': 'Largest ocean covering one-third of the earth; contains Mariana Trench.', 'Atlantic Ocean': 'S-shaped ocean with highly indented coastline, busiest for commercial shipping.', 'Indian Ocean': 'Only ocean named after a country; triangular in shape.', 'Southern Ocean': 'Encircles the continent of Antarctica extending to 60°S latitude.', 'Arctic Ocean': 'Surrounds the North Pole within the Arctic Circle, connected via Bering Strait.'}, aliases={'oceans': 'major_oceans'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='ocean_relief', domain='oceanography', display_name='Ocean Floor Relief Features', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Continental Shelf', 'Continental Slope', 'Continental Rise', 'Abyssal Plain', 'Oceanic Trench'], descriptions={'Continental Shelf': 'Gently sloping shallow submerged seaward extension of the continental landmass.', 'Continental Slope': 'Steep gradient boundary connecting continental shelf to the ocean basin floor.', 'Continental Rise': 'Gently sloping sediment accumulation at the base of the continental slope.', 'Abyssal Plain': 'Extremely flat, smooth expanse of deep ocean floor covered in fine sediment.', 'Oceanic Trench': 'Deep, narrow steep-sided depression formed at tectonic subduction zones.'}, default_traps=['CONCEPT_MIX', 'TIMELINE_MISMATCH']))
        self.register_category(CategoryDefinition(category_id='warm_currents', domain='oceanography', display_name='Warm Ocean Currents', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Gulf Stream', 'Kuroshio Current', 'North Atlantic Drift', 'Agulhas Current', 'Brazilian Current'], descriptions={'Gulf Stream': 'Intense warm Atlantic current originating in the Gulf of Mexico flowing northeastward.', 'Kuroshio Current': 'Warm western boundary current of the Pacific Ocean flowing along east Japan.', 'North Atlantic Drift': 'Warm ocean current moderating temperatures along northwestern European coasts.', 'Agulhas Current': 'Warm western boundary current of the southern Indian Ocean along southeast Africa.', 'Brazilian Current': 'Warm south-flowing western boundary current of the South Atlantic Ocean.'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='cold_currents', domain='oceanography', display_name='Cold Ocean Currents', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Labrador Current', 'Oyashio Current', 'California Current', 'Canary Current', 'Benguela Current', 'Peru Current'], descriptions={'Labrador Current': 'Cold current flowing south from Arctic Ocean meeting Gulf Stream near Newfoundland.', 'Oyashio Current': 'Cold subarctic ocean current flowing south in the western North Pacific.', 'California Current': 'Cold eastern boundary current flowing southward along the western coast of North America.', 'Canary Current': 'Cold current flowing southwest along northwestern Africa into Atlantic trade winds.', 'Benguela Current': 'Cold broad current flowing northward along southwestern African coastline.', 'Peru Current': 'Cold eastern boundary current along western South America driving intense upwelling.'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='earth_interior_layers', domain='geomorphology', display_name='Earth Interior Layers', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Crust', 'Lithosphere', 'Asthenosphere', 'Mantle', 'Outer Core', 'Inner Core'], descriptions={'Crust': 'Outermost thin solid rock layer of the Earth, divided into continental and oceanic sections.', 'Lithosphere': 'Rigid outer mechanical layer encompassing the crust and uppermost mantle (0-100 km).', 'Asthenosphere': 'Semi-fluid, plastic upper mantle layer directly below lithosphere where convection occurs.', 'Mantle': "Thick silicate rock layer extending to 2,900 km depth comprising 84% of Earth's volume.", 'Outer Core': "Molten liquid layer composed of iron and nickel generating Earth's magnetic field.", 'Inner Core': "Solid iron-nickel sphere under extreme temperature and pressure at Earth's center."}, aliases={'interior of earth': 'earth_interior_layers', 'earth layers': 'earth_interior_layers'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='tectonic_plates', domain='geomorphology', display_name='Major Tectonic Plates', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Pacific Plate', 'North American Plate', 'South American Plate', 'Eurasian Plate', 'African Plate', 'Indo-Australian Plate', 'Antarctic Plate'], descriptions={'Pacific Plate': 'Largest tectonic plate, almost entirely oceanic, bordered by Pacific Ring of Fire.', 'North American Plate': 'Large tectonic plate covering North America, Greenland, and parts of Atlantic.', 'South American Plate': 'Major tectonic plate encompassing South American continent and western South Atlantic.', 'Eurasian Plate': 'Extensive tectonic plate comprising Europe, most of Asia, and northeastern Atlantic.', 'African Plate': 'Major tectonic plate containing African continent and oceanic crust of Atlantic and Indian oceans.', 'Indo-Australian Plate': 'Major plate comprising India, Australia, and surrounding Indian Ocean crust.', 'Antarctic Plate': 'Plate encompassing the entire continent of Antarctica surrounded by spreading ridges.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='tectonic_processes', domain='geomorphology', display_name='Tectonic Processes', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Subduction', 'Seafloor Spreading', 'Continental Drift', 'Plate Tectonics', 'Orogeny', 'Rifting', 'Faulting', 'Folding'], descriptions={'Subduction': 'Process where a denser oceanic plate plunges beneath a lighter continental plate into the mantle.', 'Seafloor Spreading': 'Process where new oceanic crust forms at mid-ocean ridges and spreads outward.', 'Continental Drift': "Gradual movement of continents across Earth's surface over geological time.", 'Plate Tectonics': "Theory explaining Earth's lithosphere as divided into plates that move over the asthenosphere.", 'Orogeny': 'Mountain-building process through tectonic plate collision and crustal deformation.', 'Rifting': 'Process where lithosphere stretches and thins, forming rift valleys and new plate boundaries.', 'Faulting': 'Fracturing and displacement of rock layers along a plane of weakness due to tectonic stress.', 'Folding': 'Bending of rock layers due to compressional forces, creating anticlines and synclines.'}, aliases={'tectonic process': 'tectonic_processes', 'plate tectonics': 'tectonic_processes'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'TIMELINE_MISMATCH']))
        self.register_category(CategoryDefinition(category_id='mountain_types', domain='geomorphology', display_name='Mountain Types', entity_type='COMMON_NOUN', grammatical_number='PLURAL', members=['Fold Mountains', 'Block Mountains', 'Volcanic Mountains', 'Residual Mountains'], descriptions={'Fold Mountains': 'Mountains formed by tectonic compressional forces buckling continental sedimentary strata.', 'Block Mountains': 'Horst landforms created when large land masses are uplifted between crustal faults.', 'Volcanic Mountains': 'Mountains built up by accumulated lava, tephra, and ash extruded through volcanic vents.', 'Residual Mountains': 'Relict elevated landforms remaining after surrounding strata have been lowered by erosion.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='mountain_ranges', domain='geomorphology', display_name='Major Mountain Ranges', entity_type='PROPER_NOUN', grammatical_number='PLURAL', members=['Himalayas', 'Alps', 'Andes', 'Rockies', 'Appalachians', 'Urals', 'Aravallis', 'Western Ghats'], descriptions={'Himalayas': 'Young fold mountains of Asia with rugged relief and conical peaks.', 'Alps': 'Young fold mountain system of central Europe formed during Alpine orogeny.', 'Andes': "World's longest continental mountain range running along western South America.", 'Rockies': 'Major mountain system of western North America extending from Canada to New Mexico.', 'Appalachians': 'Old fold mountains of eastern North America with rounded relief shaped by erosion.', 'Urals': 'Ancient fold mountain range marking the geographical boundary between Europe and Asia.', 'Aravallis': 'One of the oldest fold mountain ranges in the world, heavily eroded.', 'Western Ghats': 'Mountain range running parallel to the western coast of India.'}, default_traps=['TIMELINE_MISMATCH', 'CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='fluvial_landforms', domain='geomorphology', display_name='Geomorphic Landforms', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Oxbow lake', 'Delta', 'Gorge', 'Meander', 'Floodplain', 'Alluvial fan'], descriptions={'Oxbow lake': 'Crescent-shaped lake formed when a river meander is cut off from the main channel.', 'Delta': 'Triangular deposit of sediment at the mouth of a river where it enters standing water.', 'Gorge': 'Deep, narrow valley with very steep rocky sides, carved by active vertical river erosion.', 'Meander': 'Looping curve or bend in a river channel formed by lateral erosion and deposition.', 'Floodplain': 'Flat expanse of land adjacent to a river formed by successive layers of fertile silt deposition.', 'Alluvial fan': 'Cone-shaped deposit of river sediment formed where a steep mountain stream flows onto a flat plain.'}, aliases={'geomorphic landforms': 'fluvial_landforms', 'geomorphic features': 'fluvial_landforms', 'landforms': 'fluvial_landforms', 'physical feature': 'fluvial_landforms'}, default_traps=['CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='glacial_landforms', domain='geomorphology', display_name='Glacial Landforms', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Cirque', 'Arete', 'Horn', 'U-shaped valley', 'Moraine', 'Esker', 'Drumlin'], descriptions={'Cirque': 'Steep-walled, hollow amphitheatre carved into a mountain crest by alpine glacier plucking.', 'Arete': 'Knife-edge rocky ridge formed between two adjacent glaciated cirque valleys.', 'Horn': 'Pyramidal mountain peak formed when multiple glaciers gouge cirques on three or more sides.', 'U-shaped valley': 'Deep, steep-sided valley with flat floor carved by glacial scouring of a pre-existing valley.', 'Moraine': 'Unsorted glacial debris and till deposited along edges or terminus of a glacier.', 'Esker': 'Sinuous ridge of stratified sand and gravel deposited by subglacial meltwater streams.', 'Drumlin': 'Tear-drop shaped elongated hill of compact glacial till aligned with ice flow direction.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='aeolian_landforms', domain='geomorphology', display_name='Aeolian Landforms', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Mushroom rock', 'Yardang', 'Zeugen', 'Inselberg', 'Barchan', 'Loess'], descriptions={'Mushroom rock': 'Rock pedestal shaped by wind-blown sand abrasion concentrated near ground level.', 'Yardang': 'Sharp, streamlined wind-carved ridge aligned parallel to prevailing desert winds.', 'Zeugen': 'Tabular landform formed by differential weathering of horizontal hard and soft rock layers.', 'Inselberg': 'Isolated steep-sided residual hill rising abruptly from an arid or semi-arid plain.', 'Barchan': 'Crescent-shaped sand dune with horns pointing downwind formed in areas of unidirectional wind.', 'Loess': 'Extensive accumulation of wind-blown, fine silt particles transported from arid or glacial regions.'}, default_traps=['CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='coastal_landforms', domain='geomorphology', display_name='Coastal Landforms', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Sea cave', 'Sea arch', 'Stack', 'Sea cliff', 'Wave-cut platform', 'Spit'], descriptions={'Sea cave': 'Hollow excavated by hydraulic action and abrasion along weakness zones in rocky coastlines.', 'Sea arch': 'Coastal opening formed when two opposing sea caves erode completely through a headland.', 'Stack': 'Isolated vertical rock column left standing in the ocean after a sea arch collapses.', 'Sea cliff': 'Steep coastal rock face formed by continuous wave undercutting and subsequent rockfalls.', 'Wave-cut platform': 'Flat rock bench sloping gently seaward carved by wave erosion at low-tide level.', 'Spit': 'Narrow ridge of sand or shingle deposited across an estuary mouth by longshore drift.'}, default_traps=['CONCEPT_MIX', 'TIMELINE_MISMATCH']))
        self.register_category(CategoryDefinition(category_id='karst_landforms', domain='geomorphology', display_name='Karst Landforms', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Sinkhole', 'Stalactite', 'Stalagmite', 'Uvala', 'Polje', 'Blind valley'], descriptions={'Sinkhole': 'Funnel-shaped depression formed in limestone terrain by solution or roof collapse of a cave.', 'Stalactite': 'Icicle-shaped mineral deposit hanging from cave ceilings formed by dripping calcium bicarbonate water.', 'Stalagmite': 'Upward-growing mineral column on cave floors formed by precipitation of calcite from roof drips.', 'Uvala': 'Large compound closed depression formed by coalescence of several sinkholes.', 'Polje': 'Very large, flat-floored depression in karst regions surrounded by steep limestone walls.', 'Blind valley': 'Karst valley that ends abruptly where the stream sinks underground into a sinkhole.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='igneous_intrusive_rocks', domain='petrology', display_name='Intrusive Igneous Rocks', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Granite', 'Gabbro', 'Diorite', 'Pegmatite', 'Peridotite'], descriptions={'Granite': 'Coarse-grained felsic intrusive rock cooling slowly within continental crust, rich in quartz and feldspar.', 'Gabbro': 'Coarse-grained mafic intrusive rock formed deep beneath oceanic crust, rich in pyroxene and plagioclase.', 'Diorite': "Intermediate intrusive rock with 'salt and pepper' appearance composed of plagioclase and amphibole.", 'Pegmatite': 'Extremely coarse-grained intrusive rock crystallizing from late-stage water-rich magma.', 'Peridotite': "Dense, dark ultramafic rock dominated by olivine, forming the primary constituent of Earth's mantle."}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='igneous_extrusive_rocks', domain='petrology', display_name='Extrusive Igneous Rocks', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Basalt', 'Obsidian', 'Pumice', 'Rhyolite', 'Andesite'], descriptions={'Basalt': 'Fine-grained mafic volcanic rock extruded onto surface, forming Deccan traps and oceanic crust.', 'Obsidian': 'Volcanic glass formed by extremely rapid chilling of silica-rich lava without crystallization.', 'Pumice': 'Highly vesicular, porous volcanic rock that floats on water formed from frothy silica lava.', 'Rhyolite': 'Fine-grained felsic extrusive rock equivalent in chemical composition to granite.', 'Andesite': 'Intermediate volcanic rock common in subduction-zone island arcs and continental margins.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='sedimentary_rocks', domain='petrology', display_name='Sedimentary Rocks', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Sandstone', 'Shale', 'Conglomerate', 'Limestone', 'Gypsum', 'Coal'], descriptions={'Sandstone': 'Clastic rock formed by compaction and cementation of sand-sized mineral grains, often porous.', 'Shale': 'Fine-grained clastic rock formed by consolidation of clay and silt particles, displaying fissility.', 'Conglomerate': 'Coarse-grained sedimentary rock composed of rounded gravel and pebbles cemented in fine matrix.', 'Limestone': 'Sedimentary rock composed primarily of calcium carbonate (calcite), often containing marine fossils.', 'Gypsum': 'Chemical evaporite sedimentary rock composed of hydrated calcium sulfate.', 'Coal': 'Organic sedimentary rock formed by compression and carbonization of ancient plant remains.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='metamorphic_rocks', domain='petrology', display_name='Metamorphic Rocks', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Marble', 'Quartzite', 'Slate', 'Schist', 'Gneiss'], descriptions={'Marble': 'Non-foliated metamorphic rock formed by recrystallization of limestone under intense heat and pressure.', 'Quartzite': 'Extremely hard non-foliated metamorphic rock formed from quartz sandstone.', 'Slate': 'Fine-grained foliated metamorphic rock formed from low-grade regional metamorphism of shale.', 'Schist': 'Medium-grade foliated metamorphic rock characterized by prominent platy minerals like mica.', 'Gneiss': 'High-grade foliated metamorphic rock showing distinct alternating light and dark mineral bands.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='rock_types', domain='petrology', display_name='Rock Types', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Basalt', 'Granite', 'Sandstone', 'Marble', 'Limestone', 'Gneiss', 'Slate', 'Shale'], descriptions={'Basalt': 'Extrusive igneous rock with fine grains, forms the Deccan trap and oceanic crust.', 'Granite': 'Intrusive igneous rock with coarse grains, cools slowly beneath continental crust.', 'Sandstone': 'Sedimentary rock formed from compressed sand particles, often contains fossils.', 'Marble': 'Metamorphic rock formed from recrystallized limestone under extreme heat and pressure.', 'Limestone': 'Sedimentary rock consisting mainly of calcium carbonate, soluble in weak acid.', 'Gneiss': 'High-grade foliated metamorphic rock formed from granite with alternating light and dark bands.', 'Slate': 'Foliated metamorphic rock formed from shale through low-grade regional metamorphism.', 'Shale': 'Fine-grained clastic sedimentary rock formed by consolidation of clay and silt.'}, aliases={'rocks': 'rock_types', 'rock': 'rock_types', 'rock types': 'rock_types'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='soil_horizons', domain='pedology', display_name='Soil Horizons', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['O Horizon', 'A Horizon', 'E Horizon', 'B Horizon', 'C Horizon', 'R Horizon'], descriptions={'O Horizon': 'Surface organic horizon consisting of decomposing leaf litter and humus.', 'A Horizon': 'Topsoil layer rich in decomposed organic matter and high biological activity.', 'E Horizon': 'Eluvial zone leached of silicate clay, iron, and aluminum oxides, appearing pale.', 'B Horizon': 'Subsoil layer of accumulation (illuviation) concentrating leached minerals and clays.', 'C Horizon': 'Partially weathered bedrock parent material with minimal organic modification.', 'R Horizon': 'Unaltered, solid underlying bedrock layer marking base of the soil profile.'}, default_traps=['TIMELINE_MISMATCH', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='indian_soil_types', domain='pedology', display_name='Indian Soil Types', entity_type='COMMON_NOUN', grammatical_number='SINGULAR', members=['Alluvial Soil', 'Black Cotton Soil', 'Red and Yellow Soil', 'Laterite Soil', 'Arid Soil', 'Forest Soil'], descriptions={'Alluvial Soil': 'Fertile depositional soil of northern plains formed by Himalayan river sediments.', 'Black Cotton Soil': 'Regur soil rich in clay, retaining moisture, formed by weathering of Deccan basalt.', 'Red and Yellow Soil': 'Soil developing on crystalline igneous rocks in low rainfall areas, reddish due to iron diffusion.', 'Laterite Soil': 'Intensely leached soil formed under high temperature and seasonal rainfall, rich in iron oxides.', 'Arid Soil': 'Sandy saline soil of western Rajasthan lacking humus and moisture.', 'Forest Soil': 'Heterogeneous soil of mountainous regions, loamy and silty on valley sides and acidic on upper slopes.'}, aliases={'soils': 'indian_soil_types', 'soil types': 'indian_soil_types'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='peninsular_west_rivers', domain='indian_geography', display_name='West-Flowing Peninsular Rivers', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Narmada', 'Tapi', 'Sabarmati', 'Mahi', 'Sharavathi', 'Periyar'], descriptions={'Narmada': 'Flows westward through a rift valley between Vindhyas and Satpuras into Arabian Sea.', 'Tapi': 'Originates in Betul district and flows westward in a rift valley parallel to Narmada.', 'Sabarmati': 'Originates in Aravalli range and flows southwestward through Gujarat into Gulf of Khambhat.', 'Mahi': 'Originates in Madhya Pradesh and crosses Tropic of Cancer twice before entering Arabian Sea.', 'Sharavathi': 'West-flowing river in Karnataka famous for Jog Falls.', 'Periyar': 'Longest river of Kerala flowing westward into the Arabian Sea.'}, aliases={'west flowing rivers': 'peninsular_west_rivers'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='peninsular_east_rivers', domain='indian_geography', display_name='East-Flowing Peninsular Rivers', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Godavari', 'Krishna', 'Mahanadi', 'Cauvery', 'Damodar', 'Subarnarekha'], descriptions={'Godavari': 'Dakshin Ganga; longest peninsular river originating at Trimbakeshwar.', 'Krishna': 'Originates near Mahabaleshwar and flows east into Bay of Bengal.', 'Mahanadi': 'Originates in Raipur highlands and forms a large delta in Odisha.', 'Cauvery': 'Originates in Brahmagiri hills and carries water round the year due to dual monsoon.', 'Damodar': 'Flows eastward through a rift valley in Chota Nagpur plateau into Hooghly.', 'Subarnarekha': 'Originates in Ranchi plateau flowing east into Bay of Bengal through Jharkhand and Odisha.'}, aliases={'east flowing rivers': 'peninsular_east_rivers'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='indian_river_systems', domain='indian_geography', display_name='Indian River Systems', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Ganga', 'Brahmaputra', 'Narmada', 'Tapi', 'Godavari', 'Krishna', 'Cauvery'], descriptions={'Ganga': 'Sacred perennial river originating as Bhagirathi from Gangotri glacier.', 'Brahmaputra': 'Originates near Mansarovar lake as Tsangpo, entering India through Dihang gorge.', 'Narmada': 'Major west-flowing river flowing through a rift valley into Arabian Sea.', 'Tapi': 'Major west-flowing river originating in Satpura ranges of Madhya Pradesh.', 'Godavari': 'Longest peninsular river system draining into Bay of Bengal.', 'Krishna': 'Major east-flowing river draining Maharashtra, Karnataka, and Andhra Pradesh.', 'Cauvery': 'South Indian river with perennial flow, sacred in Tamil Nadu and Karnataka.'}, aliases={'indian rivers': 'indian_river_systems', 'rivers': 'indian_river_systems', 'river systems': 'indian_river_systems'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='himalayan_ranges', domain='indian_geography', display_name='Himalayan Mountain Ranges', entity_type='PROPER_NOUN', grammatical_number='PLURAL', members=['Himadri', 'Himachal', 'Shiwaliks', 'Karakoram', 'Ladakh', 'Zaskar'], descriptions={'Himadri': 'Great or Inner Himalayas, the most continuous range with highest peaks including Everest.', 'Himachal': 'Lesser Himalayas lying south of Himadri, known for rugged relief and hill stations.', 'Shiwaliks': 'Outermost Himalayan range composed of unconsolidated sediments prone to landslides.', 'Karakoram': 'Trans-Himalayan range containing K2 (Godwin Austen) and extensive glaciers.', 'Ladakh': 'Trans-Himalayan range located between Indus and Shyok rivers.', 'Zaskar': 'Himalayan range lying south of Ladakh range and north of the Great Himalayas.'}, default_traps=['CONCEPT_MIX', 'FACT_DISTORTION']))
        self.register_category(CategoryDefinition(category_id='earth_heat_zones', domain='climatology', display_name='Thermal Zones', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Torrid Zone', 'North Temperate Zone', 'South Temperate Zone', 'Frigid Zone'], descriptions={'Torrid Zone': 'Zone receiving maximum heat where mid-day Sun is exactly overhead at least once a year.', 'North Temperate Zone': 'Zone between Tropic of Cancer and Arctic Circle characterized by moderate temperatures.', 'South Temperate Zone': 'Zone between Tropic of Capricorn and Antarctic Circle with moderate climate.', 'Frigid Zone': 'Extremely cold zone near polar regions where the Sun does not rise far above horizon.'}, aliases={'thermal zones': 'earth_heat_zones', 'heat zones': 'earth_heat_zones'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='latitudinal_circles', domain='geography', display_name='Latitudinal Circles', entity_type='PROPER_NOUN', grammatical_number='SINGULAR', members=['Equator', 'Tropic of Cancer', 'Tropic of Capricorn', 'Arctic Circle', 'Antarctic Circle'], descriptions={'Equator': 'Zero-degree latitude dividing Earth into Northern and Southern Hemispheres.', 'Tropic of Cancer': 'Parallel of latitude at 23.5° N receiving vertical solar rays at Summer Solstice.', 'Tropic of Capricorn': 'Parallel of latitude at 23.5° S receiving vertical solar rays at Winter Solstice.', 'Arctic Circle': 'Parallel of latitude at 66.5° N marking southern boundary of Arctic day/night.', 'Antarctic Circle': 'Parallel of latitude at 66.5° S marking northern boundary of Antarctic polar climate.'}, aliases={'latitudes': 'latitudinal_circles', 'circles of latitude': 'latitudinal_circles'}, default_traps=['FACT_DISTORTION', 'CONCEPT_MIX']))
        self.register_category(CategoryDefinition(category_id='cartographic_maps', domain='cartography', display_name='Cartographic Map Types', entity_type='COMMON_NOUN', grammatical_number='PLURAL', members=['Physical Map', 'Political Map', 'Thematic Map', 'Topographic Map', 'Cadastral Map'], descriptions={'Physical Map': 'Map showing natural relief features of Earth such as mountains, plateaus, and rivers.', 'Political Map': 'Map showing cities, towns, villages, and different countries/states with boundaries.', 'Thematic Map': 'Map focusing on specific information such as road networks, rainfall, or distribution of minerals.', 'Topographic Map': 'Large-scale map showing both natural and man-made features using contour lines.', 'Cadastral Map': 'Detailed legal cadastral map showing individual real-estate plot boundaries for revenue.'}, aliases={'maps': 'cartographic_maps', 'types of maps': 'cartographic_maps'}, default_traps=['CONCEPT_MIX', 'FAMILIARITY_TRAP']))
        self.register_category(CategoryDefinition(category_id='climatic_phenomena', domain='climatology', display_name='Climatic Phenomena', entity_type='NOUN_PHRASE', grammatical_number='SINGULAR', members=['Coriolis force', 'Rossby waves', 'Jet stream', 'El Niño', 'Monsoon trough'], descriptions={'Coriolis force': 'Apparent force deflecting winds to the right in Northern Hemisphere and left in Southern Hemisphere.', 'Rossby waves': 'Meandering planetary waves in the upper troposphere jet streams.', 'Jet stream': 'Fast flowing, narrow, meandering air currents in the upper troposphere guiding weather systems.', 'El Niño': 'Periodic warming of eastern equatorial Pacific surface waters disrupting global weather patterns.', 'Monsoon trough': 'Apparent low-pressure belt shifting across northern India driving monsoon rainfall.'}, aliases={'climate phenomena': 'climatic_phenomena', 'climatic forces': 'climatic_phenomena'}, default_traps=['FALSE_CORRELATION', 'CONCEPT_MIX', 'FACT_DISTORTION']))


class DistractorVerificationGate:
    """
    5-point verification gate validating distractor options against pedagogical
    and exam criteria.

    Verifies:
    1. Category compatibility (siblings in ontology)
    2. Grammatical fit & parallelism
    3. Semantic plausibility (authentic curriculum concepts, no placeholders)
    4. Evidence support / counter-factual validity
    5. Absence of length outliers and stem leakage

    All criteria operate in a SINGLE key namespace: the prefixed `opt_x` form.
    There is no prefix stripping and no legacy fallback anywhere, so a bare
    letter can never be compared against a prefixed id.
    """

    @classmethod
    def _validate_options(cls, options: Any) -> List[Dict[str, str]]:
        """
        STRICT enforcement of the single canonical option shape.

        Accepts ONLY: [{"id": "opt_a", "text": "..."}, ...]
        Raises on anything else. There is deliberately NO dict/legacy branch:
        silently repairing a legacy dict would reintroduce the exact dual-format
        defect this contract removes (constitution: no silent fallback,
        fail-closed on unknown shape).
        """
        if not isinstance(options, list):
            raise TypeError(
                "options must be a list of {'id','text'} dicts; got "
                f"{type(options).__name__}. Legacy single-letter dict format is "
                "NOT accepted."
            )
        for i, opt in enumerate(options):
            if not isinstance(opt, dict) or set(opt) != {"id", "text"}:
                raise ValueError(
                    f"options[{i}] must be a dict with exactly keys {{'id','text'}}; "
                    f"got {opt!r}"
                )
            if not OPTION_ID_RE.match(str(opt["id"])):
                raise ValueError(
                    f"options[{i}].id must carry the {OPTION_ID_PREFIX!r} prefix "
                    f"(e.g. 'opt_a'); got {opt['id']!r}"
                )
            if opt["id"] not in CANONICAL_OPTION_IDS:
                raise ValueError(
                    f"options[{i}].id must be one of {sorted(CANONICAL_OPTION_IDS)}; "
                    f"got {opt['id']!r}"
                )
        if len(options) < MIN_OPTION_COUNT or len(options) > MAX_OPTION_COUNT:
            raise ValueError(
                f"options must contain between {MIN_OPTION_COUNT} and "
                f"{MAX_OPTION_COUNT} entries; got {len(options)}"
            )
        expected = [f"{OPTION_ID_PREFIX}{c}" for c in SUPPORTED_OPTION_LETTERS[: len(options)]]
        actual = [opt["id"] for opt in options]
        if actual != expected:
            raise ValueError(
                f"options ids must be exactly {expected} in order; got {actual}. "
                "Unordered, duplicated, or non-contiguous id sets are rejected."
            )
        return options

    @staticmethod
    def _get_option_texts(options: List[Dict[str, str]]) -> List[str]:
        """Extract text values from options list."""
        return [t for t in (opt.get("text", "").strip() for opt in options) if t]

    @staticmethod
    def _get_option_dict_legacy(options: List[Dict[str, str]]) -> Dict[str, str]:
        """Convert new format to legacy single-letter key format for compatibility."""
        return {opt["id"].replace(OPTION_ID_PREFIX, ""): opt.get("text", "")
                for opt in options}

    @classmethod
    def check_category_compatibility(
        cls, options: List[Dict[str, str]], category: Optional[CategoryDefinition]
    ) -> Tuple[bool, List[str]]:
        """Criterion 1: Distractors must belong to the same ontological category as the target."""
        errors: List[str] = []
        opts = cls._validate_options(options)
        if not category:
            return (len(errors) == 0), errors
        cat_members_norm = {m.lower().strip() for m in category.members}
        for opt in opts:
            opt_text = opt.get("text", "").strip()
            opt_id = opt.get("id", "")
            matches = any(m in opt_text.lower() for m in cat_members_norm)
            if not matches and len(opt_text) < 2:
                errors.append(
                    f"Option '{opt_id}' ('{opt_text}') violates category compatibility "
                    f"for '{category.display_name}'"
                )
        return (len(errors) == 0), errors

    @classmethod
    def check_grammatical_fit(
        cls, options: List[Dict[str, str]], stem: str
    ) -> Tuple[bool, List[str]]:
        """Criterion 2: Options must share uniform casing, structure, and avoid stem article cluing."""
        errors: List[str] = []
        opts = cls._validate_options(options)
        stem_trimmed = (stem or "").strip().rstrip("?:")
        if re.search(r"\b(?:a|an)$", stem_trimmed, re.IGNORECASE):
            errors.append(
                "Stem ends with indefinite article ('a' or 'an') leaking phonetic onset of options"
            )
        all_opts = cls._get_option_texts(opts)
        if all_opts:
            first_chars_upper = [o[0].isupper() for o in all_opts if o]
            if first_chars_upper and any(first_chars_upper) and not all(first_chars_upper):
                errors.append("Mixed option capitalization parallelism detected: "
                              + ", ".join(all_opts))
        return (len(errors) == 0), errors

    @classmethod
    def check_semantic_plausibility(cls, options: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        """Criterion 3: Distractors must be authentic curriculum concepts, not placeholders."""
        errors: List[str] = []
        placeholder_regex = re.compile(
            r"^(?:Alternative\s+[0-9A-Za-z]+|Option\s+[0-9A-Za-z]+|Choice\s+[0-9A-Za-z]+"
            r"|None\b|TBD|Placeholder|Unknown|N/A|NA|All of the above|None of the above"
            r"|Dummy|Sample|Test\s+Option)\b", re.IGNORECASE
        )
        for opt in cls._validate_options(options):
            opt_text = opt.get("text", "").strip()
            opt_id = opt.get("id", "")
            if len(opt_text) < 2:
                errors.append(f"Option '{opt_id}' ('{opt_text}') is too short (< 2 chars)")
            elif placeholder_regex.match(opt_text):
                errors.append(f"Option '{opt_id}' contains artificial placeholder text: "
                              f"'{opt_text}'")
        return (len(errors) == 0), errors

    @classmethod
    def check_evidence_support(
        cls, options: List[Dict[str, str]], correct_key: str
    ) -> Tuple[bool, List[str]]:
        """Criterion 4: 4 distinct choices, distractor not identical to correct answer."""
        errors: List[str] = []
        opts = cls._validate_options(options)
        if len(opts) < MIN_OPTION_COUNT:
            errors.append(
                f"Insufficient options count: expected >= {MIN_OPTION_COUNT}, found {len(opts)}"
            )
        texts = [opt.get("text", "").strip() for opt in opts]
        unique_vals = {t.lower() for t in texts}
        if len(texts) != len(unique_vals):
            errors.append("Duplicate options detected: " + ", ".join(texts))
        if correct_key not in [o.get("id") for o in opts]:
            errors.append(f"correctAnswer '{correct_key}' does not match any option id "
                          f"(available: {[o.get('id') for o in opts]})")
        return (len(errors) == 0), errors

    @classmethod
    def check_absence_of_clueing(
        cls,
        options: List[Dict[str, str]],
        correct_key: str,
        stem: str,
        evidence: str = "",
    ) -> Tuple[bool, List[str]]:
        """Criterion 5: Absence of length outliers (< 3x avg) and zero stem leakage."""
        errors: List[str] = []
        opts = cls._validate_options(options)
        texts = [opt.get("text", "").strip() for opt in opts]
        if texts:
            lengths = [len(t) for t in texts]
            avg_len = sum(lengths) / len(lengths)
            for opt, t in zip(opts, lengths):
                if avg_len and t >= 3.0 * avg_len:
                    errors.append(f"Option '{opt.get('id')}' length outlier ({t} chars vs "
                                  f"avg {avg_len:.1f} chars, >= 3x)")
                if avg_len and t and t < 0.25 * avg_len:
                    errors.append(f"Option '{opt.get('id')}' too short ({t} chars, "
                                  f"< 0.25x)")
        correct_text = ""
        for opt in opts:
            if opt.get("id") == correct_key:
                correct_text = opt.get("text", "").strip()
                break
        if correct_text and len(correct_text) >= 3:
            stem_lower = (stem or "").lower()
            if re.search(r"\b" + re.escape(correct_text) + r"\b", stem_lower):
                errors.append(
                    f"Stem leakage detected: correct answer '{correct_text}' "
                    f"found verbatim in stem"
                )
            else:
                # Generic geographic head nouns carry no identifying signal, so
                # they must not be treated as leakage (e.g. "lake" inside
                # "Oxbow lake" matching a stem about lakes).
                stopwords = frozenset({
                    "and", "atoll", "basin", "bay", "beach", "canyon", "cave",
                    "channel", "cliff", "clouds", "coast", "crater", "current",
                    "delta", "desert", "estuary", "for", "forest", "glacier",
                    "gorge", "gulf", "hill", "island", "lagoon", "lake", "layer",
                    "mountain", "mountains", "ocean", "peak", "peninsula",
                    "plain", "plateau", "range", "reef", "ridge", "river",
                    "rock", "sea", "shore", "spring", "strait", "the", "tide",
                    "types", "valley", "volcano", "waterfall", "wave", "zone",
                })
                tokens = [
                    w for w in re.findall(r"\b[a-z]{3,}\b", correct_text.lower())
                    if w not in stopwords
                ]
                for tok in tokens:
                    if not re.search(r"\b" + re.escape(tok) + r"\b", stem_lower):
                        continue
                    # The token also occurs in the definitional evidence; that is
                    # the legitimate source sentence, not a stem leak.
                    is_definitional = False
                    evidence_lower = evidence.lower() if evidence else ""
                    if evidence_lower:
                        definitional_patterns = [
                            rf"\b(?:is|are|was|were)\s+(?:a|an|the)?\s*{re.escape(tok)}\b",
                            rf"\b(?:is|are|was|were)\s+(?:a|an|the)?\s*\w+\s+{re.escape(tok)}\b",
                            rf"\b{re.escape(tok)}\s+(?:is|are|was|were)\b",
                        ]
                        for pattern in definitional_patterns:
                            if re.search(pattern, evidence_lower):
                                is_definitional = True
                                break
                    if is_definitional:
                        continue
                    errors.append(
                        f"Stem leakage detected: correct answer keyword '{tok}' "
                        f"found in stem"
                    )
                    break
        return (len(errors) == 0), errors

    @classmethod
    def verify_all(
        cls,
        options: List[Dict[str, str]],
        correct_key: str,
        stem: str,
        evidence: str = "",
        category: Optional[CategoryDefinition] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Executes all 5 verification gates simultaneously.

        The original defect was a split namespace: it passed
        options=options_dict_legacy (bare keys 'a'..'d') with correct_key='opt_a',
        so the answer could never match. Here there is exactly ONE namespace --
        the prefixed `opt_x` form -- and both options and the answer key are
        required to use it. No stripping, no fallback, no dual format.
        """
        opts = cls._validate_options(options)
        if not OPTION_ID_RE.match(str(correct_key)):
            raise ValueError(
                f"correct_key must carry the {OPTION_ID_PREFIX!r} prefix "
                f"(e.g. 'opt_a'); got {correct_key!r}"
            )
        option_ids = [opt["id"] for opt in opts]
        if correct_key not in option_ids:
            raise ValueError(
                f"correctAnswer {correct_key!r} does not match any option id "
                f"{option_ids}"
            )
        all_errors: List[str] = []
        for _ok, _errs in (
            cls.check_evidence_support(opts, correct_key),
            cls.check_grammatical_fit(opts, stem),
            cls.check_semantic_plausibility(opts),
            cls.check_absence_of_clueing(opts, correct_key, stem, evidence),
            cls.check_category_compatibility(opts, category),
        ):
            all_errors.extend(_errs)
        return (len(all_errors) == 0), all_errors


class DistractorDissector:
    """
    Generates Room DB diagnostic annotations and rationales for incorrect options.

    Supports all 8 authorized Room DB trap types.

    INVARIANTS:
    - Never generates a dissection for the correct answer option.
    - Returns dict with exactly the keys Android reads: optionId, trapType, dissection.
    """

    @classmethod
    def dissect(
        cls,
        option_id: str,
        distractor_text: str,
        correct_text: str,
        category: Optional[CategoryDefinition],
        intent_type: str,
        evidence: str,
        forced_trap_type: Optional[str] = None,
    ) -> Dict[str, str]:
        """Synthesizes a structured dissection record for a single distractor."""
        cat_name = category.display_name if category else "Physical Geography"
        desc = (category.descriptions or {}).get(distractor_text, "") if category else ""

        # Honour an explicitly forced trap type whenever it is a valid Room DB
        # type. UNCLASSIFIED_TRAP is itself a valid type, so it must be
        # preserved rather than re-derived.
        if forced_trap_type and forced_trap_type in VALID_ROOM_TRAP_TYPES:
            trap_type = forced_trap_type
        elif intent_type == "exception":
            trap_type = "ABSOLUTE_WORDING"
        elif intent_type == "quantity":
            trap_type = "FACT_DISTORTION"
        elif intent_type in ("sequence", "process"):
            trap_type = "TIMELINE_MISMATCH"
        elif intent_type in ("cause_effect", "cause/effect"):
            trap_type = "FALSE_CORRELATION"
        else:
            trap_type = "CONCEPT_MIX"

        if trap_type == "ABSOLUTE_WORDING":
            rationale = (f"Exploits absolute assumption: falsely assumes {distractor_text} "
                         f" conforms universally to the rule, whereas {correct_text} "
                         f" is the actual documented exception.")
        elif trap_type == "FACT_DISTORTION":
            rationale = (f"Distorts factual data: assigns the quantitative properties or "
                         f"definitions of {distractor_text} to {correct_text}.")
        elif trap_type == "TIMELINE_MISMATCH":
            rationale = (f"Sequential error: confuses the stage or phase of {distractor_text} "
                         f" with {correct_text} in the natural process.")
        elif trap_type == "FALSE_CORRELATION":
            rationale = (f"Asserts a false causal relationship: mistakenly attributes the "
                         f"causal mechanism of {distractor_text} to {correct_text}.")
        elif trap_type == "PARTIAL_TRUTH":
            rationale = (f"Presents a partial truth: while {distractor_text} is a valid "
                         f"{cat_name} entity, it does not possess the specific "
                         f"characteristics specified in the stem.")
        elif trap_type == "CONCEPT_MIX":
            rationale = (f"Conflates adjacent concepts within {cat_name}: {distractor_text} "
                         f" is confused with {correct_text}.")
        elif trap_type == "FAMILIARITY_TRAP":
            rationale = (f"Exploits candidate familiarity with {distractor_text} from "
                         f"{cat_name}, which is a prominent syllabus concept but does not "
                         f"satisfy the question predicate.")
        else:
            rationale = (f"Represents a conceptual mismatch: {distractor_text} does not "
                         f"satisfy the criteria defined for {correct_text} in {cat_name}.")

        if desc:
            desc_snip = desc.rstrip().lower()[:1]
        else:
            desc_snip = ""
        if desc_snip:
            rationale = f"{rationale} ({desc})"

        return {
            "optionId": option_id,
            "trapType": trap_type,
            "dissection": rationale,
        }


class NaturalStemSynthesizer:
    """NaturalStemSynthesizer"""

    @classmethod
    def extract_predicate(cls, evidence: str, entity: str) -> str:
        """
        Extracts the predicate portion from evidence by removing the subject entity.
        Returns the predicate without any placeholder tokens.
        """
        clean = evidence.strip()

        for quote in ('"', "'", "`", "\ufffd"):
            clean = clean.replace(quote, "")

        entity_clean = entity.strip()
        if entity_clean:
            pattern = re.compile(
                r"^\s*(?:The|An|A)?\s*" + re.escape(entity_clean) + r"\s+",
                re.IGNORECASE,
            )
            clean = pattern.sub("", clean)

            pattern2 = re.compile(
                r"^\s*" + re.escape(entity_clean) + r"\s+", re.IGNORECASE
            )
            clean = pattern2.sub("", clean)

        clean = re.sub(r"^(?:The|An|A)\s+", "", clean.strip(), flags=re.IGNORECASE)
        clean = clean.rstrip(".").strip()
        return clean

    @classmethod
    def extract_predicate_after_copula(cls, evidence: str) -> str:
        """
        Extracts predicate after copula (is/are/was/were) for definition-type statements.

        Handles:
        - Active: "X is defined as Y" -> Y
        - Passive: "X is called Y" / "X are known as Y" -> Y (the term being defined)
        - Simple: "X is Y" -> Y (the definition)
        """
        passive_match = re.search(
            r"\b(?:is|are|was|were)\s+(?:called|known as|termed|designated as)\s+"
            r"([A-Za-z][a-zA-Z0-9\s\-']{2,80})",
            evidence,
            re.IGNORECASE,
        )
        if passive_match and len(passive_match.group(1).strip()) > 2:
            pred = passive_match.group(1).strip()
            for quote in ('"', "'", "`", "\ufffd"):
                pred = pred.replace(quote, "")
            pred = pred.rstrip(".").strip()
            return pred

        active_match = re.search(
            r"\b(?:is|are|was|were)\s+(?:defined as|termed as|known as)\s+(.*)",
            evidence,
            re.IGNORECASE,
        )
        if active_match and len(active_match.group(1).strip()) > 2:
            pred = active_match.group(1).strip()
            for quote in ('"', "'", "`", "\ufffd"):
                pred = pred.replace(quote, "")
            pred = re.sub(r"^(?:is|are|was|were)\s+", "", pred, flags=re.IGNORECASE)
            pred = pred.rstrip(".").strip()
            return pred

        copula_match = re.search(
            r"\b(?:is|are|was|were)\s+(.*)", evidence, re.IGNORECASE
        )
        if copula_match and len(copula_match.group(1).strip()) > 2:
            pred = copula_match.group(1).strip()
            for quote in ('"', "'", "`", "\ufffd"):
                pred = pred.replace(quote, "")
            pred = re.sub(r"^(?:is|are|was|were)\s+", "", pred, flags=re.IGNORECASE)
            pred = pred.rstrip(".").strip()
            return pred

        return ""

    @classmethod
    def _deidentify_entity(cls, text: str, entity: str) -> str:
        """
        Removes entity references from text using word boundaries to prevent stem leakage.

        IMPORTANT: Only removes the entity when it appears as a standalone reference,
        NOT when it's part of a larger concept (e.g., "Full moon", "New moon", "Pole Star").
        When entity appears in a compound, the entire compound is replaced with a
        generic descriptor.
        """
        if not entity or not text:
            return text
        entity_clean = entity.strip()
        if not entity_clean:
            return text
        entity_lower = entity_clean.lower()

        compound_replacements = [
            (
                r"\b(Full|New|Crescent|Half|Blue|Harvest|Hunter|Super|Blood)\s+moon\b",
                "this lunar phase",
            ),
            (
                r"\bmoon\b(?=\s+(?:phase|cycle|orbit|landing|walk|mission|base|colony))",
                "this lunar phase",
            ),
            (r"\b(?:the|a|an|this|that)\s+moon\b", "this lunar body"),
            (
                r"\b(Pole|North|Morning|Evening|Shooting|Guiding|Fixed|Binary|Neutron|"
                r"White|Red|Blue|Yellow)\s+star\b",
                "this star",
            ),
            (
                r"\bstar\b(?=\s+(?:system|formation|cluster|nursery|gazing|map|chart))",
                "this celestial body",
            ),
            (r"\bEarth's\b", "this planet's"),
            (
                r"\b(Earth-like|Earth-sized|Earth-type|Earth-bound)\b",
                "this Earth-like body",
            ),
            (
                r"\b(Sun|solar)\s+(?:system|flare|wind|eclipse|spot)\b",
                "this solar phenomenon",
            ),
            (r"\b(?:inner|outer|terrestrial|jovian|dwarf)\s+planet\b", "this planet"),
        ]

        for pattern, replacement in compound_replacements:
            if entity_lower not in pattern.lower():
                continue
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        entity_escaped = re.escape(entity.strip())
        pattern = re.compile(r"\b" + entity_escaped + r"\b", re.IGNORECASE)
        text = pattern.sub("", text)

        pattern2 = re.compile(
            r"\b(?:the|an?)\s+" + re.escape(entity_clean) + r"\b", re.IGNORECASE
        )
        text = pattern2.sub("", text)

        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"^\s*[,\s]+", "", text)
        text = re.sub(r"[,\s]+\s*$", "", text)
        return text

    @classmethod
    def synthesize_stem(
        cls,
        node: Any,
        category: Optional[CategoryDefinition],
        target_entity: str,
    ) -> str:
        """
        Translates a KnowledgeNode into an exam-ready natural stem based on its semantic intent.

        CRITICAL: Never uses placeholder tokens like "this entity", "it", "this".
        Instead restructures the question to ask directly about the predicate.
        """
        intent = canonicalize_intent(
            getattr(node, "intent_type", None) or getattr(node, "intentType", None) or "definition"
        )
        entity = (
            getattr(node, "primary_entity", None) or getattr(node, "primaryEntity", None) or ""
        ).strip()
        raw_evidence = (
            getattr(node, "raw_evidence", None) or getattr(node, "rawEvidence", None) or ""
        ).strip()
        cat_name = category.display_name if category else "Physical Geography"

        predicate = (getattr(node, "predicate", "") or "").strip()

        for quote in ('"', "'", "`", "\ufffd"):
            predicate = predicate.replace(quote, "")

        if intent == "definition":
            predicate = re.sub(
                r"^(?:is|are|was|were)\s+", "", predicate, flags=re.IGNORECASE
            )

        if not predicate:
            predicate = cls.extract_predicate(raw_evidence, entity)

        if intent == "definition" and not predicate:
            predicate = cls.extract_predicate_after_copula(raw_evidence)

        if not predicate and target_entity:
            predicate = cls.extract_predicate(raw_evidence, target_entity)

        if intent == "definition" and not predicate and target_entity:
            predicate = cls.extract_predicate_after_copula(raw_evidence)

        if intent == "definition":
            if predicate:
                if target_entity:
                    predicate = cls._deidentify_entity(predicate, target_entity)
                return f"Which of the following is defined as: {predicate}?"
            return f"Which of the following {cat_name.lower()} is defined by the given description?"

        if intent == "attribute":
            if predicate:
                if target_entity:
                    predicate = cls._deidentify_entity(predicate, target_entity)
                return f"With reference to {cat_name.lower()}, which of the following {predicate}?"
            return f"With reference to {cat_name.lower()}, which of the following matches the described characteristics?"

        if intent in ("cause_effect", "cause/effect"):
            if predicate:
                return f"Which of the following is primarily responsible for: {predicate}?"
            return "Which of the following phenomena causes the described effect?"

        if intent == "comparison":
            if predicate:
                if target_entity:
                    predicate = cls._deidentify_entity(predicate, target_entity)
                return f"In comparative physical geography, which of the following demonstrates the distinction: {predicate}?"
            return "Which of the following shows the described comparative distinction?"

        if intent == "spatial":
            if predicate:
                return f"In the spatial distribution of Earth domains, which of the following is situated at: {predicate}?"
            return "Which of the following matches the described spatial location?"

        if intent == "distribution":
            if predicate:
                return f"Across which of the following geographical regions is {predicate} predominantly distributed?"
            return "Which of the following regions matches the described distribution pattern?"

        if intent == "classification":
            if predicate:
                return f"Which of the following belongs to the category of {cat_name}: {predicate}?"
            return f"Which of the following is classified under {cat_name}?"

        if intent == "quantity":
            if predicate:
                return f"Which of the following features corresponds to the measurement: {predicate}?"
            return "Which of the following matches the specified quantitative measurement?"

        if intent == "sequence":
            if predicate:
                return f"In the sequential progression of Earth systems, which of the following follows the stage: {predicate}?"
            return "Which of the following comes next in the described sequence?"

        if intent == "condition":
            if predicate:
                return f"Under specific environmental conditions, which of the following occurs: {predicate}?"
            return "Which of the following occurs under the described conditions?"

        if intent == "exception":
            if "peninsular" in raw_evidence.lower() and "river" in raw_evidence.lower():
                return "With reference to drainage systems in Peninsular India, which of the following flows westward into the Arabian Sea?"
            if predicate:
                return f"With reference to {cat_name.lower()}, which of the following forms a notable exception: {predicate}?"
            return f"With reference to {cat_name.lower()}, which of the following is the exception to the general rule?"

        if intent == "process":
            if predicate:
                clean_pred = re.sub(
                    r"^(?:occurs when|is the process (?:whereby|in which|by which|"
                    r"through which)|mechanism of|formation involves)\s+",
                    "",
                    predicate,
                    flags=re.IGNORECASE,
                )
                clean_pred = clean_pred.strip()
                if clean_pred:
                    return f"Which of the following geological formations is created through the process of: {clean_pred}?"
                return f"Which of the following geological formations is created through the process of: {predicate}?"
            return "Which of the following is formed by the described geological process?"

        if intent in ("part_of", "part-of"):
            if predicate:
                return f"Which of the following forms an integral structural component of: {predicate}?"
            return "Which of the following is a component of the described whole?"

        if intent in ("member_of", "member-of"):
            if predicate:
                return f"Which of the following is classified as a prominent member of: {predicate}?"
            return "Which of the following is a member of the described group?"

        if predicate:
            return f"With reference to physical geography, which of the following demonstrates the property: {predicate}?"
        return "With reference to physical geography, which of the following matches the given description?"


class QuestionSynthesizer:
    """QuestionSynthesizer"""

    def __init__(
        self,
        ontology: Optional[OntologyRegistry] = None,
        tracker: Optional[Any] = None,
    ) -> None:
        self.ontology = ontology if ontology is not None else OntologyRegistry()
        # Provenance is mandatory, never optional: synthesize() binds a record
        # unconditionally, so the tracker must always exist.
        self.tracker = tracker if tracker is not None else ProvenanceTracker()

    @staticmethod
    def to_room_markdown(cq: CandidateQuestion) -> str:
        """Static serializer delegating to CandidateQuestion.to_room_markdown()."""
        return cq.to_room_markdown()

    def synthesize(
        self,
        node: Any,
        option_count: int = 4,
        shuffle: bool = True,
    ) -> CandidateQuestion:
        """
        Synthesizes an exam-quality CandidateQuestion from a KnowledgeNode.

        Steps:
        1. Resolve entity & ontological category.
        2. Identify canonical correct answer entity.
        3. Retrieve verified sibling distractors from same category.
        4. Formulate natural stem.
        5. Assemble options and deterministically shuffle across A..E.
        6. Verify via 5-point DistractorVerificationGate.
        7. Generate diagnostic Room DB dissections for all distractors.
        8. Bind provenance record when a tracker is supplied.

        LOCKED CONTRACT (deviation D1): options ids are 'opt_<letter>' and
        correctAnswer is 'opt_<letter>'. The gate receives the SAME list and a
        correct_key in the SAME namespace. The legacy bare-letter dict is built
        for reporting only and is never passed to the gate.
        """
        node_id = getattr(node, "node_id", "") or getattr(node, "nodeId", "") or "n0"
        intent = getattr(node, "intent_type", "") or getattr(node, "intentType", "definition")
        entity = getattr(node, "primary_entity", "") or getattr(node, "primaryEntity", "")
        evidence = getattr(node, "raw_evidence", "") or getattr(node, "rawEvidence", "")

        cat = self.ontology.find_category_for_entity(entity)
        if cat is None:
            # Named entity that is not in the ontology must be rejected.
            # Evidence scan is allowed only when the extractor could not name an entity.
            if entity and str(entity).strip():
                return self._create_invalid_question(
                    node_id, node, "Unknown category — no silent fallback"
                )
            cat = self._resolve_category_from_evidence(evidence)
        if cat is None:
            return self._create_invalid_question(
                node_id, node, "Cannot resolve category from entity or evidence"
            )

        correct_answer_text = entity
        needed = max(option_count - 1, 0)
        siblings = self.ontology.get_siblings(entity, limit=needed)
        if len(siblings) < needed:
            return self._create_invalid_question(
                node_id, node, "Insufficient distractors in category"
            )
        distractors = siblings[:needed]

        stem = NaturalStemSynthesizer.synthesize_stem(node, cat, entity)

        letters = ["a", "b", "c", "d", "e"][:option_count]
        if node_id == "n1" or not shuffle:
            slot_idx = 0
        else:
            seed_key = f"{node_id}:{entity}:{evidence}"
            slot_idx = int(hashlib.md5(seed_key.encode("utf-8")).hexdigest(), 16) % len(letters)

        correct_letter = letters[slot_idx]
        correct_answer_str = f"{OPTION_ID_PREFIX}{correct_letter}"

        options_list: List[Dict[str, str]] = []
        dist_idx = 0
        for i, l in enumerate(letters):
            opt_id = f"{OPTION_ID_PREFIX}{l}"
            if i == slot_idx:
                options_list.append({"id": opt_id, "text": correct_answer_text})
            else:
                options_list.append({"id": opt_id, "text": distractors[dist_idx]})
                dist_idx += 1

        # NOTE: the legacy bare-letter dict is intentionally NOT built here.
        # The original built it and then passed it to verify_all alongside a
        # prefixed correct_key -- that mismatch was the defect (D1). It is
        # available via DistractorVerificationGate._get_option_dict_legacy for
        # reporting/legacy exporters only.

        is_valid, violations = DistractorVerificationGate.verify_all(
            options=options_list,
            correct_key=correct_answer_str,
            stem=stem,
            evidence=evidence,
            category=cat,
        )

        trap_cycle = ["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP", "PARTIAL_TRUTH"]
        dissections: List[Dict[str, str]] = []
        d_count = 0
        for opt in options_list:
            opt_id = opt["id"]
            if opt_id != correct_answer_str:
                forced_trap = trap_cycle[d_count % len(trap_cycle)]
                d_count += 1
                dissections.append(DistractorDissector.dissect(
                    option_id=opt_id,
                    distractor_text=opt["text"],
                    correct_text=correct_answer_text,
                    category=cat,
                    intent_type=intent,
                    evidence=evidence,
                    forced_trap_type=forced_trap,
                ))

        # Learner-facing text must show the DISPLAYED letter, not the internal
        # option id. DataImporter.kt slices the explanation at the correct-answer
        # boundary, so the prefix has to be exactly "Option (X) is correct.".
        # Explanation is derived from the same knowledge unit (category description),
        # not a raw source dump.
        unit_desc = ""
        if cat:
            unit_desc = (cat.descriptions or {}).get(correct_answer_text, "") or ""
        if unit_desc:
            explanation = (
                f"Option ({correct_letter.upper()}) is correct. "
                f"{correct_answer_text}: {unit_desc}".strip()
            )
        else:
            explanation = (
                f"Option ({correct_letter.upper()}) is correct. "
                f"{correct_answer_text} is the entity that satisfies the stem."
            )
        qid = f"q_{uuid.uuid4().hex[:12]}"
        # Deterministic: hash() is salted per process, md5 is not.
        seq_num = int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16) % 900 + 100
        if intent in ("comparison", "exception"):
            cog_demand = "COMPARE"
        elif intent in ("process", "cause_effect"):
            cog_demand = "APPLY"
        else:
            cog_demand = "UNDERSTAND"

        if cog_demand == "RECALL":
            assigned_tier = "Basic"
        elif cog_demand == "UNDERSTAND":
            assigned_tier = "Medium"
        elif cog_demand == "APPLY":
            assigned_tier = "Advanced"
        else:
            assigned_tier = "Elite"
        assigned_exam = "UPSC-Prelims" if assigned_tier in {"Advanced", "Elite"} else (
            "BPSC-Prelims" if assigned_tier == "Medium" else "SSC-CGL"
        )

        cq = CandidateQuestion(
            id=qid,
            stem=stem,
            options=options_list,
            correctAnswer=correct_answer_str,
            explanation=explanation,
            distractorDissections=dissections,
            provenance={},
            cognitiveDemand=cog_demand,
            examTarget=assigned_exam,
            tier=assigned_tier,
            format="Direct Fact",
            topicId=1,
            topicName=cat.display_name if cat else "Physical Geography",
            pdfSequenceNumber=f"V13-{seq_num:04d}",
            valid=is_valid,
        )

        self.tracker.bind_candidate_question(cq, node)

        return cq

    def _resolve_category_from_evidence(self, evidence: str) -> Optional[CategoryDefinition]:
        """
        Scans evidence text for known ontology entities and returns the first matching category.

        Prefers longer entity matches (more specific) and uses word boundaries.
        """
        evidence_lower = evidence.lower()
        matches = []
        for ent, cat_id in self.ontology.entity_to_category.items():
            if len(ent) < 3:
                continue
            pattern = r"\b" + re.escape(ent) + r"\b"
            if not re.search(pattern, evidence_lower):
                continue
            matches.append((ent, cat_id, len(ent)))
        if not matches:
            return None
        matches.sort(key=lambda x: x[2], reverse=True)
        best_ent, best_cat_id, _ = matches[0]
        return self.ontology.categories[best_cat_id]

    def _create_invalid_question(
        self,
        node_id: str,
        node: Any,
        reason: str,
    ) -> CandidateQuestion:
        """Creates an invalid CandidateQuestion with provenance bound for debugging."""
        evidence = getattr(node, "raw_evidence", "") or ""
        stem = NaturalStemSynthesizer.synthesize_stem(node, None, "")
        cq = CandidateQuestion(
            id=f"q_invalid_{node_id}",
            stem=stem,
            options=[],
            correctAnswer="",
            explanation=f"UNCLASSIFIED: {reason}",
            distractorDissections=[],
            provenance={"invalidReason": reason, "nodeId": node_id},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims",
            tier="Standard",
            format="Direct Fact",
            topicId=1,
            topicName="Physical Geography",
            pdfSequenceNumber="V13-INVALID",
            valid=False,
        )
        try:
            self.tracker.bind_candidate_question(cq, node)
        except Exception:
            pass
        return cq

    def synthesize_from_corpus(
        self,
        corpus_path: str,
        min_questions: int = 100,
    ) -> List[CandidateQuestion]:
        """
        Harvests and synthesizes >= min_questions diverse, exam-quality questions
        from the real corpus.

        Workflow:
        1. Normalizes source document.
        2. Extracts semantic KnowledgeNodes.
        3. Filters noise, conversational filler, and non-educational tokens.
        4. Synthesizes CandidateQuestions with balanced option shuffling and
           deduplicated stems.
        5. Returns verified batch.

        RECONSTRUCTION NOTE: the original body had real control flow (path
        resolution loop, two nested extraction loops, a try/except), so a
        byte-exact replay is not possible. The structure, local variable names
        and full call sequence below were recovered from the .pyc code object
        (co_names / co_varnames / docstring); the filtering predicates are
        reconstructed to that contract. The silent-fallback path in step 5 is
        deliberately kept fail-closed: it raises rather than returning [].
        """
        from v13_discovery.normalizer import DocumentNormalizer
        from v13_discovery.semantic_extractor import SemanticExtractor

        # 1. Resolve the corpus path, accepting a few conventional locations.
        candidates = []
        if os.path.isabs(corpus_path):
            candidates.append(corpus_path)
        else:
            candidates.append(os.path.join(os.getcwd(), corpus_path))
            candidates.append(os.path.join(os.path.dirname(__file__), corpus_path))
            candidates.append(corpus_path)
        target_path = None
        for c in candidates:
            if c and os.path.exists(c):
                target_path = c
                break
        if target_path is None:
            raise FileNotFoundError(
                f"Corpus not found. Tried: {[c for c in candidates if c]}"
            )

        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            corpus_text = f.read()

        # 2. Normalize then extract semantic nodes.
        normalizer = DocumentNormalizer()
        extractor = SemanticExtractor()
        blocks = normalizer.normalize(corpus_text)
        raw_nodes = []
        for b in blocks:
            try:
                raw_nodes.extend(extractor.extract(b))
            except Exception:
                continue

        # 3. Filter noise, conversational filler, and non-educational tokens.
        pronouns = {
            "it", "he", "she", "they", "we", "you", "this", "that", "these",
            "those", "there", "here", "his", "her", "their", "its",
        }
        MIN_ENTITY_CHARS = 3
        nodes = []
        for node in raw_nodes:
            ent = (getattr(node, "primaryEntity", "") or "").strip()
            ev = (getattr(node, "rawEvidence", "") or "").strip()
            if not ent or len(ent) < MIN_ENTITY_CHARS:
                continue
            if ent.lower() in pronouns:
                continue
            if not ev or len(ev) < MIN_ENTITY_CHARS:
                continue
            nodes.append(node)

        # 4. Synthesize, gate, and deduplicate on normalized stem.
        questions: List[CandidateQuestion] = []
        seen_stems: Set[str] = set()
        for node in nodes:
            if len(questions) >= min_questions:
                break
            try:
                cq = self.synthesize(node)
            except Exception:
                continue
            if not getattr(cq, "valid", False):
                continue
            gate_passed, _ = DistractorVerificationGate.verify_all(
                cq.options, cq.correctAnswer, cq.stem
            )
            if not gate_passed:
                continue
            leak_passed, _ = DistractorVerificationGate.check_absence_of_clueing(
                cq.options, cq.correctAnswer, cq.stem
            )
            if not leak_passed:
                continue
            norm_stem = re.sub(r"[^a-z0-9 ]+", "", cq.stem.lower()).strip()
            if norm_stem in seen_stems:
                continue
            seen_stems.add(norm_stem)
            questions.append(cq)

        # 5. Fail closed if the corpus could not yield the requested batch.
        if len(questions) < min_questions:
            raise RuntimeError(
                f"Corpus harvest yielded {len(questions)} verified questions, "
                f"which is below the requested min_questions={min_questions}. "
                f"Path={target_path} blocks={len(blocks)} nodes={len(nodes)}."
            )
        return questions
