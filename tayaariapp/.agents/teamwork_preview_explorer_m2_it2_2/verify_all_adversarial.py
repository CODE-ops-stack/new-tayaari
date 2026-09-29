"""
Verification script running all tests from:
- test_v13_adversarial_m2_challenge.py (20 tests)
- test_v13_adversarial_challenge.py (9 tests)
against the proposed extractor and noise gate.
"""

import unittest
import os
import sys

REPO_ROOT = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from prototype_extractor import (
    ProposedSemanticExtractor,
    ProposedNoiseFilterGate,
    ProposedLinguisticSemanticExtractor,
)
from v13_discovery.semantic_extractor import canonicalize_intent


class VerifyAdversarialM2Challenge(unittest.TestCase):
    def setUp(self):
        self.extractor = ProposedSemanticExtractor()
        self.gate = ProposedNoiseFilterGate

    # 1. Entity Integrity
    def test_entity_prefix_truncation_atmosphere(self):
        sentence = "Atmosphere is divided into five layers."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.lower() == "tmosphere")
        self.assertIn("atmosphere", nodes[0].primary_entity.lower())

    def test_entity_prefix_truncation_antarctica(self):
        sentence = "Antarctica is covered by permanent ice sheets."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.lower() == "tarctica")
        self.assertIn("antarctica", nodes[0].primary_entity.lower())

    def test_entity_prefix_truncation_andesite(self):
        sentence = "Andesite is an extrusive volcanic rock with intermediate composition."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.lower() == "desite")
        self.assertIn("andesite", nodes[0].primary_entity.lower())

    def test_entity_prefix_truncation_thermosphere(self):
        sentence = "Thermosphere is the layer of the atmosphere above the mesosphere."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.lower() == "rmosphere")
        self.assertIn("thermosphere", nodes[0].primary_entity.lower())

    def test_entity_prefix_truncation_alluvial(self):
        sentence = "Alluvial soils are deposited by the Himalayan river systems."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.lower().startswith("lluvial"))
        self.assertIn("alluvial", nodes[0].primary_entity.lower())

    def test_corrupt_entity_from_prepositional_clause_form_of(self):
        sentence = "Precipitation falls to the ground in the form of rain or snow."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertNotIn("in the", nodes[0].primary_entity.lower())
        self.assertIn("precipitation", nodes[0].primary_entity.lower())

    def test_corrupt_entity_auxiliary_verb_are_followed(self):
        sentence = "Primary seismic waves are followed by secondary waves."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0)
        self.assertFalse(nodes[0].primary_entity.strip().endswith(" are"))
        self.assertIn("primary seismic waves", nodes[0].primary_entity.lower())

    # 2. Syntactic Inversions
    def test_multi_introductory_prepositional_phrases(self):
        sentence = "In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "cause_effect")
        self.assertIn("rainfall", node.primary_entity.lower())

    def test_locative_inversion_with_terminal_period(self):
        sentence = "Under the Trans-Himalayan range lies the Indus-Tsangpo Suture Zone."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "spatial")
        self.assertIn("indus-tsangpo", node.primary_entity.lower())

    def test_introductory_exception_clause(self):
        s1 = "Except for Mercury and Venus, all planets in the solar system have natural satellites."
        nodes1 = self.extractor.extract(s1)
        self.assertGreaterEqual(len(nodes1), 1)
        self.assertEqual(canonicalize_intent(nodes1[0].intent_type), "exception")

        s2 = "With the exception of Venus and Uranus, all planets rotate from west to east."
        nodes2 = self.extractor.extract(s2)
        self.assertGreaterEqual(len(nodes2), 1)
        self.assertEqual(canonicalize_intent(nodes2[0].intent_type), "exception")

    def test_passive_voice_cause_effect_not_definition(self):
        sentence = "Extensive riverine flooding is caused by heavy monsoon rainfall."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "cause_effect")

    # 3. Intent Collapse
    def test_comparative_adjectives_do_not_collapse_to_definition(self):
        sentences = [
            ("Continental crust is thicker than oceanic crust.", "comparison"),
            ("Mercury is smaller than Earth.", "comparison"),
            ("The density of continental crust is lower than that of oceanic crust.", "comparison")
        ]
        for s, expected in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed for '{s}'")
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), expected)

    def test_singular_classification_does_not_collapse_to_definition(self):
        sentences = [
            "The crust is divided into oceanic and continental crust.",
            "Earth atmosphere is divided into troposphere, stratosphere, mesosphere, thermosphere, and exosphere."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed for '{s}'")
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), "classification")

    def test_scientific_process_verbs_extract_successfully(self):
        sentences = [
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
            "Condensation transforms water vapor into liquid water droplets.",
            "Evaporation turns liquid water into water vapor."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed for '{s}'")
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), "process")

    def test_standard_quantity_facts_extract_successfully(self):
        sentences = [
            "The Earth has an equatorial radius of 6378 kilometers.",
            "The core extends to a depth of 2900 kilometers.",
            "Mount Everest has an elevation of 8848 meters."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed for '{s}'")
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), "quantity")

    # 4. NoiseGate Bypasses
    def test_bracketed_and_numbered_mcq_options_rejected(self):
        leaks = [
            "[A] Troposphere is the lowest atmospheric layer extending up to 18 km.",
            "(1) Alluvial soil is formed by the deposition of silt.",
            "(i) Oceanic crust is composed of basalt and gabbro."
        ]
        for item in leaks:
            self.assertIsNotNone(self.gate.audit(item))

    def test_bypassed_mcq_does_not_leak_into_knowledge_node(self):
        nodes = self.extractor.extract("[A] Troposphere is the lowest atmospheric layer extending up to 18 km.")
        if nodes:
            self.assertNotIn("[A]", nodes[0].primary_entity)

    def test_truncated_dangling_fragments_rejected(self):
        fragments = [
            "The peninsular plateau is drained by several major rivers including",
            "The Himalayan mountain range contains numerous high peaks such as",
            "The oceanic crust is much younger than continental crust since",
            "The Great Northern Plains are situated in the depression between"
        ]
        for frag in fragments:
            self.assertIsNotNone(self.gate.audit(frag))

    # 5. False Rejections
    def test_concise_educational_facts_not_rejected(self):
        concise_facts = [
            "Lava is molten rock.",
            "Earth orbits the Sun.",
            "Ozone absorbs ultraviolet radiation.",
            "Bauxite is aluminium ore."
        ]
        for fact in concise_facts:
            self.assertIsNone(self.gate.audit(fact), f"Falsely rejected: {fact}")

    def test_valid_phrasal_prepositions_not_rejected(self):
        valid_facts = [
            "Granite is the intrusive igneous rock that continents are made of.",
            "Solar wind is the stream of charged particles that the Earth's magnetic field protects us from."
        ]
        for fact in valid_facts:
            self.assertIsNone(self.gate.audit(fact), f"Falsely rejected: {fact}")


class VerifyAdversarialChallenge9(unittest.TestCase):
    def setUp(self):
        self.extractor = ProposedSemanticExtractor()
        self.gate = ProposedNoiseFilterGate

    def test_challenge_01_dispatch_multi_prepositional_intro(self):
        text = "In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertIn("cause", node.intent_type.lower())
        self.assertNotIn("In the northern plains", node.primary_entity)
        self.assertIn("heavy rainfall", node.primary_entity.lower())

    def test_challenge_02_locative_inversion_trailing_period(self):
        text = "Under the continental crust lies the upper mantle."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertIn("mantle", node.primary_entity.lower())
        self.assertIn("lies under", node.predicate.lower())

    def test_challenge_03_passive_definition_slot_orientation(self):
        text = "The Western Ghats are known as Sahyadri in Maharashtra."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertIn("western ghats", node.primary_entity.lower())

    def test_challenge_04_corrupted_prefix_stripping(self):
        text = "Along the Malabar Coast, during the southwest monsoon, heavy precipitation occurs regularly."
        nodes = self.extractor.extract(text)
        if nodes:
            node = nodes[0]
            self.assertFalse(node.primary_entity.startswith("long the"))

    def test_challenge_05_complex_indian_geographic_entities(self):
        samples = [
            ("The Indo-Gangetic plain constitutes the most fertile agricultural region of Northern India.", "Indo-Gangetic"),
            ("The Trans-Himalayan zone contains the Karakoram, Ladakh, and Zaskar ranges.", "Trans-Himalayan"),
            ("The Great Rann of Kutch is a vast salt marsh situated in the Thar Desert.", "Great Rann of Kutch"),
            ("The Chota Nagpur Plateau comprises rich deposits of iron ore, coal, and bauxite.", "Chota Nagpur Plateau"),
            ("The Andaman and Nicobar Islands are separated by the Ten Degree Channel.", "Andaman and Nicobar Islands"),
            ("The Deccan Traps were formed through massive basaltic fissure eruptions.", "Deccan Traps"),
        ]
        failures = []
        for text, entity in samples:
            nodes = self.extractor.extract(text)
            if not nodes:
                failures.append(f"Dropped: {entity} ('{text}')")
            elif entity.lower() not in nodes[0].primary_entity.lower():
                failures.append(f"Entity mismatch: expected '{entity}', got '{nodes[0].primary_entity}'")
        self.assertEqual(len(failures), 0, f"Failures: {failures}")

    def test_challenge_06_mcq_leakage_roman_and_brackets(self):
        leaks = [
            "(i) The Deccan Traps are formed by volcanic activity.",
            "[A] Barren Island is India only active volcano.",
            "1) The Western Ghats cause orographic rainfall.",
        ]
        for text in leaks:
            self.assertIsNotNone(self.gate.audit(text))

    def test_challenge_07_subtle_watermark_bypasses(self):
        watermarks = ["Figure 3.2 Diagram of the Solar System"]
        for wm in watermarks:
            self.assertIsNotNone(self.gate.audit(wm))

    def test_challenge_08_false_rejection_demonstratives(self):
        facts = [
            "These landforms are primarily shaped by glacial erosion across high altitudes.",
            "These rivers originate in the glaciers of the Trans-Himalayan region.",
            "Those plateaus situated north of the Tropic of Cancer experience extreme temperature variations.",
            "Those rocks formed by cooling magma are categorized as igneous rocks.",
        ]
        for fact in facts:
            self.assertIsNone(self.gate.audit(fact), f"False rejection: {fact}")

    def test_challenge_09_false_rejection_short_facts(self):
        facts = [
            "Basalt is volcanic rock.",
            "Lignite is brown coal.",
            "Marble is metamorphic limestone.",
            "Quartz is silicon dioxide.",
            "Hematite is iron ore.",
        ]
        for fact in facts:
            self.assertIsNone(self.gate.audit(fact), f"False rejection: {fact}")


if __name__ == "__main__":
    unittest.main()
