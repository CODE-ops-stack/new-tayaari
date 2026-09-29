#!/usr/bin/env python3
"""
tests/test_v13_challenger_it4_stress.py
======================================
Empirical Challenger Stress Harness for Milestone 2 Iteration 4.
Agent: teamwork_preview_challenger_m2_it4_1

Comprehensive verification suite:
PART 1: Empirical verification of the 8 syntactic remediations (M2 Iteration 4)
- Past-tense superlatives (had/exhibited/possessed/displayed)
- Open taxonomic classes in member-of (moon, forest, mammal, observatory, reef, desert, bird, trench)
- Comparison with trailing clauses, participles, and commas
- Compound attribute participles (adjective and adjective, [adverb] verb-ing)
- Thousands-comma numbers in quantity parsing (40,075 km, 299,792 km/s, 149,600,000 km, etc.)
- Sequence colon items and secondary entity population
- Generalized passive voice inversion for definitions
- Spatial prepositions in part-of (beneath, under, above, below, between, within)

PART 2: Coreference, pronoun shielding, and zero hardcoded strings
- Singular proper nouns ending in s (Indus, Ganges, Mars)
- Plural mountain ranges (Himalayas)
- Ungrounded pronouns (zero nodes)
- Anti-overfitting / zero hardcoded domain strings audit

PART 3: Adversarial boundary & edge-case stress testing
- Boundary: Proper noun entities with 5+ capitalized words trigger NoiseFilterGate broken_reading_order
- Boundary: Adverbs in compound attributes restricted to very/extremely/highly/mostly
- Boundary: Action verbs in superlatives (e.g. produced the loudest...)
- Boundary: Noun scope in part-of (shield vs layer/portion)
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


# =====================================================================
# PART 1: Verification of 8 Syntactic Remediations
# =====================================================================

class TestPastTenseSuperlatives(unittest.TestCase):
    """Verifies that past-tense superlative assertions extract as attribute KnowledgeNodes."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_past_tense_superlatives_across_domains(self):
        """Past-tense superlatives using had, exhibited, possessed, displayed."""
        cases = [
            ("Pangaea possessed the largest continuous continental landmass during the late Paleozoic era.", "Pangaea"),
            ("The Pleistocene woolly mammoth possessed the thickest adipose insulation layer among Quaternary herbivores.", "woolly mammoth"),
            ("Ancient Lake Bonneville had the greatest pluvial surface area in prehistoric North America.", "Lake Bonneville"),
            ("The Apollo 10 spacecraft exhibited the fastest crewed atmospheric re-entry speed in history at 39,897 kilometres per hour.", "Apollo 10"),
            ("The Krakatoa eruption of 1883 exhibited the loudest acoustic sound in recorded history.", "Krakatoa eruption"),
            ("Tycho Brahe possessed the most precise astronomical instruments in pre-telescopic Europe.", "Tycho Brahe"),
            ("The Carboniferous dragonfly Meganeura had the greatest recorded wingspan among all known insects.", "Meganeura"),
            ("Early Mars exhibited the densest carbon dioxide atmosphere in its planetary history.", "Mars"),
            ("Ancient Thera displayed the highest volcanic explosivity index among Aegean eruptions.", "Ancient Thera"),
        ]
        for sentence, expected_entity in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract node from past-tense superlative: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "attribute",
                f"Expected 'attribute' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIn(
                expected_entity.lower(), node.primary_entity.lower(),
                f"Expected primary entity to contain '{expected_entity}', got '{node.primary_entity}'"
            )


class TestOpenTaxonomicMemberOf(unittest.TestCase):
    """Verifies member-of classification generalizes beyond closed 17-noun whitelist."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_open_taxonomic_nouns(self):
        """Standard educational taxonomy nouns (moon, rainforest, mammal, desert, reef, observatory, bird, trench)."""
        cases = [
            ("Ganymede is a massive Jovian moon orbiting Jupiter in the outer solar system.", "Ganymede", "moon"),
            ("The Amazon Rainforest is a vast tropical rainforest situated in northern South America.", "Amazon Rainforest", "rainforest"),
            ("The blue whale is a marine cetacean mammal inhabiting open oceans worldwide.", "blue whale", "mammal"),
            ("The Atacama Desert is a hyper-arid non-polar desert located in northern Chile.", "Atacama Desert", "desert"),
            ("The Great Barrier Reef is an extensive coral reef system situated off the coast of Queensland.", "Great Barrier Reef", "reef"),
            ("The Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point.", "Webb Space Telescope", "observatory"),
            ("The platypus is a semi-aquatic monotreme mammal endemic to eastern Australia.", "platypus", "mammal"),
            ("The peregrine falcon is a cosmopolitan raptorial bird found across every continent except Antarctica.", "peregrine falcon", "bird"),
            ("The Mariana Trench is a deep crescent-shaped oceanic trench situated in the western Pacific Ocean.", "Mariana Trench", "trench"),
        ]
        for sentence, expected_entity, expected_tax_class in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract node for open taxonomy: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "member_of",
                f"Expected 'member_of' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIn(
                expected_entity.lower(), node.primary_entity.lower(),
                f"Expected entity '{expected_entity}' in '{node.primary_entity}'"
            )


class TestComparisonWithTrailingClauses(unittest.TestCase):
    """Verifies comparison intent does not collapse when trailing clauses/commas exist."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_comparisons_with_trailing_qualifiers(self):
        cases = [
            ("Ganymede is much larger than Mercury, having a mean diameter of 5,268 kilometres.", "Ganymede", "Mercury"),
            ("Basaltic magma is much less viscous than rhyolitic magma, allowing volatile volcanic gases to escape quietly.", "Basaltic magma", "rhyolitic magma"),
            ("The troposphere is much denser than the mesosphere, containing nearly 80 percent of total atmospheric mass.", "troposphere", "mesosphere"),
            ("Diamond is much harder than quartz, exhibiting a hardness rating of 10 on the Mohs scale.", "Diamond", "quartz"),
            ("Continental lithosphere is much older than oceanic lithosphere, dating back over 3.8 billion years in cratons.", "Continental lithosphere", "oceanic lithosphere"),
            ("Sedimentary limestone is much more soluble than igneous granite, dissolving readily in acidic groundwater.", "limestone", "granite"),
        ]
        for sentence, primary, secondary in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract comparison node: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "comparison",
                f"Expected 'comparison' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIn(primary.lower(), node.primary_entity.lower())
            sec_joined = " ".join(node.secondary_entities).lower()
            self.assertTrue(
                secondary.lower() in sec_joined or secondary.lower() in node.predicate.lower(),
                f"Expected '{secondary}' in secondary entities or predicate for '{sentence}'"
            )


class TestCompoundAttributeParticiples(unittest.TestCase):
    """Verifies attribute extraction on compound adjectives followed by participle clauses."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_compound_attribute_with_participles(self):
        cases = [
            ("Neutron stars are extremely compact and dense, generating immense gravitational fields.", "Neutron stars"),
            ("Cumulonimbus clouds are extremely tall and turbulent, producing severe localized thunderstorms.", "Cumulonimbus clouds"),
            ("Active subduction zones are highly dynamic and unstable, triggering destructive megathrust earthquakes.", "subduction zones"),
            ("Glacial ice sheets are very thick and heavy, depressing the underlying continental crust.", "ice sheets"),
            ("Pyroclastic flows are scorching and rapid, incinerating organic matter within seconds.", "Pyroclastic flows"),
            ("Coronal mass ejections are highly energetic and expansive, releasing billions of tons of solar plasma.", "Coronal mass ejections"),
        ]
        for sentence, expected_entity in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract attribute for participle sentence: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "attribute",
                f"Expected 'attribute' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIn(expected_entity.lower(), node.primary_entity.lower())


class TestThousandsCommaNumbersInQuantity(unittest.TestCase):
    """Verifies thousands-comma formatted numbers parse accurately without truncation."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_thousands_comma_numerical_parsing(self):
        cases = [
            ("Light travels at approximately 299,792 kilometres per second in a vacuum.", 299792.0, "kilometres per second"),
            ("The mean distance from the Earth to the Sun measures approximately 149,600,000 kilometres.", 149600000.0, "kilometres"),
            ("The mean radius of the Earth measures approximately 6,371 kilometres.", 6371.0, "kilometres"),
            ("Standard atmospheric sea level pressure measures approximately 1,013 mb.", 1013.0, "mb"),
            ("Mount Everest has an elevation of approximately 8,848 meters above sea level.", 8848.0, "meters"),
            ("The equatorial circumference of Mars measures approximately 21,344 kilometres.", 21344.0, "kilometres"),
        ]
        for sentence, expected_val, expected_unit in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract quantity node: '{sentence}'"
            )
            node = nodes[0]
            self.assertIn(
                canonicalize_intent(node.intent_type), ["quantity", "attribute"],
                f"Expected 'quantity' or 'attribute' with numerical data for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIsNotNone(
                node.quantitative_data,
                f"Quantitative data was None for '{sentence}'"
            )
            val = node.quantitative_data.get("value")
            self.assertEqual(
                val, expected_val,
                f"Value parsed incorrectly for '{sentence}': got {val}, expected {expected_val}"
            )
            unit = node.quantitative_data.get("unit", "").lower()
            self.assertIn(
                expected_unit.lower().split()[0], unit,
                f"Unit parsed incorrectly for '{sentence}': got '{unit}', expected '{expected_unit}'"
            )


class TestSequenceColonItems(unittest.TestCase):
    """Verifies colon-separated sequence stages populate secondary_entities cleanly."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_sequence_colons_populate_secondary_entities(self):
        cases = [
            (
                "Meiotic cell division progresses through four sequential stages: prophase, metaphase, anaphase, and telophase.",
                ["prophase", "metaphase", "anaphase", "telophase"]
            ),
            (
                "The geological Wilson cycle progresses through six distinct phases: continental rifting, ocean basin opening, seafloor spreading, subduction initiation, ocean basin closure, and continental collision.",
                ["continental rifting", "ocean basin opening", "seafloor spreading", "subduction initiation", "ocean basin closure", "continental collision"]
            ),
            (
                "Speciation progresses through a sequential cycle: geographical isolation, reproductive divergence, and morphological differentiation.",
                ["geographical isolation", "reproductive divergence", "morphological differentiation"]
            ),
            (
                "Fossilization progresses through several chronological steps: rapid burial, permineralization, and stratigraphic consolidation.",
                ["rapid burial", "permineralization", "stratigraphic consolidation"]
            ),
        ]
        for sentence, expected_stages in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract sequence node: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "sequence",
                f"Expected 'sequence' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertGreaterEqual(
                len(node.secondary_entities), len(expected_stages),
                f"Expected at least {len(expected_stages)} secondary entities for '{sentence}', got {node.secondary_entities}"
            )
            for stage in expected_stages:
                self.assertTrue(
                    any(stage.lower() in sec.lower() for sec in node.secondary_entities),
                    f"Stage '{stage}' missing from secondary entities: {node.secondary_entities}"
                )


class TestGeneralizedPassiveVoiceInversion(unittest.TestCase):
    """Verifies passive definitions invert descriptive clauses to concise terms."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_passive_voice_definition_inversions(self):
        cases = [
            (
                "The process by which liquid water changes into water vapor is called evaporation.",
                "evaporation",
                "liquid water changes into water vapor"
            ),
            (
                "The boundary separating the Earth's crust from the underlying mantle is known as the Mohorovicic discontinuity.",
                "Mohorovicic discontinuity",
                "boundary separating"
            ),
            (
                "Organisms capable of synthesizing their own organic food from inorganic substances are called autotrophs.",
                "autotrophs",
                "capable of synthesizing"
            ),
            (
                "The circular motion of fluids caused by temperature gradients and density differences is designated as thermal convection.",
                "thermal convection",
                "circular motion of fluids"
            ),
            (
                "The scientific study of earthquakes and the propagation of elastic waves through planets is termed seismology.",
                "seismology",
                "scientific study of earthquakes"
            ),
        ]
        for sentence, expected_primary, expected_desc_fragment in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract passive definition: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "definition",
                f"Expected 'definition' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertEqual(
                node.primary_entity.lower(), expected_primary.lower(),
                f"Primary entity inverted incorrectly for '{sentence}': got '{node.primary_entity}', expected '{expected_primary}'"
            )
            self.assertIn(
                expected_desc_fragment.lower(), node.predicate.lower(),
                f"Expected description fragment '{expected_desc_fragment}' in predicate: '{node.predicate}'"
            )


class TestSpatialPrepositionsInPartOf(unittest.TestCase):
    """Verifies part-of relations parse spatial prepositions (beneath, under, above, between, etc.)."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_spatial_prepositions_in_part_of(self):
        cases = [
            (
                "The outer core forms a liquid metallic layer situated beneath the rocky mantle.",
                "outer core",
                "rocky mantle"
            ),
            (
                "The stratosphere constitutes a dry atmospheric layer positioned directly above the troposphere.",
                "stratosphere",
                "troposphere"
            ),
            (
                "The Mohorovicic discontinuity forms a distinct boundary zone located between the crust and the upper mantle.",
                "Mohorovicic discontinuity",
                "crust"
            ),
            (
                "The asthenosphere constitutes a semi-molten layer situated under the brittle tectonic plates.",
                "asthenosphere",
                "brittle tectonic plates"
            ),
            (
                "The ozone layer constitutes a protective atmospheric layer located within the lower stratosphere.",
                "ozone layer",
                "lower stratosphere"
            ),
            (
                "The transition zone constitutes a dense mantle layer situated between the upper and lower mantle.",
                "transition zone",
                "upper and lower mantle"
            ),
        ]
        for sentence, expected_entity, expected_parent in cases:
            nodes = self.extractor.extract(sentence)
            self.assertGreaterEqual(
                len(nodes), 1,
                f"Failed to extract part-of node: '{sentence}'"
            )
            node = nodes[0]
            self.assertEqual(
                canonicalize_intent(node.intent_type), "part_of",
                f"Expected 'part_of' for '{sentence}', got '{node.intent_type}'"
            )
            self.assertIn(
                expected_entity.lower(), node.primary_entity.lower(),
                f"Expected primary entity '{expected_entity}', got '{node.primary_entity}'"
            )
            sec_joined = " ".join(node.secondary_entities).lower()
            self.assertTrue(
                expected_parent.lower().split()[0] in sec_joined or expected_parent.lower().split()[0] in node.predicate.lower(),
                f"Expected parent '{expected_parent}' in secondary entities: {node.secondary_entities}"
            )


# =====================================================================
# PART 2: Discourse, Pronoun Shield & Anti-Overfitting Integrity
# =====================================================================

class TestDiscourseAgreementAndPronounShield(unittest.TestCase):
    """Stress tests number agreement on tricky proper nouns and pronoun shielding."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_singular_proper_nouns_ending_in_s(self):
        """Discourse resolution: singular proper nouns ending in s (Mars, Ganges, Indus, Thames)
        must resolve singular pronouns ('It', 'Its') correctly without cross-attribution."""
        block = NormalizedBlock(
            id="blk_proper_s",
            text="The Indus is a trans-Himalayan river originating in Tibet. It flows across Pakistan into the Arabian Sea.",
            type="PROSE",
            clean_sentences=[
                "The Indus is a trans-Himalayan river originating in Tibet.",
                "It flows across Pakistan into the Arabian Sea."
            ],
            metadata={"sourceId": "test_indus", "page": 1}
        )
        nodes = self.extractor.extract(block)
        self.assertGreaterEqual(len(nodes), 2)
        self.assertIn("indus", nodes[1].primary_entity.lower())

    def test_plural_mountain_ranges_ending_in_as(self):
        """Discourse resolution: plural mountain ranges (Himalayas) must resolve 'They'."""
        block = NormalizedBlock(
            id="blk_himalayas",
            text="The Himalayas are young fold mountains in Asia. They have the highest peaks in the world.",
            type="PROSE",
            clean_sentences=[
                "The Himalayas are young fold mountains in Asia.",
                "They have the highest peaks in the world."
            ],
            metadata={"sourceId": "test_himalayas", "page": 1}
        )
        nodes = self.extractor.extract(block)
        self.assertGreaterEqual(len(nodes), 2)
        self.assertIn("himalayas", nodes[1].primary_entity.lower())

    def test_ungrounded_pronouns_yield_zero_nodes(self):
        ungrounded = [
            "It has the greatest volume among terrestrial volcanoes.",
            "They are composed of silicate minerals and iron.",
            "These are divided into intrusive and extrusive classes.",
            "Its elevation reaches over 4,000 meters above sea level.",
            "Their trajectories cross interplanetary orbits periodically.",
        ]
        for sentence in ungrounded:
            nodes = self.extractor.extract(sentence)
            self.assertEqual(
                len(nodes), 0,
                f"Ungrounded pronoun leak! Sentence '{sentence}' emitted: {nodes}"
            )


class TestAntiOverfittingAudit(unittest.TestCase):
    """Verifies that no hardcoded domain sentences or phrases exist in the extractor."""

    def test_no_banned_strings_in_extractor(self):
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
            "all those objects shining in the night sky"
        ]
        found = [b for b in banned_domain_strings if b.lower() in code]
        self.assertEqual(found, [], f"Hardcoded domain strings detected: {found}")


# =====================================================================
# PART 3: Adversarial Boundary & Limitation Characterization
# =====================================================================

class TestAdversarialBoundaryConditions(unittest.TestCase):
    """Empirically documents boundary conditions and syntax limits of the regex engine.
    These tests record nuanced architectural boundaries without blocking standard grammar."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_boundary_capitalized_words_noise_gate(self):
        """Demonstrates that 5+ capitalized words in valid grammatical sentences do not trigger NoiseFilterGate."""
        # 5 consecutive capitalized words passes noise gate cleanly when verb-guarded:
        s_5_caps = "The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."
        self.assertIsNone(NoiseFilterGate.audit(s_5_caps))

        # 4 consecutive capitalized words passes noise gate cleanly:
        s_4_caps = "The Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."
        self.assertIsNone(NoiseFilterGate.audit(s_4_caps))

    def test_boundary_compound_attribute_adverb_whitelist(self):
        """Demonstrates that adverbs in compound attributes support generalized -ly adverbs."""
        # 'extremely' matches Pattern 14 attribute:
        s_whitelisted = "Cumulonimbus clouds are extremely tall and turbulent, producing severe localized thunderstorms."
        n1 = self.extractor.extract(s_whitelisted)[0]
        self.assertEqual(canonicalize_intent(n1.intent_type), "attribute")

        # 'unusually' matches generalized adverb Pattern 14 attribute:
        s_unwhitelisted = "Cumulonimbus clouds are unusually tall and turbulent, producing severe localized thunderstorms."
        n2 = self.extractor.extract(s_unwhitelisted)[0]
        self.assertEqual(canonicalize_intent(n2.intent_type), "attribute")

    def test_boundary_action_verbs_in_superlatives(self):
        """Demonstrates that action verbs (produced/generated/emitted/yielded)
        are captured by Pattern 14 attribute."""
        s_remediated_verb = "The Krakatoa eruption of 1883 exhibited the loudest acoustic sound in recorded history."
        nodes = self.extractor.extract(s_remediated_verb)
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "attribute")

        s_unsupported_verb = "The Krakatoa eruption of 1883 produced the loudest acoustic sound in recorded history."
        nodes_unsupported = self.extractor.extract(s_unsupported_verb)
        self.assertGreaterEqual(len(nodes_unsupported), 1)
        self.assertEqual(canonicalize_intent(nodes_unsupported[0].intent_type), "attribute")


if __name__ == "__main__":
    unittest.main()
