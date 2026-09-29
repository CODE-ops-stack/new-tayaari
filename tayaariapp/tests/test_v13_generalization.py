#!/usr/bin/env python3
"""
tests/test_v13_generalization.py
================================
Empirical Generalization & Anti-Overfitting Test Suite for V13 Semantic Extractor.
Milestone 2 Iteration 3 Specification.

Objective:
Pair golden evaluation items with unseen educational sentences across all 14 semantic intents.
Ensure that:
1. All 14 intents categorize both golden and unseen sentences without intent collapse.
2. The empirical counter-examples (Experiments A, B, C) flagged by the Forensic Auditor pass cleanly.
3. No domain vocabulary is hardcoded in PATTERNS or extraction logic.
"""

import json
import os
import re
import sys
import unittest
from typing import Dict, Any, List, Optional

cur = os.path.abspath(os.path.dirname(__file__))
while cur and not os.path.exists(os.path.join(cur, "v13_discovery")):
    parent = os.path.dirname(cur)
    if parent == cur:
        break
    cur = parent
REPO_ROOT = cur
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    KnowledgeNode,
    canonicalize_intent
)

class TestV13EmpiricalGeneralization(unittest.TestCase):
    """Verifies that the extractor categorizes expository sentences via structural grammar,
    not domain vocabulary overfitting."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def _assert_extraction(
        self,
        sentence: str,
        expected_intent: str,
        expected_entity_substr: str,
        validate_fn: Optional[Any] = None
    ) -> KnowledgeNode:
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Failed to extract any KnowledgeNode from: '{sentence}'"
        )
        node = nodes[0]
        actual_intent = canonicalize_intent(node.intent_type)
        norm_expected = canonicalize_intent(expected_intent)

        self.assertEqual(
            actual_intent, norm_expected,
            f"Intent collapse detected for: '{sentence}'\n"
            f"Expected: '{norm_expected}', Got: '{actual_intent}'"
        )
        self.assertIn(
            expected_entity_substr.lower(),
            node.primary_entity.lower(),
            f"Primary entity mismatch for: '{sentence}'\n"
            f"Expected substring '{expected_entity_substr}' in '{node.primary_entity}'"
        )
        self.assertTrue(
            bool(node.predicate and node.predicate.strip()),
            f"Predicate was empty for: '{sentence}'"
        )
        if validate_fn:
            validate_fn(node)
        return node

    # =========================================================================
    # PART 1: FORENSIC AUDITOR COUNTER-EXAMPLES (EXPERIMENTS A, B, C)
    # =========================================================================

    def test_experiment_a_attribute_generalization(self):
        """Exp A: Attribute intent must categorize unseen kinematic vibration sentences
        identically to golden wave sentences without collapsing to definition."""
        # Golden Sentence (POS-006)
        s_gold = (
            "Primary waves (P-waves) are longitudinal compressional waves "
            "that vibrate parallel to the direction of wave propagation."
        )
        # Unseen Sentence (Identical syntactic frame, new domain vocabulary)
        s_unseen = (
            "Primary waves (P-waves) are fast mechanical vibrations "
            "that travel through rock."
        )

        n_gold = self._assert_extraction(s_gold, "attribute", "Primary waves")
        n_unseen = self._assert_extraction(s_unseen, "attribute", "Primary waves")

        self.assertIn("vibrat", (n_gold.predicate + " " + n_gold.raw_evidence).lower())
        self.assertIn("vibration", (n_unseen.predicate + " " + n_unseen.raw_evidence).lower())

    def test_experiment_b_superlative_attribute_generalization(self):
        """Exp B: Superlative property attributes ('has the highest/lowest [property]')
        must extract cleanly for unseen properties and not return None."""
        # Golden Sentence (POS-007)
        s_gold = (
            "Saturn has the lowest mean density among all planets in the Solar System "
            "at 0.69 grams per cubic centimeter, making it less dense than water."
        )
        # Unseen Sentence (Substituted attribute 'highest equatorial bulge')
        s_unseen = (
            "Saturn has the highest equatorial bulge among all planets in the Solar System "
            "at 0.69 grams per cubic centimeter, making it less dense than water."
        )

        n_gold = self._assert_extraction(s_gold, "attribute", "Saturn")
        n_unseen = self._assert_extraction(s_unseen, "attribute", "Saturn")

        self.assertTrue(
            any(w in n_gold.predicate.lower() for w in ["density", "planets", "solar system"]),
            f"Predicate missed attribute content: {n_gold.predicate}"
        )
        self.assertTrue(
            any(w in n_unseen.predicate.lower() for w in ["equatorial bulge", "bulge", "planets"]),
            f"Predicate missed attribute content: {n_unseen.predicate}"
        )

    def test_experiment_c_member_of_generalization(self):
        """Exp C: Member-of classification must not rely on hardcoded 'yellow dwarf'.
        Unseen taxonomic stellar class ('main-sequence star') must extract as member-of."""
        # Golden Sentence (POS-054)
        s_gold = (
            "The Sun is an ordinary yellow dwarf star located in the Orion Cygnus Arm."
        )
        # Unseen Sentence (Stellar classification 'main-sequence star')
        s_unseen = (
            "The Sun is an ordinary main-sequence star located in the Milky Way."
        )

        n_gold = self._assert_extraction(s_gold, "member_of", "Sun")
        n_unseen = self._assert_extraction(s_unseen, "member_of", "Sun")

        self.assertTrue(
            any(w in n_gold.predicate.lower() for w in ["star", "yellow dwarf", "orion"]),
            f"Golden predicate missed taxonomy: {n_gold.predicate}"
        )
        self.assertTrue(
            any(w in n_unseen.predicate.lower() for w in ["star", "main-sequence", "milky way"]),
            f"Unseen predicate missed taxonomy: {n_unseen.predicate}"
        )

    # =========================================================================
    # PART 2: 14-INTENT PAIRED GENERALIZATION BENCHMARK
    # =========================================================================

    def test_gen_01_definition(self):
        """Intent 1: definition — Golden celestial definition vs Unseen biochemical/hydrological definitions."""
        s_gold = "The sun, the moon and all those objects shining in the night sky are called celestial bodies."
        s_unseen_1 = "Photosynthesis is defined as the biochemical process whereby green plants synthesize carbohydrates from carbon dioxide and water."
        s_unseen_2 = "An aquifer refers to an underground layer of water-bearing permeable rock, rock fractures, or unconsolidated materials."

        self._assert_extraction(s_gold, "definition", "celestial bodies")
        self._assert_extraction(s_unseen_1, "definition", "Photosynthesis")
        self._assert_extraction(s_unseen_2, "definition", "aquifer")

    def test_gen_02_attribute(self):
        """Intent 2: attribute — Golden wave & density attributes vs Unseen shear wave & gravity attributes."""
        s_gold = "The tropical rainforest ecosystem is characterized by extreme biodiversity, multi-layered forest canopies, and continuous year-round vegetative growth."
        s_unseen_1 = "Secondary waves (S-waves) are transverse shear vibrations that displace rock particles perpendicular to the direction of wave travel."
        s_unseen_2 = "Jupiter has the greatest gravitational acceleration among all planets in the Solar System at 24.79 meters per second squared."

        self._assert_extraction(s_gold, "attribute", "tropical rainforest")
        self._assert_extraction(s_unseen_1, "attribute", "Secondary waves")
        self._assert_extraction(s_unseen_2, "attribute", "Jupiter")

    def test_gen_03_cause_effect(self):
        """Intent 3: cause_effect — Golden subduction & insolation vs Unseen acid rain & hurricane surge."""
        s_gold = "The subduction of oceanic tectonic plates beneath continental margins causes deep-focus earthquakes and explosive volcanic arc activity due to intense crustal convergence."
        s_unseen_1 = "Sulfur dioxide emissions from industrial combustion cause acid precipitation by reacting with atmospheric moisture."
        s_unseen_2 = "Severe coastal erosion is triggered by storm surges during intense tropical hurricanes."

        self._assert_extraction(s_gold, "cause_effect", "subduction")
        self._assert_extraction(s_unseen_1, "cause_effect", "Sulfur dioxide emissions")
        self._assert_extraction(s_unseen_2, "cause_effect", "coastal erosion")

    def test_gen_04_comparison(self):
        """Intent 4: comparison — Golden seismic media & latitude/longitude vs Unseen petrology & circulatory systems."""
        s_gold_1 = "Primary seismic waves are compressional waves that propagate through solids, liquids, and gases, whereas secondary seismic waves are shear waves that can travel exclusively through solid materials."
        s_gold_2 = "Parallels of latitude decrease in circumference progressively from the Equator toward the poles, whereas all meridians of longitude maintain identical lengths from pole to pole."
        s_unseen_1 = "Granite is much coarser-grained than basalt due to slow subterranean magma cooling."
        s_unseen_2 = "Arteries carry oxygenated blood away from the heart at high hydrostatic pressure, whereas veins transport deoxygenated blood back to the heart under low pressure."

        self._assert_extraction(s_gold_1, "comparison", "Primary seismic waves")
        self._assert_extraction(s_gold_2, "comparison", "Parallels of latitude")
        self._assert_extraction(s_unseen_1, "comparison", "Granite")
        self._assert_extraction(s_unseen_2, "comparison", "Arteries")

    def test_gen_05_spatial(self):
        """Intent 5: spatial — Golden Narmada rift valley vs Unseen Mariana Trench & Konkan coastal plain."""
        s_gold = "The Narmada River flows westward through a linear tectonic rift valley situated between the Vindhya Range to the north and the Satpura Range to the south."
        s_unseen_1 = "The Mariana Trench is located in the western Pacific Ocean, extending over 2,500 kilometres along a convergent plate boundary."
        s_unseen_2 = "Between the Western Ghats and the Arabian Sea lies the Konkan coastal plain."

        self._assert_extraction(s_gold, "spatial", "Narmada River")
        self._assert_extraction(s_unseen_1, "spatial", "Mariana Trench")
        self._assert_extraction(s_unseen_2, "spatial", "Konkan coastal plain")

    def test_gen_06_distribution(self):
        """Intent 6: distribution — Golden water & mineral concentration vs Unseen petroleum & mangrove distributions."""
        s_gold = "More than 97 percent of the Earth's total water reserves are distributed in oceanic saltwater basins, while less than 3 percent constitutes freshwater, of which the majority is locked in polar ice sheets and glaciers."
        s_unseen_1 = "Extensive reserves of petroleum are concentrated in the sedimentary basins of the Persian Gulf region."
        s_unseen_2 = "Mangrove forests are distributed across tropical and subtropical intertidal estuaries and deltaic shorelines."

        self._assert_extraction(s_gold, "distribution", "Earth's total water reserves")
        self._assert_extraction(s_unseen_1, "distribution", "petroleum")
        self._assert_extraction(s_unseen_2, "distribution", "Mangrove forests")

    def test_gen_07_classification(self):
        """Intent 7: classification — Golden rock & planet classifications vs Unseen cloud & plate boundary classifications."""
        s_gold_1 = "Geologists classify rocks into three fundamental genetic categories based on mode of origin: igneous rocks, sedimentary rocks, and metamorphic rocks."
        s_gold_2 = "Plate tectonics classifies lithospheric plate margins into three major boundaries: divergent boundaries where plates pull apart, convergent boundaries where plates collide, and transform boundaries where plates slide past one another horizontally."
        s_unseen_1 = "Meteorologists classify clouds into three altitude families: high clouds, middle clouds, and low clouds."
        s_unseen_2 = "Plate boundaries can be divided into divergent boundaries, convergent boundaries, and transform fault margins."

        self._assert_extraction(s_gold_1, "classification", "rocks")
        self._assert_extraction(s_gold_2, "classification", "lithospheric plate margins")
        self._assert_extraction(s_unseen_1, "classification", "clouds")
        self._assert_extraction(s_unseen_2, "classification", "Plate boundaries")

    def test_gen_08_quantity(self):
        """Intent 8: quantity — Golden solar mass & moon distance vs Unseen trench depth & speed of light."""
        s_gold = "The mean orbital distance between the center of the Earth and the center of the Moon is approximately 384,400 kilometres."
        s_unseen_1 = "The Mariana Trench extends to a depth of approximately 10,994 meters below sea level at the Challenger Deep."
        s_unseen_2 = "Electromagnetic radiation in a vacuum travels at approximately 299,792 kilometres per second."

        self._assert_extraction(s_gold, "quantity", "orbital distance")
        self._assert_extraction(s_unseen_1, "quantity", "Mariana Trench")
        self._assert_extraction(s_unseen_2, "quantity", "Electromagnetic radiation")

    def test_gen_09_sequence(self):
        """Intent 9: sequence — Golden solar genesis & seismic arrival vs Unseen hydrological cycle & cell mitosis."""
        s_gold = "The genesis of the Solar System commenced approximately 4.8 billion years ago with the gravitational collapse of a giant molecular cloud, followed by the formation of a rotating accretion disk, core ignition of the protosun, and subsequent accretion of planetesimals into planets."
        s_unseen_1 = "The hydrological cycle progresses through a continuous sequence: solar evaporation from ocean surfaces, atmospheric condensation into clouds, terrestrial precipitation, and surface runoff back to oceans."
        s_unseen_2 = "During cell division, mitosis progresses through four chronological stages: prophase, metaphase, anaphase, and telophase."

        self._assert_extraction(s_gold, "sequence", "genesis of the Solar System")
        self._assert_extraction(s_unseen_1, "sequence", "hydrological cycle")
        self._assert_extraction(s_unseen_2, "sequence", "mitosis")

    def test_gen_10_condition(self):
        """Intent 10: condition — Golden eclipse & cyclogenesis conditions vs Unseen dew point & glacial deformation."""
        s_gold = "A solar eclipse occurs exclusively during the new moon phase when the Moon passes directly along the line of syzygy between the Sun and the Earth, projecting its umbral shadow onto Earth's surface."
        s_unseen_1 = "Atmospheric dew forms only when the ground surface temperature falls below the dew point temperature on calm, clear nights."
        s_unseen_2 = "Glacial flow can occur only if the accumulated ice thickness exceeds 30 meters, generating sufficient internal plastic deformation."

        self._assert_extraction(s_gold, "condition", "solar eclipse")
        self._assert_extraction(s_unseen_1, "condition", "Atmospheric dew")
        self._assert_extraction(s_unseen_2, "condition", "Glacial flow")

    def test_gen_11_exception(self):
        """Intent 11: exception — Golden planetary retrograde & moonless planets vs Unseen mammalian monotremes & liquid metals."""
        s_gold = "While nearly all planets in the Solar System rotate counter-clockwise from west to east on their axes, Venus and Uranus are unique exceptions that rotate clockwise in retrograde motion from east to west."
        s_unseen_1 = "Except for the platypus and echidna, all living mammals give birth to live young rather than laying eggs."
        s_unseen_2 = "Mercury is the only metallic element that remains liquid at standard ambient room temperature and pressure."

        self._assert_extraction(s_gold, "exception", "Venus and Uranus")
        self._assert_extraction(s_unseen_1, "exception", "mammals")
        self._assert_extraction(s_unseen_2, "exception", "Mercury")

    def test_gen_12_process(self):
        """Intent 12: process — Golden seafloor spreading & convectional rain vs Unseen cellular respiration & metamorphism."""
        s_gold = "Seafloor spreading is the geodynamic process whereby upwelling mantle magma rises along divergent mid-ocean ridge axes, solidifies into new oceanic basaltic crust, and drives older lithosphere outward on either side."
        s_unseen_1 = "Cellular respiration converts biochemical energy from glucose nutrients into adenosine triphosphate (ATP) molecules and metabolic waste."
        s_unseen_2 = "Regional metamorphism is the thermodynamic process whereby intense heat and confining pressure recrystallize shale rocks into foliated schists."

        self._assert_extraction(s_gold, "process", "Seafloor spreading")
        self._assert_extraction(s_unseen_1, "process", "Cellular respiration")
        self._assert_extraction(s_unseen_2, "process", "Regional metamorphism")

    def test_gen_13_part_of(self):
        """Intent 13: part_of — Golden corona & Earth interior shells vs Unseen inner core & cell mitochondria."""
        s_gold_1 = "The solar corona constitutes the outermost atmospheric envelope of the Sun, extending millions of kilometres into space and visible to the naked eye during total solar eclipses."
        s_gold_2 = "The Earth's internal structure is composed of three concentric geosphere shells: the outer silicate crust, the middle dense peridotite mantle, and the central nickel-iron metallic core."
        s_unseen_1 = "The inner core constitutes the innermost solid metallic sphere of the Earth, consisting primarily of an iron-nickel alloy."
        s_unseen_2 = "Mitochondria form an essential organelle component located within the cytoplasm of eukaryotic cells."

        self._assert_extraction(s_gold_1, "part_of", "solar corona")
        self._assert_extraction(s_gold_2, "part_of", "internal structure")
        self._assert_extraction(s_unseen_1, "part_of", "inner core")
        self._assert_extraction(s_unseen_2, "part_of", "Mitochondria")

    def test_gen_14_member_of(self):
        """Intent 14: member_of — Golden Ursa Major & Aravalli vs Unseen Betelgeuse & Indian rhinoceros."""
        s_gold_1 = "Ursa Major (commonly known as the Big Bear or Great Bear) is a prominent member of the 88 internationally recognised astronomical constellations."
        s_gold_2 = "The Aravalli Range in northwestern India is a remnant member of the ancient Precambrian fold mountain systems of the world."
        s_unseen_1 = "Betelgeuse is a prominent red supergiant star located in the constellation of Orion."
        s_unseen_2 = "The Indian rhinoceros is a vulnerable member of the greater one-horned rhinoceros family indigenous to the Brahmaputra valley."

        self._assert_extraction(s_gold_1, "member_of", "Ursa Major")
        self._assert_extraction(s_gold_2, "member_of", "Aravalli Range")
        self._assert_extraction(s_unseen_1, "member_of", "Betelgeuse")
        self._assert_extraction(s_unseen_2, "member_of", "Indian rhinoceros")

    # =========================================================================
    # PART 3: ZERO DOMAIN OVERFITTING AUDIT
    # =========================================================================

    def test_zero_domain_vocabulary_in_patterns(self):
        """Anti-Cheating Integrity Audit: Verifies that PATTERNS contains zero literal golden set strings."""
        source_path = os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        banned_domain_strings = [
            "longitudinal compressional",
            "lowest mean density",
            "very big and hot",
            "comprises immense reserves",
            "yellow dwarf",
            "satellite container port",
            "nearly all planets in",
            "denudational process in which",
            "tectonic process of",
            "plunges beneath",
            "transported and deposited by",
            "Geologists|Scientists|Geographers|Plate tectonics"
        ]

        found_violations = []
        for banned in banned_domain_strings:
            if banned.lower() in content.lower():
                found_violations.append(banned)

        self.assertEqual(
            len(found_violations), 0,
            f"INTEGRITY VIOLATION DETECTED: Hardcoded domain strings found in semantic_extractor.py:\n"
            f"{found_violations}\n"
            f"Extraction patterns must be structurally generalized and free of dataset-specific tokens."
        )


if __name__ == "__main__":
    unittest.main()
