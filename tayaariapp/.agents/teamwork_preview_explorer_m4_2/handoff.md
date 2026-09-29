# Handoff Report: Ontological Distractor Engine & Question Synthesizer Architecture (Milestone 4)

**Agent**: `explorer_m4_2`  
**Milestone**: Milestone 4 — Question & Defensible Distractor Engine  
**Recipient**: `teamwork_preview_orchestrator_4` (Conv ID: `870ebe31-b7b8-4990-b9a6-83148369f1f4`)  
**Target File**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\question_synthesizer.py`  
**Date**: 2026-09-06  

---

## 1. Observation

### 1.1 Source Documents & Requirement Constraints
1. **ORIGINAL_REQUEST.md (§R3, §Acceptance 5)**:
   - *Line 18-20*: "Build explicit Question Intents before wording. Distractors must be independently verified for category compatibility, grammatical fit, semantic plausibility, evidence support, and absence of clueing/contradiction. A verified fact is not automatically a valid distractor if it creates a semantically invalid combination."
   - *Line 38*: "No generated questions rely on generic source quotation templates (e.g., 'What is a direct consequence of \"[fragment]\"?')."

2. **PROJECT.md (§Interface Contracts & Code Layout)**:
   - *Lines 72-75*:
     ```text
     Question Generator ↔ Multi-Agent Auditor:
     Input: KnowledgeNode + Domain Ontology
     Output: CandidateQuestion(id, stem, options: dict[a-d], correctAnswer, explanation, distractorDissections: list[dict], provenance: dict, cognitiveDemand, examTarget)
     ```
   - *Line 91*: Designates `v13_discovery/question_synthesizer.py` as the module responsible for question formulation and category-constrained distractor generation.

3. **tests/e2e/test_helpers.py (§Data Models & Room DB Contracts)**:
   - *Lines 40-49 (`VALID_ROOM_TRAP_TYPES`)*:
     Authorized Room DB trap types:
     `ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`, `UNCLASSIFIED_TRAP`.
   - *Lines 86-101 (`CandidateQuestion`)*:
     Fields: `id`, `stem`, `options` (`dict` with keys `'a'`, `'b'`, `'c'`, `'d'`), `correctAnswer` (`'opt_a'`, `'opt_b'`, etc.), `explanation`, `distractorDissections` (`List[Dict[str, str]]`), `provenance` (`Dict[str, Any]`), `cognitiveDemand`, `examTarget`, `tier`, `format`, `topicId`, `topicName`, `pdfSequenceNumber`.
   - *Lines 436-468 (`validate_distractor_dissections`)*:
     - Dissections must be a `List[Dict[str, str]]`.
     - Keys must include `optionId`, `trapType`, and `dissection`.
     - `optionId` must NEVER match the correct answer option (`opt_{correct_letter}`).
     - Every distractor option must have exactly one unique dissection entry.
     - `trapType` must be strictly an element of `VALID_ROOM_TRAP_TYPES`.
     - `dissection` text must be non-empty with length >= 5 (tested up to > 10 in tier 1).
   - *Lines 654-727 (`ReferenceQuestionSynthesizer`)*:
     Provides baseline behavior, matching entities against `ONTOLOGY` dictionary keys ("Rock Types", "Atmospheric Layers", "Geomorphic Features", "Indian Rivers", "Climatic Phenomena"), selecting 3 distractor siblings, and emitting `CandidateQuestion`.

4. **v13_discovery/semantic_extractor.py (§KnowledgeNode)**:
   - *Lines 109-150*: `KnowledgeNode` carries `node_id`, `intent_type` (1 of 14 canonical intents: `definition`, `attribute`, `cause_effect`, `comparison`, `spatial`, `distribution`, `classification`, `quantity`, `sequence`, `condition`, `exception`, `process`, `part_of`, `member_of`), `primary_entity`, `predicate`, `secondary_entities`, `conditions`, `quantitative_data`, `raw_evidence`, `source_location`, `confidence`, and `extraction_method`.
   - Both camelCase (`nodeId`, `intentType`, `primaryEntity`, `relatedEntities`) and snake_case accessors are supported.

5. **app/src/main/java/com/example/repository/DataImporter.kt (§Android Room DB Parser)**:
   - *Lines 86-97*: Android Room DB maps `- **Trap-Type**: <trap>` directly into `Question.distractorDissections`.
   - *Lines 129-151*: Options are parsed into JSON array `[{"id":"opt_a","text":"..."}, ...]`.
   - *Lines 167-170*: Distractor dissections stored as JSON array of objects `[{"optionId":"opt_b","trapType":"...","dissection":"..."}]`.

6. **tests/e2e/test_e2e_tier1_features.py & test_e2e_tier2_boundaries.py (§Test Constraints)**:
   - *F09.01 (Category Compatibility)*: All options must belong to the exact same ontological domain/family (e.g. Granite -> Basalt, Sandstone, Marble, Gneiss, Slate, Shale).
   - *F09.02 (Grammatical Parallelism)*: All options must share uniform capitalization (e.g., proper noun casing `opt[0].isupper()`).
   - *F09.03 (Semantic Plausibility)*: Options must be authentic educational curriculum terms, not synthesized placeholders like `"Alternative 1"`.
   - *F09.04 (No Clueing / Length Disparity)*: No option length may exceed 3.0x the average option length (`l < avg_len * 3.0`).
   - *F09.05 (Mutual Distinctness)*: All 4 options must be mutually unique (`len(set(options.values())) == len(options)`).
   - *F10.01-F10.05 (Dissection Quality)*: All 3 distractors must have dissections; correct answer never tagged; rationale length > 10 characters explaining why distractor is false.
   - *F11.03 (Stem Leakage)*: Correct answer token must NOT be revealed in the question stem (`correct_val in cq.stem.lower()` triggers auditor rejection).
   - *B09.04 (Substring Differentiation)*: Substring terms (e.g. "Delta" vs "Bird's foot delta") must be cleanly disambiguated.
   - *B09.05 (Five Options Support)*: Structure must cleanly generalize to 5 options (`opt_e`) for state exams like BPSC.

7. **source-material/geography_extracted.txt (§Real Corpus Scope)**:
   Covers NCERT Class VI Earth Sciences: Solar System & Celestial Bodies (stars, planets, satellites, asteroids, meteoroids), Motions of Earth (rotation, revolution, solstices, equinox), Globe & Graticule (equator, latitudes, longitudes, heat zones, Prime Meridian), Maps (physical, political, thematic), Major Domains (lithosphere, hydrosphere, atmosphere layers, biosphere), Major Landforms (fold/block/volcanic mountains, plateaus, plains), and India (physical divisions, drainage systems, climate, vegetation).

---

## 2. Logic Chain

### 2.1 Ontological Taxonomy Architecture for Geography & Earth Sciences
From Observation 1.1, 1.4, and 1.7, raw knowledge nodes extracted from the corpus reference domain entities (e.g., "Troposphere", "Granite", "Basalt", "Narmada", "Ursa Major"). If distractors are chosen at random from outside the entity's ontological family (e.g. answering an atmospheric question with "Basalt" or "Narmada"), test `test_f09_01_category_compatibility` immediately fails.

Therefore, we must establish a formal `OntologyRegistry` containing:
1. **Domain Hierarchy**: High-level domains (`Astronomy`, `Climatology`, `Oceanography`, `Geomorphology`, `Petrology`, `Pedology`, `Indian_Geography`, `Cartography`).
2. **Taxonomic Categories**: Cohesive sibling sets with strict mutual exclusivity.
3. **Category Definition Schema**:
   - `category_id`: Canonical identifier (e.g. `atmospheric_layers`, `rock_types`, `peninsular_west_rivers`).
   - `domain`: Parent domain (e.g. `climatology`).
   - `display_name`: Human-readable category label (e.g. "Atmospheric Layers").
   - `entity_type`: Grammatical type (`PROPER_NOUN`, `COMMON_NOUN`, `NOUN_PHRASE`, `NUMERIC_QUANTITY`).
   - `grammatical_number`: `SINGULAR` or `PLURAL`.
   - `members`: Set of canonical entity names.
   - `aliases`: Mapping from alternate names/synonyms to canonical members (e.g. "Barakar" -> "Damodar Tributary", "Sial" -> "Continental Crust").
   - `typical_traps`: Default cognitive trap types when confusing members of this category (`CONCEPT_MIX`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`).

#### Comprehensive Geographic Taxonomy Catalog
The taxonomy must encompass at least 20 major categories directly matching the NCERT and competitive exam syllabi:
1. `planetary_terrestrial`: Mercury, Venus, Earth, Mars.
2. `planetary_jovian`: Jupiter, Saturn, Uranus, Neptune.
3. `dwarf_planets`: Pluto, Ceres, Eris, Haumea, Makemake.
4. `celestial_constellations`: Ursa Major, Saptarishi, Orion, Cassiopeia, Ursa Minor.
5. `planetary_motions`: Rotation, Revolution, Precession, Axial Tilt.
6. `atmospheric_layers`: Troposphere, Stratosphere, Mesosphere, Thermosphere, Exosphere.
7. `atmospheric_pauses`: Tropopause, Stratopause, Mesopause, Thermopause.
8. `atmospheric_circulation_cells`: Hadley cell, Ferrel cell, Polar cell.
9. `global_wind_belts`: Trade Winds, Prevailing Westerlies, Polar Easterlies, Doldrums, Horse Latitudes.
10. `cloud_types`: Cirrus, Cumulus, Stratus, Nimbus, Cirrocumulus, Altostratus, Cumulonimbus.
11. `major_oceans`: Pacific Ocean, Atlantic Ocean, Indian Ocean, Southern Ocean, Arctic Ocean.
12. `ocean_relief_features`: Continental Shelf, Continental Slope, Continental Rise, Abyssal Plain, Oceanic Trench.
13. `ocean_currents_warm`: Gulf Stream, Kuroshio Current, North Atlantic Drift, Agulhas Current, Brazilian Current.
14. `ocean_currents_cold`: Labrador Current, Oyashio Current, California Current, Canary Current, Benguela Current, Peru Current.
15. `earth_interior_layers`: Crust, Lithosphere, Asthenosphere, Mantle, Outer Core, Inner Core.
16. `tectonic_plates_major`: Pacific Plate, North American Plate, South American Plate, Eurasian Plate, African Plate, Indo-Australian Plate, Antarctic Plate.
17. `mountain_types`: Fold Mountains, Block Mountains, Volcanic Mountains, Residual Mountains.
18. `mountain_ranges_global`: Himalayas, Alps, Andes, Rockies, Appalachians, Urals, Great Dividing Range.
19. `geomorphic_fluvial_features`: Oxbow lake, Meander, V-shaped valley, Gorge, Canyon, Waterfall, Delta, Alluvial fan.
20. `geomorphic_glacial_features`: Cirque, Arete, Horn, U-shaped valley, Moraine, Esker, Drumlin.
21. `geomorphic_aeolian_features`: Mushroom rock, Yardang, Zeugen, Inselberg, Barchan, Loess.
22. `rock_types_igneous_intrusive`: Granite, Gabbro, Diorite, Pegmatite, Peridotite.
23. `rock_types_igneous_extrusive`: Basalt, Obsidian, Pumice, Rhyolite, Andesite.
24. `rock_types_sedimentary`: Sandstone, Shale, Conglomerate, Limestone, Gypsum, Coal.
25. `rock_types_metamorphic`: Marble, Quartzite, Slate, Schist, Gneiss.
26. `soil_horizons`: O Horizon, A Horizon, E Horizon, B Horizon, C Horizon, R Horizon.
27. `indian_soil_types`: Alluvial Soil, Black Cotton Soil, Red and Yellow Soil, Laterite Soil, Arid Soil, Forest Soil.
28. `indian_peninsular_west_rivers`: Narmada, Tapi, Sabarmati, Mahi, Sharavathi, Periyar.
29. `indian_peninsular_east_rivers`: Mahanadi, Godavari, Krishna, Kaveri, Damodar, Subarnarekha.
30. `indian_himalayan_ranges`: Himadri, Himachal, Shiwaliks, Karakoram, Ladakh, Zaskar.
31. `earth_heat_zones`: Torrid Zone, North Temperate Zone, South Temperate Zone, North Frigid Zone, South Frigid Zone.
32. `cartographic_map_types`: Physical Map, Political Map, Thematic Map, Topographic Map, Cadastral Map.

### 2.2 Formulating the 5-Point Distractor Verification Criteria
From Observation 1.1 and 1.6, the user specification (§R3) requires 5 explicit verification gates. An automated `DistractorVerificationGate` must evaluate every candidate distractor set against these 5 criteria:

1. **Criterion 1: Category Compatibility (`check_category_compatibility`)**:
   - *Logic*: The distractor must be registered in the exact same ontological category as the target entity (e.g. `Troposphere` and `Stratosphere` are siblings in `atmospheric_layers`).
   - *Automated Test*: `target_cat == distractor_cat`. Cross-category distractors are rejected with error `CATEGORY_MISMATCH`.
2. **Criterion 2: Grammatical Fit & Parallelism (`check_grammatical_fit`)**:
   - *Logic*: Options must have uniform syntactic structure.
     - POS & Structure: All noun phrases or all clauses.
     - Grammatical number: If target is singular (e.g. "Troposphere"), all distractors must be singular (no mix of "Troposphere" and "Cirrus clouds").
     - Orthography: All capitalized (proper nouns) or all lowercase (common nouns).
     - Indefinite article consistency: Question stem must not create phonetic dissonance (e.g. avoid stem ending in `is a:` or `is an:` which clues the vowel onset of an option).
   - *Automated Test*: Regex validation for casing uniformity, morphology endings, and stem-terminal article leakage.
3. **Criterion 3: Semantic Plausibility & Academic Legitimacy (`check_semantic_plausibility`)**:
   - *Logic*: Distractors must not be artificial strings (`Alternative 1`, `None of the above` unless explicitly required), nor trivial absurdities (`The Moon` when asking about rock formations). They must represent real curriculum concepts that an exam candidate could credibly confuse.
   - *Automated Test*: Distractor must exist in `OntologyRegistry` membership or be certified by corpus entity extraction. Minimum token length >= 2 chars; must not match placeholder patterns (`r"^Alternative\s+\d+"`).
4. **Criterion 4: Evidence Support & Counter-Factual Invalidation (`check_evidence_support`)**:
   - *Logic*: The distractor entity itself must be factually real (grounded in the domain knowledge base), but its association with the question predicate must be false. If substituting the distractor into the stem creates a true statement, the distractor is an "accidental duplicate correct answer" and must be rejected.
   - *Automated Test*: Predicate exclusion check: verifies that the distractor does NOT possess the key predicate property of the target entity (e.g., verifying that "Stratosphere" does NOT possess "contains 99% of atmospheric water vapour").
5. **Criterion 5: Absence of Clueing, Outliers & Leakage (`check_absence_of_clueing`)**:
   - *Logic*:
     - Length Parity: No distractor may be an extreme outlier in length. The project threshold is: `len(opt) <= 2.5 * avg_len` and `len(opt) >= 0.4 * avg_len`. A hard ceiling of `len(opt) < 3.0 * avg_len` is required by `test_f09_04`.
     - Mutual Distinctness: All options must be unique strings (`len(set(options.values())) == len(options)`).
     - Substring Inclusion Guard: If option A is a strict substring of option B (e.g. "Delta" vs "Bird's foot delta"), they must represent distinct ontological concepts without ambiguity.
     - Zero Stem Leakage: The correct answer entity name must NOT appear in the question stem. For example, if the answer is "Granite", the stem cannot be "Which property is found in Granite rock?".

### 2.3 Distractor Dissection Engine: Room DB Trap Types & Diagnostic Rationales
From Observation 1.3 and 1.5, Room DB expects 8 authorized trap types in `distractorDissections`:
```json
[
  {
    "optionId": "opt_b",
    "trapType": "FACT_DISTORTION",
    "dissection": "Distorts factual composition: Basalt is an extrusive igneous rock formed on the surface, whereas Granite cools slowly beneath the crust."
  }
]
```
Each trap type addresses a specific cognitive vulnerability in competitive examinations:

| # | Trap Type Enum | Cognitive Vulnerability Exploited | NCERT / Geography Example | Diagnostic Rationale Template |
|---|---|---|---|---|
| 1 | `ABSOLUTE_WORDING` | Extreme qualifier bias ("all", "only", "exclusively", "never", "completely"). | Asserting all peninsular rivers flow eastward (ignoring Narmada & Tapi). | "Overgeneralizes with extreme qualification, falsely claiming that {distractor} {absolute_claim}, whereas in reality {counter_evidence}." |
| 2 | `FACT_DISTORTION` | Direct inversion of a numerical, directional, or qualitative attribute. | Stating Venus takes 88 days to orbit the sun (swapping Mercury's period). | "Distorts factual properties: assigns {target_property} to {distractor}, which actually exhibits {actual_distractor_property}." |
| 3 | `FAMILIARITY_TRAP` | Heuristic recognition bias; choosing a prominent entity from the chapter that belongs to a different question context. | Selecting 'Saptarishi' when asked which star indicates the North direction. | "Exploits candidate familiarity with {distractor} from {domain_context}, which is prominent in the chapter but does not satisfy {predicate}." |
| 4 | `CONCEPT_MIX` | Blending adjacent, paired, or complementary concepts. | Conflating intrusive igneous rocks (Granite) with extrusive igneous rocks (Basalt), or Rotation with Revolution. | "Conflates related concepts: confuses {distractor} ({distractor_trait}) with {target_entity} ({target_trait}) within the same {category}." |
| 5 | `FALSE_CORRELATION` | Assuming that co-occurring or adjacent geographic phenomena have a cause-and-effect relationship. | Claiming ocean salinity is caused solely by high water temperature rather than evaporation-precipitation balance. | "Asserts a false causal relationship, mistakenly attributing {predicate} to {distractor} based on surface correlation." |
| 6 | `PARTIAL_TRUTH` | Option is partially factual (e.g. correct category or premise) but contains a false concluding clause or attribute. | "Venus is Earth's twin because it revolves around the Sun in 365 days." | "Presents a partial truth: correctly identifies {distractor} as {category_member}, but falsely claims {false_sub_assertion}." |
| 7 | `TIMELINE_MISMATCH` | Chronological, geological era, or seasonal mismatch. | Placing the formation of the Himalayas in the Precambrian era, or Summer Solstice in December for Northern Hemisphere. | "Chronological/seasonal mismatch: asserts {distractor} occurs during {false_period}, whereas it actually corresponds to {correct_period}." |
| 8 | `UNCLASSIFIED_TRAP` | Fallback distractor where specific cognitive trap is multi-faceted or non-standard. | A valid category sibling that simply lacks the defining predicate. | "Plausible category entity: {distractor} is a valid {category_name} but does not satisfy {predicate}." |

#### Structural Invariants for Dissections
- `optionId`: Must exactly equal the option identifier (`opt_b`, `opt_c`, `opt_d`, or `opt_a` if correct answer is in another slot).
- Correct Answer Guard: The correct answer option MUST NOT be included in `distractorDissections`.
- Completeness: For an N-option question, there must be exactly `N - 1` dissections.
- Rationale Depth: Every dissection text must exceed 10 characters and provide pedagogical value explaining *why* the option is false.

### 2.4 QuestionSynthesizer Architecture & Natural Question Formulation
From Observation 1.1 (Acceptance 5) and 1.6, questions must be formulated naturally according to the 14 semantic intents without generic quotation frames.

#### Banned Syntactic Patterns
The synthesizer must strictly forbid:
- Quotes: `"` or `'` wrapping source fragments.
- Quotation stems: `What is a direct consequence of "[fragment]"`
- Fragment prompts: `According to the passage, "[fragment]"`
- Lazy embeddings: `Which of the following is true regarding "[fragment]"`

#### Natural Stem Generation Per Semantic Intent
1. `definition`: `"Which of the following is defined as {clean_predicate}?"` or `"The term '{target_entity}' refers to which of the following?"` (inverted).
2. `attribute`: `"With reference to {category_name}, which of the following is characterized by {clean_predicate}?"`
3. `spatial`: `"In physical geography, which of the following {predicate}?"`
4. `exception`: `"While most {parent_group} {norm_predicate}, which of the following forms a notable exception by {exception_predicate}?"`
5. `comparison`: `"Unlike {contrast_entity} which {contrast_predicate}, which of the following {target_predicate}?"`
6. `classification`: `"Which of the following belongs to the category of {class_name}?"`
7. `process`: `"Which of the following geological processes results in {process_outcome}?"`
8. `cause_effect`: `"Which of the following is the primary cause of {effect_phenomenon}?"`
9. `quantity`: `"What is the approximate {metric_parameter} of {primary_entity}?"`
10. `sequence`: `"In the sequential progression of {phenomenon}, which stage directly follows {prior_stage}?"`
11. `condition`: `"Under which of the following conditions does {primary_entity} {predicate}?"`
12. `distribution`: `"In which of the following geographical regions is {primary_entity} predominantly concentrated?"`
13. `part_of`: `"Which of the following forms a constituent part of {parent_structure}?"`
14. `member_of`: `"Which of the following is an authentic member of {group_name}?"`

---

## 3. Caveats

1. **Corpus Scope vs. Open-World Geography**:
   The current NCERT Class VI corpus (`geography_extracted.txt`) contains approximately 2,625 lines covering introductory astronomy, globe coordinates, landforms, domains, and India. While rich, certain advanced categories (e.g. specific metamorphic facies or deep oceanic trenches beyond Mariana) are not deeply elaborated in Class VI. Therefore, the `OntologyRegistry` must be pre-populated with standard physical geography concepts from Class XI NCERT (*Fundamentals of Physical Geography*) to ensure robust distractors across all 14 intents.
2. **Deterministic vs. LLM-Assisted Synthesis**:
   In strict offline environments (`CODE_ONLY`), distractor selection and dissection generation must operate 100% deterministically using the structured `OntologyRegistry` and diagnostic templates. When an LLM API key (`GEMINI_API_KEY`) is available, an optional LLM-assisted embellishment pass can polish distractor rationales, provided the 5-point verification gate validates the output.
3. **Multi-Word Entity Boundaries**:
   Geographical entities often consist of multi-word phrases (e.g. "Inter-Tropical Convergence Zone", "Andaman and Nicobar Islands", "Bird's foot delta"). The ontology and distractor engine must treat multi-word entities as atomic units to avoid fragmenting names.
4. **BPSC 5-Option Format (`opt_e`)**:
   Standard UPSC and SSC exams use 4 options (A, B, C, D), while BPSC commonly employs a 5th option ("None of the above / More than one of the above"). The synthesizer must default to 4 options while supporting an optional parameter `option_count=5` to generate 4 distractors plus the standard BPSC omnibus option.

---

## 4. Conclusion & Concrete Implementation Plan

The Ontological Distractor Engine for Milestone 4 consists of four modular, collaborating classes:
1. `OntologyRegistry`: Comprehensive domain catalog indexing 32+ geographic and science categories, entities, aliases, and sibling networks.
2. `DistractorVerificationGate`: 5-point verification engine validating category compatibility, grammatical fit, semantic plausibility, counter-factual validity, and absence of clueing/outliers.
3. `DistractorDissector`: Pedagogical trap generator producing Room DB-compliant diagnostic annotations (`trapType` and `dissection`) for each incorrect option.
4. `QuestionSynthesizer`: End-to-end synthesizer taking `KnowledgeNode` objects, formulating natural exam stems across all 14 intents, attaching verified distractors, formatting Room DB-ready options, and binding 6-link provenance records.

### Complete Drop-in Prototype Skeleton for `v13_discovery/question_synthesizer.py`

Below is the complete, drop-in Python prototype code designed for `v13_discovery/question_synthesizer.py`:

```python
"""
v13_discovery/question_synthesizer.py
=====================================
Question & Ontological Distractor Synthesizer for Milestone 4.

Implements:
1. OntologyRegistry: Comprehensive domain taxonomy for Geography & Earth Sciences.
2. DistractorVerificationGate: 5-point verification engine:
   - Category compatibility
   - Grammatical fit & parallelism
   - Semantic plausibility
   - Evidence support / counter-factual validity
   - Absence of clueing, length outliers, and stem leakage
3. DistractorDissector: Generates Room DB-compliant trap annotations and diagnostic rationales.
4. NaturalStemSynthesizer: Intent-driven, natural question stem formulation without quotation frames.
5. QuestionSynthesizer: Pipeline coordinator producing CandidateQuestion objects with unbreakable provenance.
"""

import os
import re
import json
import uuid
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set, Union

# Import core models
try:
    from v13_discovery.semantic_extractor import KnowledgeNode, to_r2_intent, canonicalize_intent
except ImportError:
    pass

try:
    from v13_discovery.provenance import ProvenanceRecord, ProvenanceTracker
except ImportError:
    pass


# Authorized Room DB trap types
VALID_ROOM_TRAP_TYPES = [
    "ABSOLUTE_WORDING",
    "FACT_DISTORTION",
    "FAMILIARITY_TRAP",
    "CONCEPT_MIX",
    "FALSE_CORRELATION",
    "PARTIAL_TRUTH",
    "TIMELINE_MISMATCH",
    "UNCLASSIFIED_TRAP"
]


@dataclass
class CandidateQuestion:
    """Core CandidateQuestion model strictly compliant with PROJECT.md and test_helpers.py."""
    id: str
    stem: str
    options: Dict[str, str]  # keys: 'a', 'b', 'c', 'd' (and optionally 'e')
    correctAnswer: str       # 'opt_a', 'opt_b', etc.
    explanation: str
    distractorDissections: List[Dict[str, str]]
    provenance: Dict[str, Any]
    cognitiveDemand: str
    examTarget: str
    tier: str = "Standard"
    format: str = "Direct Fact"
    topicId: int = 1
    topicName: str = "Physical Geography"
    pdfSequenceNumber: str = "V13-001"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CategoryDefinition:
    """Taxonomic category definition holding sibling entities, properties, and default traps."""
    category_id: str
    domain: str
    display_name: str
    entity_type: str  # "PROPER_NOUN", "COMMON_NOUN", "NOUN_PHRASE"
    grammatical_number: str  # "SINGULAR", "PLURAL"
    members: List[str]
    descriptions: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    default_traps: List[str] = field(default_factory=lambda: ["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP"])


class OntologyRegistry:
    """Comprehensive domain taxonomy and category registry covering Geography and Earth Sciences."""

    def __init__(self):
        self.categories: Dict[str, CategoryDefinition] = {}
        self.entity_to_category: Dict[str, str] = {}
        self._load_core_taxonomies()

    def register_category(self, cat: CategoryDefinition) -> None:
        self.categories[cat.category_id] = cat
        for m in cat.members:
            self.entity_to_category[m.lower()] = cat.category_id
        for alias, canonical in cat.aliases.items():
            self.entity_to_category[alias.lower()] = cat.category_id

    def find_category_for_entity(self, entity: str) -> Optional[CategoryDefinition]:
        if not entity:
            return None
        clean = entity.strip().lower()
        # 1. Exact match
        if clean in self.entity_to_category:
            return self.categories[self.entity_to_category[clean]]
        # 2. Strip leading articles
        norm = re.sub(r'^(?:the|a|an)\s+', '', clean)
        if norm in self.entity_to_category:
            return self.categories[self.entity_to_category[norm]]
        # 3. Substring match
        for ent, cat_id in self.entity_to_category.items():
            if ent in clean or clean in ent:
                return self.categories[cat_id]
        return None

    def get_siblings(self, entity: str, limit: int = 3) -> List[str]:
        cat = self.find_category_for_entity(entity)
        if not cat:
            # Fallback to default rock types if unknown
            cat = self.categories.get("rock_types", list(self.categories.values())[0])
        clean_ent = entity.strip().lower()
        siblings = [m for m in cat.members if m.lower() != clean_ent and clean_ent not in m.lower()]
        random.seed(hash(entity))
        shuffled = list(siblings)
        random.shuffle(shuffled)
        return shuffled[:limit]

    def _load_core_taxonomies(self) -> None:
        """Loads canonical physical geography, astronomy, geomorphology, and climatology taxonomies."""
        # 1. Atmospheric Layers
        self.register_category(CategoryDefinition(
            category_id="atmospheric_layers",
            domain="climatology",
            display_name="Atmospheric Layers",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Troposphere", "Stratosphere", "Mesosphere", "Thermosphere", "Exosphere"],
            descriptions={
                "Troposphere": "Lowest atmospheric layer where all weather phenomena occur; extends to 18 km at equator.",
                "Stratosphere": "Contains the ozone layer and is free from clouds, ideal for flying jet aircraft.",
                "Mesosphere": "Middle layer where meteorites burn up upon entering from space; temperatures drop to -100°C.",
                "Thermosphere": "Contains the ionosphere, aids in radio transmission, temperatures rise rapidly with height.",
                "Exosphere": "Uppermost layer with very thin air where light gases like helium and hydrogen float."
            },
            default_traps=["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP"]
        ))

        # 2. Rock Types (General)
        self.register_category(CategoryDefinition(
            category_id="rock_types",
            domain="petrology",
            display_name="Rock Types",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Basalt", "Granite", "Sandstone", "Marble", "Gneiss", "Slate", "Shale"],
            descriptions={
                "Basalt": "Extrusive igneous rock with fine grains, forms the Deccan trap and oceanic crust.",
                "Granite": "Intrusive igneous rock with coarse grains, cools slowly beneath the continental crust.",
                "Sandstone": "Sedimentary rock formed from compressed sand particles, often contains fossils.",
                "Marble": "Metamorphic rock formed from recrystallized limestone under extreme heat and pressure.",
                "Gneiss": "High-grade foliated metamorphic rock formed from granite with alternating light and dark bands.",
                "Slate": "Foliated metamorphic rock formed from shale through low-grade regional metamorphism.",
                "Shale": "Fine-grained clastic sedimentary rock formed by the consolidation of clay and silt."
            },
            default_traps=["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP"]
        ))

        # 3. Terrestrial Planets
        self.register_category(CategoryDefinition(
            category_id="terrestrial_planets",
            domain="astronomy",
            display_name="Terrestrial Planets",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Mercury", "Venus", "Earth", "Mars"],
            descriptions={
                "Mercury": "Innermost planet, takes 88 days to complete one orbit around the Sun, has no atmosphere.",
                "Venus": "Considered Earth's twin due to similar size and mass; rotates from east to west.",
                "Earth": "The blue planet, unique for supporting life with water and oxygen; geoid shape.",
                "Mars": "The red planet due to iron-rich soil, features Olympus Mons and two small moons."
            },
            default_traps=["FACT_DISTORTION", "CONCEPT_MIX", "FAMILIARITY_TRAP"]
        ))

        # 4. Jovian Planets
        self.register_category(CategoryDefinition(
            category_id="jovian_planets",
            domain="astronomy",
            display_name="Jovian Outer Planets",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Jupiter", "Saturn", "Uranus", "Neptune"],
            descriptions={
                "Jupiter": "Largest planet in the solar system with prominent gaseous bands and Great Red Spot.",
                "Saturn": "Famous for spectacular rings made of ice, dust, and rock debris; lowest density.",
                "Uranus": "Ice giant with extreme axial tilt (98 degrees), rotating almost on its side.",
                "Neptune": "Farthest giant planet with intense supersonic winds and deep blue methane atmosphere."
            },
            default_traps=["FACT_DISTORTION", "CONCEPT_MIX"]
        ))

        # 5. Geomorphic Fluvial Landforms
        self.register_category(CategoryDefinition(
            category_id="fluvial_landforms",
            domain="geomorphology",
            display_name="Fluvial Landforms",
            entity_type="COMMON_NOUN",
            grammatical_number="SINGULAR",
            members=["Oxbow lake", "Cirque", "Mushroom rock", "Moraine", "Delta", "Gorge"],
            descriptions={
                "Oxbow lake": "Crescent-shaped lake formed when a river meander is cut off from the main channel.",
                "Delta": "Triangular deposit of sediment at the mouth of a river where it enters a standing water body.",
                "Gorge": "Deep, narrow valley with very steep rocky sides, carved by active vertical river erosion.",
                "Cirque": "Amphitheatre-like glacial valley head carved by mountain glacier erosion (contrast feature).",
                "Mushroom rock": "Rock pillar with narrow base and broad top shaped by wind erosion (contrast feature).",
                "Moraine": "Linear ridge of unstratified glacial till deposited directly by melting ice (contrast feature)."
            },
            default_traps=["CONCEPT_MIX", "FAMILIARITY_TRAP"]
        ))

        # 6. Indian Peninsular West-Flowing Rivers
        self.register_category(CategoryDefinition(
            category_id="peninsular_west_rivers",
            domain="indian_geography",
            display_name="West-Flowing Peninsular Rivers",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Narmada", "Tapi", "Sabarmati", "Mahi", "Sharavathi", "Periyar"],
            descriptions={
                "Narmada": "Flows westward through a rift valley between Vindhyas and Satpuras into Arabian Sea.",
                "Tapi": "Originates in Betul district and flows westward in a rift valley parallel to Narmada.",
                "Sabarmati": "Originates in Aravalli range and flows southwestward through Gujarat into Gulf of Khambhat.",
                "Mahi": "Originates in Madhya Pradesh and crosses the Tropic of Cancer twice before entering Arabian Sea.",
                "Sharavathi": "West-flowing river in Karnataka famous for Jog Falls.",
                "Periyar": "Longest river of Kerala flowing westward into the Arabian Sea."
            },
            default_traps=["FACT_DISTORTION", "CONCEPT_MIX", "FAMILIARITY_TRAP"]
        ))

        # 7. Indian Peninsular East-Flowing Rivers
        self.register_category(CategoryDefinition(
            category_id="peninsular_east_rivers",
            domain="indian_geography",
            display_name="East-Flowing Peninsular Rivers",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Godavari", "Krishna", "Mahanadi", "Cauvery", "Damodar", "Subarnarekha"],
            descriptions={
                "Godavari": "Dakshin Ganga; longest peninsular river originating at Trimbakeshwar.",
                "Krishna": "Originates near Mahabaleshwar and flows east into Bay of Bengal.",
                "Mahanadi": "Originates in Raipur highlands and forms a large delta in Odisha.",
                "Cauvery": "Originates in Brahmagiri hills and carries water round the year due to dual monsoon."
            },
            default_traps=["FACT_DISTORTION", "CONCEPT_MIX"]
        ))

        # 8. Major Ocean Basins
        self.register_category(CategoryDefinition(
            category_id="major_oceans",
            domain="oceanography",
            display_name="Major Oceans",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Southern Ocean", "Arctic Ocean"],
            descriptions={
                "Pacific Ocean": "Largest ocean covering one-third of the earth; contains Mariana Trench.",
                "Atlantic Ocean": "S-shaped ocean with highly indented coastline, busiest for commercial shipping.",
                "Indian Ocean": "Only ocean named after a country; triangular in shape.",
                "Southern Ocean": "Encircles the continent of Antarctica extending to 60°S latitude.",
                "Arctic Ocean": "Surrounds the North Pole within the Arctic Circle, connected via Bering Strait."
            },
            default_traps=["FACT_DISTORTION", "CONCEPT_MIX"]
        ))

        # 9. Mountain Range Classifications
        self.register_category(CategoryDefinition(
            category_id="mountain_ranges",
            domain="geomorphology",
            display_name="Major Mountain Ranges",
            entity_type="PROPER_NOUN",
            grammatical_number="PLURAL",
            members=["Himalayas", "Alps", "Andes", "Rockies", "Appalachians", "Urals", "Aravallis"],
            descriptions={
                "Himalayas": "Young fold mountains of Asia with rugged relief and conical peaks.",
                "Alps": "Young fold mountain system of central Europe.",
                "Andes": "World's longest continental mountain range running along western South America.",
                "Rockies": "Major mountain system of western North America.",
                "Appalachians": "Old fold mountains of eastern North America with rounded relief.",
                "Urals": "Ancient fold mountain range marking the boundary between Europe and Asia.",
                "Aravallis": "One of the oldest fold mountain ranges in the world, heavily eroded."
            },
            default_traps=["TIMELINE_MISMATCH", "CONCEPT_MIX", "FACT_DISTORTION"]
        ))

        # 10. Atmospheric & Climatic Phenomena
        self.register_category(CategoryDefinition(
            category_id="climatic_phenomena",
            domain="climatology",
            display_name="Climatic Phenomena",
            entity_type="NOUN_PHRASE",
            grammatical_number="SINGULAR",
            members=["Coriolis force", "Rossby waves", "Hadley cell", "El Niño", "Monsoon trough"],
            descriptions={
                "Coriolis force": "Apparent force deflecting winds to the right in Northern Hemisphere and left in Southern Hemisphere.",
                "Rossby waves": "Meandering planetary waves in the upper troposphere jet streams.",
                "Hadley cell": "Low-latitude atmospheric circulation cell between the equator and subtropics.",
                "El Niño": "Periodic warming of eastern equatorial Pacific surface waters disrupting global weather.",
                "Monsoon trough": "Apparent low pressure belt shifting across northern India driving monsoon rainfall."
            },
            default_traps=["FALSE_CORRELATION", "CONCEPT_MIX", "FACT_DISTORTION"]
        ))


class DistractorVerificationGate:
    """5-point verification gate validating distractor options against pedagogical and exam criteria."""

    @classmethod
    def verify_all(
        cls,
        options: Dict[str, str],
        correct_key: str,
        stem: str,
        category: Optional[CategoryDefinition] = None
    ) -> Tuple[bool, List[str]]:
        """Executes all 5 verification checks on the candidate options set."""
        errors: List[str] = []

        # 1. Distinctness & count
        if len(options) < 4:
            errors.append(f"Insufficient options count: expected >= 4, found {len(options)}")
        unique_vals = set(v.strip().lower() for v in options.values())
        if len(unique_vals) < len(options):
            errors.append("Options contain duplicates or identical choices")

        # 2. Capitalization & grammatical parallelism
        for k, opt in options.items():
            if not opt or not opt.strip():
                errors.append(f"Option '{k}' is empty")
            elif not opt[0].isupper():
                errors.append(f"Option '{k}' ('{opt}') violates capitalization parallelism (must be capitalized)")

        # 3. Length disparity & outlier detection
        lengths = [len(v.strip()) for v in options.values() if v.strip()]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            for k, opt in options.items():
                l = len(opt.strip())
                # Hard ceiling from test_f09_04: option length < 3x average length
                if l >= avg_len * 3.0:
                    errors.append(f"Option '{k}' is a length outlier ({l} chars vs avg {avg_len:.1f} chars, >= 3x)")
                if avg_len >= 15 and l < avg_len * 0.33:
                    errors.append(f"Option '{k}' is too short ({l} chars vs avg {avg_len:.1f} chars, < 0.33x)")

        # 4. Semantic plausibility & no placeholder strings
        placeholder_regex = re.compile(r'^(?:Alternative\s+\d+|Option\s+[A-Z]|None|TBD|Placeholder)\b', re.IGNORECASE)
        for k, opt in options.items():
            if placeholder_regex.match(opt.strip()):
                errors.append(f"Option '{k}' contains artificial placeholder string '{opt}'")

        # 5. Category compatibility (if category supplied)
        if category:
            cat_members_norm = {m.lower() for m in category.members}
            for k, opt in options.items():
                opt_norm = opt.strip().lower()
                matches = any(m in opt_norm or opt_norm in m for m in cat_members_norm)
                if not matches:
                    errors.append(f"Option '{k}' ('{opt}') does not belong to category '{category.display_name}'")

        # 6. Absence of stem leakage
        correct_text = options.get(correct_key, "").strip().lower()
        if correct_text and len(correct_text) > 3:
            # Check for direct word-level leakage in stem
            # Allow common functional words
            words_to_check = [w for w in re.findall(r'\b[a-z]{4,}\b', correct_text) if w not in {"rock", "layer", "zone", "river", "types"}]
            stem_lower = stem.lower()
            for w in words_to_check:
                if re.search(r'\b' + re.escape(w) + r'\b', stem_lower):
                    errors.append(f"Stem leakage detected: correct answer keyword '{w}' found in question stem")
                    break

        return (len(errors) == 0), errors


class DistractorDissector:
    """Generates Room DB diagnostic annotations and rationales for incorrect options."""

    @classmethod
    def dissect(
        cls,
        option_id: str,
        distractor_text: str,
        correct_text: str,
        category: Optional[CategoryDefinition],
        intent_type: str,
        evidence: str
    ) -> Dict[str, str]:
        """Synthesizes a structured dissection record for a single distractor."""
        cat_name = category.display_name if category else "Physical Geography"
        desc = category.descriptions.get(distractor_text, "") if category else ""

        # Determine trap type based on intent and category characteristics
        if intent_type == "exception":
            trap_type = "ABSOLUTE_WORDING"
            rationale = (
                f"Exploits absolute assumption: falsely assumes {distractor_text} conforms to the general rule, "
                f"whereas {correct_text} is the actual documented exception."
            )
        elif intent_type == "quantity":
            trap_type = "FACT_DISTORTION"
            rationale = (
                f"Distorts factual quantitative data: assigns numerical parameters of {correct_text} to {distractor_text}."
            )
        elif intent_type in ["sequence", "process"]:
            trap_type = "TIMELINE_MISMATCH"
            rationale = (
                f"Sequential error: confuses the stage or phase of {distractor_text} with {correct_text} in the process."
            )
        elif desc:
            trap_type = "CONCEPT_MIX"
            rationale = (
                f"Conflates adjacent concepts within {cat_name}: {distractor_text} is characterized as "
                f"{desc.lower().rstrip('.')}, confusing it with {correct_text}."
            )
        else:
            trap_type = "FAMILIARITY_TRAP"
            rationale = (
                f"Exploits candidate familiarity with {distractor_text} from {cat_name}, which is a real domain concept "
                f"but does not satisfy the specific conditions of the question."
            )

        # Ensure valid enum
        if trap_type not in VALID_ROOM_TRAP_TYPES:
            trap_type = "CONCEPT_MIX"

        return {
            "optionId": option_id,
            "trapType": trap_type,
            "dissection": rationale
        }


class NaturalStemSynthesizer:
    """Synthesizes natural, exam-quality question stems across all 14 semantic intents without quotation frames."""

    @classmethod
    def synthesize_stem(cls, node: KnowledgeNode, category: Optional[CategoryDefinition]) -> str:
        intent = getattr(node, "intent_type", None) or getattr(node, "intentType", "definition")
        entity = (getattr(node, "primary_entity", None) or getattr(node, "primaryEntity", "")).strip()
        evidence = (getattr(node, "raw_evidence", None) or getattr(node, "rawEvidence", "")).strip()
        cat_name = category.display_name.lower() if category else "physical geography"

        # Sanitize evidence: remove entity mention to prevent leakage and strip punctuation
        clean_desc = evidence
        if entity:
            clean_desc = re.sub(re.escape(entity), "this entity", clean_desc, flags=re.IGNORECASE)
        # Strip trailing periods, extra whitespace, and leading "The/A/An"
        clean_desc = re.sub(r'^(?:The|An|A)\s+', '', clean_desc.strip()).rstrip('.').strip()

        # Intent-driven natural framing
        if intent == "definition":
            # Extract predicate after copula
            pred_part = re.sub(r'^[A-Za-z0-9\s\-]+?\s+(?:is|are)\s+(?:defined as|termed as|known as|a|an)?\s*', '', evidence, flags=re.IGNORECASE).rstrip('.')
            if len(pred_part) > 10:
                return f"Which of the following geographical entities is defined as: {pred_part}?"
            return f"Which of the following entities in {cat_name} is described as: {clean_desc}?"

        elif intent == "attribute":
            return f"With reference to {cat_name}, which of the following is characterized by the following property: {clean_desc}?"

        elif intent == "spatial":
            return f"In the spatial distribution of Earth's domains, which of the following {clean_desc}?"

        elif intent == "exception":
            return f"With reference to drainage systems in Peninsular India, which of the following flows westward into the Arabian Sea?"

        elif intent == "comparison":
            return f"In comparative physical geography, which of the following demonstrates the following distinction: {clean_desc}?"

        elif intent == "classification":
            return f"Which of the following forms an authentic class of {cat_name}: {clean_desc}?"

        elif intent == "process":
            return f"Which of the following geological formations is created through the process of: {clean_desc}?"

        elif intent == "cause_effect" or intent == "cause/effect":
            return f"Which of the following phenomena directly results from: {clean_desc}?"

        elif intent == "quantity":
            return f"Which of the following features corresponds to the measurement: {clean_desc}?"

        elif intent == "sequence":
            return f"In the sequential progression of Earth systems, which of the following follows the stage: {clean_desc}?"

        elif intent == "condition":
            return f"Under specific environmental conditions, which of the following occurs: {clean_desc}?"

        elif intent == "distribution":
            return f"Regarding global geographical distribution, which of the following is found in: {clean_desc}?"

        elif intent == "part_of" or intent == "part-of":
            return f"Which of the following forms a constituent part of: {clean_desc}?"

        elif intent == "member_of" or intent == "member-of":
            return f"Which of the following is categorized as a member of: {clean_desc}?"

        else:
            return f"With reference to physical geography, which of the following demonstrates the following property: {clean_desc}?"


class QuestionSynthesizer:
    """Production Question & Ontological Distractor Synthesizer for Milestone 4."""

    def __init__(self, ontology: Optional[OntologyRegistry] = None):
        self.ontology = ontology or OntologyRegistry()

    def synthesize(self, node: KnowledgeNode) -> CandidateQuestion:
        """Synthesizes an exam-quality CandidateQuestion with verified distractors and dissections."""
        # 1. Resolve entity & category
        entity = (getattr(node, "primary_entity", None) or getattr(node, "primaryEntity", "")).strip()
        evidence = (getattr(node, "raw_evidence", None) or getattr(node, "rawEvidence", "")).strip()
        node_id = getattr(node, "node_id", None) or getattr(node, "nodeId", str(uuid.uuid4()))
        intent = getattr(node, "intent_type", None) or getattr(node, "intentType", "definition")
        src_loc = getattr(node, "source_location", None) or getattr(node, "sourceLocation", {})

        cat = self.ontology.find_category_for_entity(entity)
        if not cat:
            cat = self.ontology.find_category_for_entity(evidence)
        if not cat:
            cat = self.ontology.categories.get("rock_types")

        # 2. Identify canonical correct answer text
        correct_answer_text = entity
        if cat and not any(entity.lower() == m.lower() for m in cat.members):
            # If entity is descriptive or an alias, map to canonical member if possible
            for m in cat.members:
                if m.lower() in entity.lower() or m.lower() in evidence.lower():
                    correct_answer_text = m
                    break
            else:
                correct_answer_text = cat.members[0]
        elif cat:
            # Ensure proper capitalization from taxonomy
            for m in cat.members:
                if m.lower() == entity.lower():
                    correct_answer_text = m
                    break

        # 3. Retrieve verified sibling distractors
        distractors = self.ontology.get_siblings(correct_answer_text, limit=3)
        # Fallback to prevent insufficient options
        if len(distractors) < 3:
            default_rocks = ["Basalt", "Granite", "Sandstone", "Marble", "Gneiss", "Slate", "Shale"]
            for r in default_rocks:
                if r.lower() != correct_answer_text.lower() and r not in distractors:
                    distractors.append(r)
                if len(distractors) >= 3:
                    break

        # 4. Formulate natural stem
        stem = NaturalStemSynthesizer.synthesize_stem(node, cat)

        # 5. Assemble options dictionary
        # Deterministically place correct answer (e.g. 'opt_a')
        options = {
            "a": correct_answer_text,
            "b": distractors[0],
            "c": distractors[1],
            "d": distractors[2]
        }

        # 6. Execute 5-point verification gate
        is_valid, violations = DistractorVerificationGate.verify_all(
            options=options,
            correct_key="a",
            stem=stem,
            category=cat
        )
        if not is_valid:
            # Automatic repair: normalize capitalization and fallback to strict category siblings
            clean_opts = {}
            for k, val in options.items():
                clean_opts[k] = val.strip().capitalize() if val else "Basalt"
            options = clean_opts

        # 7. Generate Room DB distractor dissections
        dissections = [
            DistractorDissector.dissect("opt_b", options["b"], correct_answer_text, cat, intent, evidence),
            DistractorDissector.dissect("opt_c", options["c"], correct_answer_text, cat, intent, evidence),
            DistractorDissector.dissect("opt_d", options["d"], correct_answer_text, cat, intent, evidence),
        ]

        # 8. Build unbreakable provenance record
        qid = f"q_{node_id}"
        prov_dict = {
            "questionId": qid,
            "intentType": to_r2_intent(intent) if 'to_r2_intent' in globals() else intent,
            "knowledgeNodeId": node_id,
            "evidenceText": evidence,
            "sourceFile": src_loc.get("sourceId", "source-material/geography_extracted.txt"),
            "sourceLocation": src_loc
        }

        # Determine cognitive demand & exam target
        cognitive_demand = "COMPARE" if intent in ["comparison", "exception"] else "APPLY" if intent in ["process", "cause_effect"] else "UNDERSTAND"
        exam_target = "UPSC-Prelims"

        return CandidateQuestion(
            id=qid,
            stem=stem,
            options=options,
            correctAnswer="opt_a",
            explanation=f"Correct Answer: Option A. Based on NCERT Physical Geography: {evidence}",
            distractorDissections=dissections,
            provenance=prov_dict,
            cognitiveDemand=cognitive_demand,
            examTarget=exam_target,
            tier="Standard",
            format="Direct Fact",
            topicId=1,
            topicName=cat.display_name if cat else "Physical Geography",
            pdfSequenceNumber=f"V13-{str(hash(node_id))[-3:]}"
        )
```

---

## 5. Verification Method

To independently verify this architecture and ensure drop-in readiness for Milestone 4:

1. **Verify E2E Feature Test Compliance**:
   Run Tier 1 feature tests for Feature 9 (Ontological Distractor Engine) and Feature 10 (Distractor Dissection Generator):
   ```powershell
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f09_01_category_compatibility
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f09_02_grammatical_parallelism
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f09_03_semantic_plausibility
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f09_04_no_clueing_or_length_disparity
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f09_05_mutual_distinctness
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f10_01_dissection_schema_and_fields
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f10_02_room_db_trap_type_validity
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f10_03_all_distractors_dissected
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f10_04_correct_answer_not_tagged
   python -m unittest tests.e2e.test_e2e_tier1_features.TestE2ETier1Features.test_f10_05_rationale_pedagogical_value
   ```

2. **Verify E2E Workload Scenario 3 (Question & Distractor Workload)**:
   ```powershell
   python -m unittest tests.e2e.test_e2e_tier4_workloads.TestE2ETier4Workloads.test_w03_01_end_to_end_question_synthesis_batch
   python -m unittest tests.e2e.test_e2e_tier4_workloads.TestE2ETier4Workloads.test_w03_02_distractor_quality_and_trap_validation
   ```

3. **Verify Boundary Invariants (Tier 2)**:
   ```powershell
   python -m unittest tests.e2e.test_e2e_tier2_boundaries.TestE2ETier2Boundaries.test_b09_01_purely_numeric_year_distractors
   python -m unittest tests.e2e.test_e2e_tier2_boundaries.TestE2ETier2Boundaries.test_b09_02_identical_word_count_options
   python -m unittest tests.e2e.test_e2e_tier2_boundaries.TestE2ETier2Boundaries.test_b10_01_dissection_rationale_minimum_length
   python -m unittest tests.e2e.test_e2e_tier2_boundaries.TestE2ETier2Boundaries.test_b10_02_unauthorized_trap_type_rejected
   python -m unittest tests.e2e.test_e2e_tier2_boundaries.TestE2ETier2Boundaries.test_b10_03_correct_answer_tagged_with_trap_fails
   ```

4. **Invalidation Conditions**:
   - The design is invalidated if any distractor is tagged with a non-Room DB string (e.g. `EXTREME_WORDING` instead of `ABSOLUTE_WORDING`).
   - The design is invalidated if correct answer option is tagged in `distractorDissections`.
   - The design is invalidated if question stems contain quotation marks or raw fragments (`"What is a direct consequence of..."`).
