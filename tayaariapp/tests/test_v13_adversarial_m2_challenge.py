#!/usr/bin/env python3
"""
tests/test_v13_adversarial_m2_challenge.py
==========================================
Adversarial Stress Test Suite for Milestone 2:
- v13_discovery/semantic_extractor.py
- v13_discovery/normalizer.py

Author: teamwork_preview_challenger_m2_1
Role: EMPIRICAL CHALLENGER (critic, specialist)

Tests empirical vulnerabilities:
1. Entity integrity and truncation bugs (eating prefixes 'A', 'An', 'The')
2. Syntactic inversions, multi-prepositional clauses, passive voice, and terminal punctuation
3. Semantic intent collapse (comparisons, processes, singular classifications falling back to definition)
4. NoiseFilterGate bypasses (bracketed MCQ leaks, Roman numeral leaks, truncated fragments)
5. NoiseFilterGate false rejections (concise facts < 5 words, phrasal prepositions, impersonal pronouns)
"""

import os
import sys
import unittest
from typing import List, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    NoiseFilterGate,
    KnowledgeNode,
    canonicalize_intent
)
from v13_discovery.normalizer import WatermarkOcrCleaner, DocumentNormalizer


class TestAdversarialEntityIntegrity(unittest.TestCase):
    """Verifies whether entity names are preserved without truncation or corruption."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_entity_prefix_truncation_atmosphere(self):
        """Discovers bug where 'Atmosphere' is truncated to 'tmosphere'."""
        sentence = "Atmosphere is divided into five layers."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        # Adversarial check: verify if the entity is corrupted to 'tmosphere'
        is_corrupted = (node.primary_entity.lower() == "tmosphere")
        self.assertFalse(
            is_corrupted,
            f"VULNERABILITY CONFIRMED: 'Atmosphere' was corrupted to '{node.primary_entity}' due to un-bounded prefix stripping"
        )

    def test_entity_prefix_truncation_antarctica(self):
        """Discovers bug where 'Antarctica' is truncated to 'tarctica'."""
        sentence = "Antarctica is covered by permanent ice sheets."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        is_corrupted = (node.primary_entity.lower() == "tarctica")
        self.assertFalse(
            is_corrupted,
            f"VULNERABILITY CONFIRMED: 'Antarctica' was corrupted to '{node.primary_entity}' due to 'An' prefix stripping"
        )

    def test_entity_prefix_truncation_andesite(self):
        """Discovers bug where 'Andesite' is truncated to 'desite'."""
        sentence = "Andesite is an extrusive volcanic rock with intermediate composition."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        is_corrupted = (node.primary_entity.lower() == "desite")
        self.assertFalse(
            is_corrupted,
            f"VULNERABILITY CONFIRMED: 'Andesite' was corrupted to '{node.primary_entity}' due to 'An' prefix stripping"
        )

    def test_entity_prefix_truncation_thermosphere(self):
        """Discovers bug where 'Thermosphere' is truncated to 'rmosphere'."""
        sentence = "Thermosphere is the layer of the atmosphere above the mesosphere."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        is_corrupted = (node.primary_entity.lower() == "rmosphere")
        self.assertFalse(
            is_corrupted,
            f"VULNERABILITY CONFIRMED: 'Thermosphere' was corrupted to '{node.primary_entity}' due to 'The' prefix stripping"
        )

    def test_entity_prefix_truncation_alluvial(self):
        """Discovers bug where 'Alluvial soils' is truncated to 'lluvial soils'."""
        sentence = "Alluvial soils are deposited by the Himalayan river systems."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        is_corrupted = (node.primary_entity.lower().startswith("lluvial"))
        self.assertFalse(
            is_corrupted,
            f"VULNERABILITY CONFIRMED: 'Alluvial soils' was corrupted to '{node.primary_entity}'"
        )

    def test_corrupt_entity_from_prepositional_clause_form_of(self):
        """Discovers bug where 'in the form of' causes 'Precipitation falls to the ground in the' to become primary entity."""
        sentence = "Precipitation falls to the ground in the form of rain or snow."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        self.assertNotIn(
            "in the",
            node.primary_entity.lower(),
            f"VULNERABILITY CONFIRMED: Prepositional fragment swallowed into entity: '{node.primary_entity}'"
        )

    def test_corrupt_entity_auxiliary_verb_are_followed(self):
        """Discovers bug where 'Primary seismic waves are' becomes primary entity because 'followed by' matched."""
        sentence = "Primary seismic waves are followed by secondary waves."
        nodes = self.extractor.extract(sentence)
        self.assertTrue(len(nodes) > 0, "Failed to extract any node")
        node = nodes[0]
        self.assertFalse(
            node.primary_entity.strip().endswith(" are"),
            f"VULNERABILITY CONFIRMED: Auxiliary verb swallowed into entity: '{node.primary_entity}'"
        )


class TestAdversarialSyntacticInversions(unittest.TestCase):
    """Verifies handling of complex syntactic structures, multiple prepositional phrases, and inversions."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_multi_introductory_prepositional_phrases(self):
        """Tests the exact dispatch sentence with chained introductory prepositional phrases."""
        sentence = "In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            "VULNERABILITY CONFIRMED: Extractor completely dropped sentence with multiple introductory prepositional phrases"
        )
        node = nodes[0]
        self.assertEqual(
            canonicalize_intent(node.intent_type), "cause_effect",
            f"Expected cause_effect intent, got {node.intent_type}"
        )
        self.assertIn("rainfall", node.primary_entity.lower(), f"Unexpected primary entity: {node.primary_entity}")

    def test_locative_inversion_with_terminal_period(self):
        """Tests locative inversion with Indian geographic entity ending in standard sentence period."""
        sentence = "Under the Trans-Himalayan range lies the Indus-Tsangpo Suture Zone."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            "VULNERABILITY CONFIRMED: Locative inversion failed to extract because terminal period was unhandled in LOCATIVE_INV_REGEX"
        )
        node = nodes[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "spatial")
        self.assertIn("indus-tsangpo", node.primary_entity.lower())

    def test_introductory_exception_clause(self):
        """Tests exception intent when introduced by 'Except for' or 'With the exception of'."""
        s1 = "Except for Mercury and Venus, all planets in the solar system have natural satellites."
        nodes1 = self.extractor.extract(s1)
        self.assertGreaterEqual(
            len(nodes1), 1,
            "VULNERABILITY CONFIRMED: 'Except for...' introductory clause failed to extract"
        )
        self.assertEqual(canonicalize_intent(nodes1[0].intent_type), "exception")

        s2 = "With the exception of Venus and Uranus, all planets rotate from west to east."
        nodes2 = self.extractor.extract(s2)
        self.assertGreaterEqual(
            len(nodes2), 1,
            "VULNERABILITY CONFIRMED: 'With the exception of...' failed to extract"
        )
        self.assertEqual(canonicalize_intent(nodes2[0].intent_type), "exception")

    def test_passive_voice_cause_effect_not_definition(self):
        """Tests that passive cause/effect ('is caused by') is not misclassified as definition."""
        sentence = "Extensive riverine flooding is caused by heavy monsoon rainfall."
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(
            canonicalize_intent(node.intent_type), "cause_effect",
            f"VULNERABILITY CONFIRMED: Passive cause/effect misclassified as '{node.intent_type}'"
        )


class TestAdversarialIntentCollapse(unittest.TestCase):
    """Verifies that the 14 intents do not collapse into definition or None on standard educational sentences."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_comparative_adjectives_do_not_collapse_to_definition(self):
        """Tests that standard comparisons ('is thicker than', 'is smaller than') are classified as comparison."""
        sentences = [
            ("Continental crust is thicker than oceanic crust.", "comparison"),
            ("Mercury is smaller than Earth.", "comparison"),
            ("The density of continental crust is lower than that of oceanic crust.", "comparison")
        ]
        for s, expected_intent in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract node for '{s}'")
            actual_intent = canonicalize_intent(nodes[0].intent_type)
            self.assertEqual(
                actual_intent, expected_intent,
                f"VULNERABILITY CONFIRMED: '{s}' collapsed to '{actual_intent}' instead of '{expected_intent}'"
            )

    def test_singular_classification_does_not_collapse_to_definition(self):
        """Tests that singular classifications ('is divided into', 'is classified into') are classified as classification."""
        sentences = [
            "The crust is divided into oceanic and continental crust.",
            "Earth atmosphere is divided into troposphere, stratosphere, mesosphere, thermosphere, and exosphere."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract node for '{s}'")
            actual_intent = canonicalize_intent(nodes[0].intent_type)
            self.assertEqual(
                actual_intent, "classification",
                f"VULNERABILITY CONFIRMED: Singular classification collapsed to '{actual_intent}'"
            )

    def test_scientific_process_verbs_extract_successfully(self):
        """Tests that fundamental science process verbs ('converts', 'transforms', 'turns') extract as process."""
        sentences = [
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
            "Condensation transforms water vapor into liquid water droplets.",
            "Evaporation turns liquid water into water vapor."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"VULNERABILITY CONFIRMED: Process sentence '{s}' completely dropped (returned None/empty)"
            )
            actual_intent = canonicalize_intent(nodes[0].intent_type)
            self.assertEqual(actual_intent, "process", f"Expected process, got {actual_intent}")

    def test_standard_quantity_facts_extract_successfully(self):
        """Tests that standard geographical quantities ('has an equatorial radius of', 'extends to a depth of') extract."""
        sentences = [
            "The Earth has an equatorial radius of 6378 kilometers.",
            "The core extends to a depth of 2900 kilometers.",
            "Mount Everest has an elevation of 8848 meters."
        ]
        for s in sentences:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"VULNERABILITY CONFIRMED: Quantity sentence '{s}' completely dropped"
            )
            actual_intent = canonicalize_intent(nodes[0].intent_type)
            self.assertEqual(actual_intent, "quantity")


class TestAdversarialNoiseGateBypasses(unittest.TestCase):
    """Verifies that NoiseFilterGate rejects borderline MCQ options and truncated fragments."""

    def test_bracketed_and_numbered_mcq_options_rejected(self):
        """Tests that bracketed [A] and numbered (1), (i) MCQ options are rejected by NoiseFilterGate."""
        leaks = [
            "[A] Troposphere is the lowest atmospheric layer extending up to 18 km.",
            "(1) Alluvial soil is formed by the deposition of silt.",
            "(i) Oceanic crust is composed of basalt and gabbro."
        ]
        for item in leaks:
            verdict = NoiseFilterGate.audit(item)
            self.assertIsNotNone(
                verdict,
                f"VULNERABILITY CONFIRMED: NoiseFilterGate bypassed by MCQ option: '{item}'"
            )

    def test_bypassed_mcq_does_not_leak_into_knowledge_node(self):
        """Tests that MCQ markers are not incorporated into KnowledgeNode primaryEntity."""
        extractor = SemanticExtractor()
        nodes = extractor.extract("[A] Troposphere is the lowest atmospheric layer extending up to 18 km.")
        if nodes:
            self.assertNotIn(
                "[A]", nodes[0].primary_entity,
                f"VULNERABILITY CONFIRMED: MCQ option marker leaked into entity: '{nodes[0].primary_entity}'"
            )

    def test_truncated_dangling_fragments_rejected(self):
        """Tests that truncated sentences ending in prepositions/conjunctions are rejected."""
        fragments = [
            "The peninsular plateau is drained by several major rivers including",
            "The Himalayan mountain range contains numerous high peaks such as",
            "The oceanic crust is much younger than continental crust since",
            "The Great Northern Plains are situated in the depression between"
        ]
        for frag in fragments:
            verdict = NoiseFilterGate.audit(frag)
            self.assertIsNotNone(
                verdict,
                f"VULNERABILITY CONFIRMED: Dangling fragment bypassed NoiseFilterGate: '{frag}'"
            )


class TestAdversarialFalseRejections(unittest.TestCase):
    """Verifies that legitimate concise facts and phrasal prepositions are NOT rejected by NoiseFilterGate."""

    def test_concise_educational_facts_not_rejected(self):
        """Tests that valid short facts (< 5 words) are not falsely rejected as syntactic_fragment."""
        concise_facts = [
            "Lava is molten rock.",
            "Earth orbits the Sun.",
            "Ozone absorbs ultraviolet radiation.",
            "Bauxite is aluminium ore."
        ]
        for fact in concise_facts:
            verdict = NoiseFilterGate.audit(fact)
            self.assertIsNone(
                verdict,
                f"VULNERABILITY CONFIRMED: Legitimate fact falsely rejected as '{verdict}': '{fact}'"
            )

    def test_valid_phrasal_prepositions_not_rejected(self):
        """Tests that valid facts ending in legitimate phrasal prepositions ('made of', 'protects from') are not rejected."""
        valid_facts = [
            "Granite is the intrusive igneous rock that continents are made of.",
            "Solar wind is the stream of charged particles that the Earth's magnetic field protects us from."
        ]
        for fact in valid_facts:
            verdict = NoiseFilterGate.audit(fact)
            self.assertIsNone(
                verdict,
                f"VULNERABILITY CONFIRMED: Valid fact ending in phrasal preposition falsely rejected as '{verdict}': '{fact}'"
            )


if __name__ == "__main__":
    unittest.main()
