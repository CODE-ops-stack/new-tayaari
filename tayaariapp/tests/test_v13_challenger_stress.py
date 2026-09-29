#!/usr/bin/env python3
"""
tests/test_v13_challenger_stress.py
===================================
Empirical Challenger Stress Harness for Milestone 2 Iteration 3.
Agent: teamwork_preview_challenger_m2_it3_1

Empirically challenges the V13 semantic extractor on:
1. Re-running Auditor Experiments A, B, C with novel unseen sentences.
2. Stress testing across all 14 intents (complex syntax, parentheticals, passive voice, comparative trailing clauses, numbers with commas).
3. Ungrounded pronouns and anaphora shielding.
4. Anti-overfitting / zero hardcoded golden strings audit.
"""

import os
import sys
import unittest
from typing import List, Optional, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    NoiseFilterGate,
    DiscourseContext,
    KnowledgeNode,
    canonicalize_intent,
)
from v13_discovery.normalizer import DocumentNormalizer, NormalizedBlock


class TestChallengerAuditorExperiments(unittest.TestCase):
    """Re-run Auditor Experiments A, B, and C with completely novel unseen sentences."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_exp_a_novel_kinematic_wave_attributes(self):
        """Exp A: Kinematic wave/oscillation attribute sentences with novel vocabulary."""
        novel_sentences = [
            ("Rayleigh waves are elliptical surface waves that propagate along the boundary of elastic solids.", "Rayleigh waves"),
            ("Love waves are polarized transverse vibrations that displace particles horizontally during earthquakes.", "Love waves"),
            ("Gamma rays are high-frequency electromagnetic radiations that penetrate deeply into matter.", "Gamma rays"),
            ("Seismic surface waves are dispersive mechanical oscillations that diminish exponentially with depth.", "Seismic surface waves"),
            ("Thermal plumes are buoyant convective currents that rise through the Earth's mantle.", "Thermal plumes"),
        ]
        for sent, expected_entity in novel_sentences:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract from: {sent}")
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type),
                "attribute",
                f"Collapsed to wrong intent for: {sent}. Got: {node.intent_type}"
            )
            self.assertIn(expected_entity.lower(), node.primary_entity.lower())

    def test_exp_b_present_tense_superlative_attributes(self):
        """Exp B: Present-tense superlative properties across multiple domains."""
        novel_sentences = [
            ("Mount Everest has the highest topographical elevation among all terrestrial mountains at 8,848 meters.", "Mount Everest"),
            ("The Dead Sea possesses the lowest continental elevation on Earth at 430 meters below sea level.", "Dead Sea"),
            ("Venus exhibits the highest mean surface temperature among all planets in the Solar System at 465 degrees Celsius.", "Venus"),
            ("The Mariana Trench has the greatest oceanic depth on Earth at nearly 11 kilometres.", "Mariana Trench"),
            ("Mercury displays the smallest orbital radius among all major planets in the Solar System.", "Mercury"),
        ]
        for sent, expected_entity in novel_sentences:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract from: {sent}")
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type),
                "attribute",
                f"Collapsed to wrong intent for: {sent}. Got: {node.intent_type}"
            )
            self.assertIn(expected_entity.lower(), node.primary_entity.lower())

    def test_exp_b_past_tense_superlatives(self):
        """Exp B Remediated: Past-tense superlative assertions ('had', 'exhibited', 'possessed')
        extract valid attribute KnowledgeNodes."""
        past_tense_sentences = [
            ("The Chelyabinsk meteor had the strongest recorded atmospheric shockwave among recent bolides.", "Chelyabinsk meteor"),
            ("The prehistoric Megalodon had the largest bite force among all known apex predators.", "prehistoric Megalodon"),
            ("Ancient Mars possessed a thicker atmospheric envelope during the Noachian epoch.", "Ancient Mars"),
        ]
        for sent, expected_ent in past_tense_sentences:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1, f"Expected node for: {sent}")
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), "attribute")
            self.assertIn(expected_ent.lower(), nodes[0].primary_entity.lower())

    def test_exp_c_whitelisted_member_of(self):
        """Exp C: Member-of classifications where noun is in the 17-word whitelist."""
        whitelisted_sentences = [
            ("Kilauea is an active basaltic shield volcano located in the Hawaiian Islands.", "Kilauea"),
            ("Sirius is a bright binary star located in the constellation of Canis Major.", "Sirius"),
            ("Ceres is a rocky dwarf planet orbiting in the asteroid belt between Mars and Jupiter.", "Ceres"),
            ("The Caspian Sea is an endorheic inland sea situated between Europe and Asia.", "Caspian Sea"),
        ]
        for sent, expected_entity in whitelisted_sentences:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract from: {sent}")
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type),
                "member_of",
                f"Collapsed to wrong intent for: {sent}. Got: {node.intent_type}"
            )
            self.assertIn(expected_entity.lower(), node.primary_entity.lower())

    def test_exp_c_non_whitelisted_member_of(self):
        """Exp C Remediated: Member-of statements with standard educational nouns outside the old 17-word
        whitelist (e.g. moon, forest, mammal, desert, observatory) correctly extract as member_of."""
        non_whitelisted = [
            ("Titan is a massive icy moon orbiting Saturn within the outer Solar System.", "Titan"),
            ("The Sundarbans is an expansive tidal halophytic mangrove forest situated in the delta of the Ganga and Brahmaputra rivers.", "Sundarbans"),
            ("The cheetah is a carnivorous feline mammal found in sub-Saharan Africa.", "cheetah"),
            ("The Sahara is an expansive subtropical desert located in northern Africa.", "Sahara"),
            ("The Hubble Space Telescope is an optical space observatory orbiting the Earth.", "Hubble Space Telescope"),
        ]
        for sent, expected_ent in non_whitelisted:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1)
            self.assertEqual(
                canonicalize_intent(nodes[0].intent_type),
                "member_of",
                f"Failed to extract as member_of for: {sent}"
            )
            self.assertIn(expected_ent.lower(), nodes[0].primary_entity.lower())


class TestChallenger14IntentsStress(unittest.TestCase):
    """Stress tests across all 14 intents evaluating robustness and surfacing syntax traps."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_01_definition_passive_inversion(self):
        """Definition: Passive definitions invert cleanly to concise term and descriptive predicate."""
        s = "The process by which plants convert light energy into chemical energy is called photosynthesis."
        node = self.extractor.extract(s)[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "definition")
        self.assertEqual(node.primary_entity, "photosynthesis")
        self.assertIn("process by which plants convert light energy", node.predicate)

    def test_02_attribute_participle_clause(self):
        """Attribute: Sentences with compound adjectives followed by participle clauses extract as attribute."""
        s = "Stars in open clusters are extremely young and hot, emitting intense ultraviolet radiation into interstellar gas."
        nodes = self.extractor.extract(s)
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "attribute")
        self.assertIn("stars in open clusters", nodes[0].primary_entity.lower())

    def test_03_cause_effect_complex_clauses(self):
        s1 = "Anthropogenic emissions of greenhouse gases drive rapid global thermodynamic warming of tropospheric layers."
        s2 = "Tsunamis are triggered by underwater dip-slip earthquakes displacing large oceanic water columns along convergent subduction trenches."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "cause_effect")
        self.assertIn("anthropogenic emissions", n1.primary_entity.lower())

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "cause_effect")
        self.assertIn("tsunamis", n2.primary_entity.lower())

    def test_04_comparison_comma_qualifier(self):
        r"""Comparison: Comparative clauses followed by comma qualifiers extract as comparison."""
        s = "Continental crust is much thicker than oceanic crust, averaging 35 kilometres compared to 7 kilometres beneath oceans."
        nodes = self.extractor.extract(s)
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "comparison")
        self.assertIn("oceanic crust", nodes[0].secondary_entities)

    def test_05_spatial_locative_inversion(self):
        s1 = "Beneath the outer lithosphere lies the asthenosphere, a ductile layer facilitating tectonic motion."
        s2 = "The Great Rift Valley extends up to 6,000 kilometres from northern Syria to central Mozambique."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "spatial")
        self.assertIn("asthenosphere", n1.primary_entity.lower())

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "spatial")
        self.assertIn("great rift valley", n2.primary_entity.lower())

    def test_06_distribution_percentages(self):
        s1 = "Over 80 percent of global seismic energy is concentrated across the Circum-Pacific seismic belt."
        s2 = "Boreal taiga forests are distributed across the subarctic zones of North America and northern Eurasia."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "distribution")

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "distribution")
        self.assertIn("boreal taiga forests", n2.primary_entity.lower())

    def test_07_classification_subclasses(self):
        s1 = "Geomorphologists classify river drainage patterns into four primary types: dendritic, trellis, radial, and rectangular."
        s2 = "Sedimentary rocks can be divided into clastic, chemical, and organic sedimentary categories."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "classification")
        self.assertTrue(len(n1.secondary_entities) >= 3)

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "classification")

    def test_08_quantity_formatted_numbers_with_commas(self):
        r"""Quantity: Numbers containing commas like '40,075 kilometres' parse fully to 40075.0."""
        s = "The equatorial circumference of the Earth measures approximately 40,075 kilometres."
        node = self.extractor.extract(s)[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "quantity")
        self.assertEqual(node.quantitative_data["value"], 40075.0)
        self.assertEqual(node.quantitative_data["unit"], "kilometres")

    def test_09_sequence_colon_secondary_entities(self):
        """Sequence: Colon-separated stages populate secondary_entities with distinct stages."""
        s = "Volcanic caldera formation progresses through a distinct sequence: rapid magma chamber evacuation, structural roof collapse, and secondary resurgent dome uplift."
        node = self.extractor.extract(s)[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "sequence")
        self.assertEqual(len(node.secondary_entities), 3)
        self.assertIn("rapid magma chamber evacuation", node.secondary_entities)

    def test_10_condition_physical_thresholds(self):
        s1 = "Tropical cyclogenesis can occur only if sea surface temperatures exceed 26.5 degrees Celsius across substantial oceanic depths."
        s2 = "Metamorphic recrystallization occurs only when confining lithostatic pressure and temperature exceed standard diagenetic thresholds."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "condition")
        self.assertIn("tropical cyclogenesis", n1.primary_entity.lower())

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "condition")

    def test_11_exception_contrastive_clauses(self):
        s1 = "Except for the ozone layer in the stratosphere, atmospheric gases have relatively low absorption capacity for solar ultraviolet radiation."
        s2 = "While nearly all celestial planets orbit in circular trajectories, comets are unique exceptions that travel in highly eccentric parabolic or hyperbolic orbits."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "exception")
        self.assertTrue(len(n1.secondary_entities) >= 1)

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "exception")
        self.assertTrue(len(n2.secondary_entities) >= 1)

    def test_12_process_biogeochemical_conversions(self):
        s1 = "Subduction zone metamorphism is the thermodynamic process whereby hydrated oceanic crust minerals release volatile fluids into the overriding mantle wedge."
        s2 = "Nitrogen fixation converts unreactive atmospheric dinitrogen gas into bioavailable ammonia and nitrate ions."

        n1 = self.extractor.extract(s1)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "process")

        n2 = self.extractor.extract(s2)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "process")

    def test_13_part_of_spatial_preposition(self):
        """Part-of: Components with spatial prepositions like 'located immediately beneath...' extract as part_of."""
        s = "The asthenosphere constitutes the ductile upper mantle portion located immediately beneath the rigid lithospheric plates."
        node = self.extractor.extract(s)[0]
        self.assertEqual(canonicalize_intent(node.intent_type), "part_of")
        self.assertIn("rigid lithospheric plates", node.secondary_entities)


class TestChallengerPronounAndAnaphora(unittest.TestCase):
    """Stress tests on ungrounded pronouns, anaphora shielding, and discourse resolution."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_ungrounded_isolated_bare_pronouns_return_zero_nodes(self):
        """Personal and demonstrative bare pronouns MUST return 0 nodes in isolation."""
        ungrounded = [
            "It is characterized by extreme aridity and sparse vegetation.",
            "They are distributed across the subarctic zones of North America.",
            "These are classified into three major tectonic boundary types.",
            "Those have the lowest mean density among all planets.",
            "He proposed the continental drift hypothesis in 1912.",
            "She discovered the seismic discontinuity between the outer and inner core.",
            "This is defined as the point on the surface directly above the focus.",
            "That results in devastating tsunami waves across coastal regions.",
            "Its atmosphere is composed primarily of carbon dioxide and nitrogen.",
            "Their orbits maintain high eccentricities across centuries.",
        ]
        for sent in ungrounded:
            nodes = self.extractor.extract(sent)
            self.assertEqual(
                len(nodes), 0,
                f"Pronoun shield leak! Sentence: '{sent}' yielded {nodes}"
            )

    def test_block_without_antecedent_starting_with_pronoun_returns_zero_nodes(self):
        block = NormalizedBlock(
            id="blk_ungrounded",
            text="It is an arid plateau. They receive minimal annual rainfall.",
            type="PROSE",
            clean_sentences=[
                "It is an arid plateau.",
                "They receive minimal annual rainfall."
            ],
            metadata={"sourceId": "test_ungrounded", "page": 1}
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 0, f"Leaked nodes from ungrounded block: {nodes}")

    def test_grounded_discourse_resolves_pronoun_correctly(self):
        block = NormalizedBlock(
            id="blk_grounded",
            text="The Thar Desert is an arid region in northwestern India. It is characterized by low annual precipitation and shifting sand dunes.",
            type="PROSE",
            clean_sentences=[
                "The Thar Desert is an arid region in northwestern India.",
                "It is characterized by low annual precipitation and shifting sand dunes."
            ],
            metadata={"sourceId": "test_grounded", "page": 1}
        )
        nodes = self.extractor.extract(block)
        self.assertGreaterEqual(len(nodes), 2)
        self.assertEqual(nodes[0].primary_entity, "Thar Desert")
        self.assertEqual(nodes[1].primary_entity, "Thar Desert")
        self.assertEqual(canonicalize_intent(nodes[1].intent_type), "attribute")

    def test_demonstrative_determiner_vs_bare_pronoun(self):
        bare = "These are classified into three major rock types based on origin."
        self.assertEqual(len(self.extractor.extract(bare)), 0)

        determiner = "These crystalline rocks can be classified into intrusive and extrusive igneous categories."
        det_nodes = self.extractor.extract(determiner)
        self.assertGreaterEqual(len(det_nodes), 1)
        self.assertIn("rocks", det_nodes[0].primary_entity.lower())
        self.assertEqual(canonicalize_intent(det_nodes[0].intent_type), "classification")


class TestChallengerIntegrityAntiOverfitting(unittest.TestCase):
    """Confirms 0 banned golden set strings in semantic_extractor.py."""

    def test_no_hardcoded_golden_strings_in_extractor(self):
        extractor_path = os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py")
        with open(extractor_path, "r", encoding="utf-8") as f:
            code = f.read().lower()

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
            "geologists|scientists|geographers|plate tectonics"
        ]

        found = [b for b in banned_domain_strings if b.lower() in code]
        self.assertEqual(found, [], f"Hardcoded domain strings found: {found}")


if __name__ == "__main__":
    unittest.main()
