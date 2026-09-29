#!/usr/bin/env python3
"""
tests/test_v13_adversarial_challenge.py
========================================
Empirical Adversarial Challenge Test Suite for Milestone 2:
- Semantic Extractor (LinguisticSemanticExtractor / SemanticExtractor)
- NoiseFilterGate
- Document Normalizer

Authored by teamwork_preview_challenger_m2_1_rep.
Evaluates:
1. Syntactic inversions, passive voice, and multi-prepositional clauses.
2. Complex Indian geographic entities (hyphenated, multi-word, capitalized).
3. NoiseFilterGate bypasses (borderline MCQs, subtle watermarks).
4. NoiseFilterGate false rejections of valid factual knowledge.
"""

import unittest
from v13_discovery.semantic_extractor import SemanticExtractor, NoiseFilterGate, LinguisticSemanticExtractor


class TestAdversarialSemanticExtractor(unittest.TestCase):
    """Stress tests on LinguisticSemanticExtractor & SemanticExtractor."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_challenge_01_dispatch_multi_prepositional_intro(self):
        """Dispatched test sentence: Multi-prepositional introductory clause."""
        text = "In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Extractor completely dropped multi-prepositional sentence: '{text}'"
        )
        node = nodes[0]
        self.assertIn("cause", node.intent_type.lower())
        self.assertNotIn("In the northern plains", node.primary_entity)
        self.assertIn("heavy rainfall", node.primary_entity.lower())

    def test_challenge_02_locative_inversion_trailing_period(self):
        """Locative inversion ending in a period should extract entity and predicate."""
        text = "Under the continental crust lies the upper mantle."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Extractor failed on single-clause locative inversion with period: '{text}'"
        )
        node = nodes[0]
        self.assertIn("mantle", node.primary_entity.lower())
        self.assertIn("lies under", node.predicate.lower())

    def test_challenge_03_passive_definition_slot_orientation(self):
        """Passive definition should slot defined term as primary_entity, not predicate target."""
        text = "The Western Ghats are known as Sahyadri in Maharashtra."
        nodes = self.extractor.extract(text)
        self.assertGreaterEqual(len(nodes), 1, f"Failed to extract node from: '{text}'")
        node = nodes[0]
        # Primary entity should be the subject Western Ghats, not 'Sahyadri in Maharashtra'
        self.assertIn(
            "western ghats", node.primary_entity.lower(),
            f"Subject inverted: primary_entity was slotted as '{node.primary_entity}'"
        )

    def test_challenge_04_corrupted_prefix_stripping(self):
        """Ensure determiners/articles regex does not strip characters from words like 'Along'."""
        text = "Along the Malabar Coast, during the southwest monsoon, heavy precipitation occurs regularly."
        nodes = self.extractor.extract(text)
        if nodes:
            node = nodes[0]
            self.assertFalse(
                node.primary_entity.startswith("long the"),
                f"Entity corrupted by leading 'A' strip: '{node.primary_entity}'"
            )

    def test_challenge_05_complex_indian_geographic_entities(self):
        """Test extraction across complex Indian geographic entities."""
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
        self.assertEqual(len(failures), 0, f"Entity extraction failures: {failures}")


class TestAdversarialNoiseFilterGate(unittest.TestCase):
    """Stress tests on NoiseFilterGate discrimination & false rejections."""

    def test_challenge_06_mcq_leakage_roman_and_brackets(self):
        """Borderline MCQ markers like (i) or [A] must be rejected by NoiseFilterGate."""
        leaks = [
            "(i) The Deccan Traps are formed by volcanic activity.",
            "[A] Barren Island is India only active volcano.",
            "1) The Western Ghats cause orographic rainfall.",
        ]
        bypasses = []
        for text in leaks:
            rejection = NoiseFilterGate.audit(text)
            if rejection is None:
                bypasses.append(text)
        self.assertEqual(len(bypasses), 0, f"MCQ noise bypassed NoiseFilterGate: {bypasses}")

    def test_challenge_07_subtle_watermark_bypasses(self):
        """Figure captions without colon or subtle watermarks must not bypass gate."""
        watermarks = [
            "Figure 3.2 Diagram of the Solar System",
        ]
        bypasses = []
        for wm in watermarks:
            rejection = NoiseFilterGate.audit(wm)
            if rejection is None:
                bypasses.append(wm)
        self.assertEqual(len(bypasses), 0, f"Watermarks bypassed NoiseFilterGate: {bypasses}")

    def test_challenge_08_false_rejection_demonstratives(self):
        """Valid educational facts starting with 'These' or 'Those' must NOT be falsely rejected."""
        facts = [
            "These landforms are primarily shaped by glacial erosion across high altitudes.",
            "These rivers originate in the glaciers of the Trans-Himalayan region.",
            "Those plateaus situated north of the Tropic of Cancer experience extreme temperature variations.",
            "Those rocks formed by cooling magma are categorized as igneous rocks.",
        ]
        false_rejections = []
        for fact in facts:
            rejection = NoiseFilterGate.audit(fact)
            if rejection is not None:
                false_rejections.append((fact, rejection))
        self.assertEqual(
            len(false_rejections), 0,
            f"True facts falsely rejected as noise: {false_rejections}"
        )

    def test_challenge_09_false_rejection_short_facts(self):
        """Concise 4-word educational definitions must NOT be rejected as fragments."""
        facts = [
            "Basalt is volcanic rock.",
            "Lignite is brown coal.",
            "Marble is metamorphic limestone.",
            "Quartz is silicon dioxide.",
            "Hematite is iron ore.",
        ]
        false_rejections = []
        for fact in facts:
            rejection = NoiseFilterGate.audit(fact)
            if rejection is not None:
                false_rejections.append((fact, rejection))
        self.assertEqual(
            len(false_rejections), 0,
            f"Concise true facts falsely rejected as noise: {false_rejections}"
        )


if __name__ == "__main__":
    unittest.main()
