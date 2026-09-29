#!/usr/bin/env python3
"""
tests/test_v13_challenger_it5_empirics.py
==========================================
Empirical Challenger Verification Suite for Milestone 2 Iteration 5.
Agent: teamwork_preview_challenger_m2_it5_1 (Challenger 1)

Mandatory Verification Coverage:
1. Generalized Quantity Patterns:
   - Verbs: maintains, has, had, exhibits, possesses (and plural forms)
   - Properties: axial tilt, axial inclination, equatorial radius, altitude, depth, thickness, density
   - Unseen planetary, geophysical, and atmospheric domain sentences
   - Verification: extracted as 'quantity', primary entity cleanly isolated, quantitative data parsed.
2. Generalized Sequence Patterns:
   - Inception and progression sequences:
     * 'begins with ... followed by ...'
     * 'began with ... followed by ...'
     * 'condense first ... followed in turn by ...'
     * 'condenses first ... followed in turn by ...'
     * 'arrive first ... followed sequentially by ...'
     * 'forms first ... followed in turn by ...'
     * 'starts initially ... followed by ...'
     * 'progresses through ... followed by ...'
   - Verification: extracted as 'sequence', primary entity preserved.
3. Generalized Superlative Patterns:
   - Action verbs: produced, generated, emitted, yielded (and present tense)
   - Superlatives: loudest, brightest, highest (and related physical superlatives)
   - Verification: extracted as 'attribute', entity and predicate correctly matched.
4. Anti-Overfitting Forensic Audit:
   - Strict AST/string inspection ensuring 0 occurrences of audited golden phrases
     (POS-032, POS-034, POS-036, NEG-021, NEG-030, NEG-031, NEG-033).
"""

import os
import sys
import unittest
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    NoiseFilterGate,
    KnowledgeNode,
    canonicalize_intent,
)


class TestQuantityGeneralizationEmpirics(unittest.TestCase):
    """Exhaustive empirical testing of generalized quantity patterns on unseen domain sentences.
    Verifies all permutations of verbs [maintains, has, had, exhibits, possesses]
    with physical properties [axial tilt, axial inclination, equatorial radius, altitude, depth, thickness, density].
    """

    def setUp(self):
        self.extractor = SemanticExtractor()

    def _assert_quantity_extraction(
        self, sentence: str, expected_entity: str, expected_prop: str, expected_val: float
    ) -> KnowledgeNode:
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Failed to extract any KnowledgeNode from quantity sentence: '{sentence}'"
        )
        node = nodes[0]
        actual_intent = canonicalize_intent(node.intent_type)
        self.assertEqual(
            actual_intent, "quantity",
            f"Expected 'quantity' intent for '{sentence}', got '{actual_intent}'"
        )
        self.assertIn(
            expected_entity.lower(), node.primary_entity.lower(),
            f"Expected entity '{expected_entity}' in '{node.primary_entity}' for '{sentence}'"
        )
        self.assertTrue(
            expected_prop.lower() in node.predicate.lower() or expected_prop.lower() in node.raw_evidence.lower(),
            f"Expected property '{expected_prop}' in predicate or raw_evidence for '{sentence}'"
        )
        self.assertIsNotNone(
            node.quantitative_data,
            f"Expected parsed quantitative_data for '{sentence}', got None"
        )
        self.assertAlmostEqual(
            node.quantitative_data["value"], expected_val, places=1,
            msg=f"Expected value {expected_val}, got {node.quantitative_data['value']} for '{sentence}'"
        )
        return node

    def test_quantity_verb_maintains_permutations(self):
        """Verify 'maintains' across various physical properties."""
        test_cases = [
            ("The Earth maintains an axial tilt of 23.5 degrees.", "Earth", "axial tilt", 23.5),
            ("Mars maintains an axial inclination of 25.2 degrees.", "Mars", "axial inclination", 25.2),
            ("The stratosphere maintains an altitude of 50 kilometres.", "stratosphere", "altitude", 50.0),
            ("The continental shield maintains a thickness of 40 kilometres.", "continental shield", "thickness", 40.0),
            ("The oceanic trench maintains a depth of 6500 meters.", "oceanic trench", "depth", 6500.0),
            ("The basaltic layer maintains a density of 2.9 g/cm^3.", "basaltic layer", "density", 2.9),
            ("Jupiter maintains an equatorial radius of 71492 kilometres.", "Jupiter", "equatorial radius", 71492.0),
        ]
        for s, ent, prop, val in test_cases:
            self._assert_quantity_extraction(s, ent, prop, val)

    def test_quantity_verb_has_permutations(self):
        """Verify 'has' across various physical properties."""
        test_cases = [
            ("Uranus has an axial inclination of 97.8 degrees.", "Uranus", "axial inclination", 97.8),
            ("Saturn has an equatorial radius of 60268 kilometres.", "Saturn", "equatorial radius", 60268.0),
            ("Mount Everest has an altitude of 8848 meters.", "Mount Everest", "altitude", 8848.0),
            ("The oceanic abyss has a depth of 4000 meters.", "oceanic abyss", "depth", 4000.0),
            ("The lithospheric plate has a thickness of 100 kilometres.", "lithospheric plate", "thickness", 100.0),
            ("The continental granite has a density of 2.7 g/cm^3.", "continental granite", "density", 2.7),
            ("Neptune has an axial tilt of 28.3 degrees.", "Neptune", "axial tilt", 28.3),
        ]
        for s, ent, prop, val in test_cases:
            self._assert_quantity_extraction(s, ent, prop, val)

    def test_quantity_verb_had_permutations(self):
        """Verify past tense 'had' across various physical properties."""
        test_cases = [
            ("The primordial Earth had an axial tilt of 24.0 degrees.", "primordial Earth", "axial tilt", 24.0),
            ("Ancient Mars had an equatorial radius of 3390 kilometres.", "Ancient Mars", "equatorial radius", 3390.0),
            ("The prehistoric caldera had a depth of 1200 meters.", "prehistoric caldera", "depth", 1200.0),
            ("The ancestral ice sheet had a thickness of 3000 meters.", "ancestral ice sheet", "thickness", 3000.0),
            ("The collapsed volcano had an altitude of 4500 meters.", "collapsed volcano", "altitude", 4500.0),
            ("The proto-planetary core had a density of 8.5 g/cm^3.", "proto-planetary core", "density", 8.5),
            ("Early Venus had an axial inclination of 177.3 degrees.", "Early Venus", "axial inclination", 177.3),
        ]
        for s, ent, prop, val in test_cases:
            self._assert_quantity_extraction(s, ent, prop, val)

    def test_quantity_verb_exhibits_permutations(self):
        """Verify 'exhibits' across various physical properties."""
        test_cases = [
            ("The Martian axis exhibits an axial tilt of 25.19 degrees.", "Martian axis", "axial tilt", 25.19),
            ("Mercury exhibits an axial inclination of 0.03 degrees.", "Mercury", "axial inclination", 0.03),
            ("Callisto exhibits an equatorial radius of 2410 kilometres.", "Callisto", "equatorial radius", 2410.0),
            ("The Tibetan plateau exhibits an altitude of 4500 meters.", "Tibetan plateau", "altitude", 4500.0),
            ("The rift valley exhibits a depth of 1500 meters.", "rift valley", "depth", 1500.0),
            ("The permafrost layer exhibits a thickness of 25 meters.", "permafrost layer", "thickness", 25.0),
            ("The subducted slab exhibits a density of 3.4 g/cm^3.", "subducted slab", "density", 3.4),
        ]
        for s, ent, prop, val in test_cases:
            self._assert_quantity_extraction(s, ent, prop, val)

    def test_quantity_verb_possesses_permutations(self):
        """Verify 'possesses' across various physical properties."""
        test_cases = [
            ("The Mariana Trench possesses a depth of 10994 meters.", "Mariana Trench", "depth", 10994.0),
            ("Ganymede possesses an equatorial radius of 2634 kilometres.", "Ganymede", "equatorial radius", 2634.0),
            ("The inner core possesses a density of 13 g/cm^3.", "inner core", "density", 13.0),
            ("The mesosphere possesses an altitude of 85 kilometres.", "mesosphere", "altitude", 85.0),
            ("The oceanic crust possesses a thickness of 7 kilometres.", "oceanic crust", "thickness", 7.0),
            ("The dwarf planet Ceres possesses an axial tilt of 4.0 degrees.", "Ceres", "axial tilt", 4.0),
            ("The gas giant possesses an axial inclination of 3.1 degrees.", "gas giant", "axial inclination", 3.1),
        ]
        for s, ent, prop, val in test_cases:
            self._assert_quantity_extraction(s, ent, prop, val)


class TestSequenceGeneralizationEmpirics(unittest.TestCase):
    """Exhaustive empirical testing of generalized sequence patterns on unseen domain sentences.
    Verifies inception, progression, and multi-stage sequential descriptions.
    """

    def setUp(self):
        self.extractor = SemanticExtractor()

    def _assert_sequence_extraction(self, sentence: str, expected_entity: str) -> KnowledgeNode:
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Failed to extract any KnowledgeNode from sequence sentence: '{sentence}'"
        )
        node = nodes[0]
        actual_intent = canonicalize_intent(node.intent_type)
        self.assertEqual(
            actual_intent, "sequence",
            f"Expected 'sequence' intent for '{sentence}', got '{actual_intent}'"
        )
        self.assertIn(
            expected_entity.lower(), node.primary_entity.lower(),
            f"Expected entity '{expected_entity}' in '{node.primary_entity}' for '{sentence}'"
        )
        return node

    def test_inception_begins_with_followed_by(self):
        """Verify 'begins with ... followed by ...' and 'began with ... followed by ...'."""
        test_cases = [
            ("Stellar evolution begins with gravitational collapse followed by thermonuclear hydrogen fusion.", "stellar evolution"),
            ("The Wilson cycle began with continental rifting followed by seafloor spreading.", "Wilson cycle"),
            ("Magma crystallization begins with olivine precipitation followed by pyroxene formation.", "magma crystallization"),
            ("Orogenesis begins with tectonic convergence followed by crustal thickening.", "orogenesis"),
        ]
        for s, ent in test_cases:
            self._assert_sequence_extraction(s, ent)

    def test_inception_condense_first_followed_in_turn_by(self):
        """Verify 'condense first ... followed in turn by ...' and variants."""
        test_cases = [
            ("Refractory mineral grains condense first from the solar nebula followed in turn by silicates and metallic iron.", "Refractory mineral grains"),
            ("Heavy silicates condense first in cooling protosolar gas followed in turn by lighter volatiles.", "Heavy silicates"),
            ("High-temperature compounds condense first during nebular cooling followed sequentially by hydrated minerals.", "High-temperature compounds"),
        ]
        for s, ent in test_cases:
            self._assert_sequence_extraction(s, ent)

    def test_inception_arrive_first_followed_sequentially_by(self):
        """Verify 'arrive first ... followed sequentially by ...' and variants."""
        test_cases = [
            ("Compressional P-waves arrive first at seismological observatories followed sequentially by transverse S-waves.", "Compressional P-waves"),
            ("Direct seismic waves arrive first at the epicentral detector followed sequentially by reflected crustal phases.", "Direct seismic waves"),
        ]
        for s, ent in test_cases:
            self._assert_sequence_extraction(s, ent)

    def test_inception_forms_first_and_starts_initially(self):
        """Verify 'forms first ... followed in turn by' and 'starts initially ... followed by'."""
        test_cases = [
            ("Basaltic oceanic crust forms first along mid-ocean ridges followed in turn by pelagic sediment accumulation.", "Basaltic oceanic crust"),
            ("The monsoon depression starts initially over the Bay of Bengal followed by westward propagation across central India.", "monsoon depression"),
            ("Glacial valley erosion commences initially with cirque carving followed by U-shaped trough deepening.", "Glacial valley erosion"),
        ]
        for s, ent in test_cases:
            self._assert_sequence_extraction(s, ent)

    def test_progression_through_stages(self):
        """Verify 'progresses through ... stages/phases/cycle followed by'."""
        test_cases = [
            ("The geomorphic erosion cycle progresses through youth and maturity stages followed by the senile peneplain stage.", "geomorphic erosion cycle"),
            ("Tropical cyclone development progresses through depression and storm phases followed by mature hurricane equilibrium.", "Tropical cyclone development"),
        ]
        for s, ent in test_cases:
            self._assert_sequence_extraction(s, ent)


class TestSuperlativeGeneralizationEmpirics(unittest.TestCase):
    """Exhaustive empirical testing of generalized superlative patterns on unseen domain sentences.
    Verifies verbs [produced, generated, emitted, yielded] with superlatives [loudest, brightest, highest].
    """

    def setUp(self):
        self.extractor = SemanticExtractor()

    def _assert_superlative_extraction(
        self, sentence: str, expected_entity: str, expected_verb: str, expected_superlative: str
    ) -> KnowledgeNode:
        nodes = self.extractor.extract(sentence)
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Failed to extract any KnowledgeNode from superlative sentence: '{sentence}'"
        )
        node = nodes[0]
        actual_intent = canonicalize_intent(node.intent_type)
        self.assertEqual(
            actual_intent, "attribute",
            f"Expected 'attribute' intent for '{sentence}', got '{actual_intent}'"
        )
        self.assertIn(
            expected_entity.lower(), node.primary_entity.lower(),
            f"Expected entity '{expected_entity}' in '{node.primary_entity}' for '{sentence}'"
        )
        self.assertIn(
            expected_verb.lower(), node.predicate.lower(),
            f"Expected verb '{expected_verb}' in predicate '{node.predicate}' for '{sentence}'"
        )
        self.assertIn(
            expected_superlative.lower(), node.predicate.lower(),
            f"Expected superlative '{expected_superlative}' in predicate '{node.predicate}' for '{sentence}'"
        )
        return node

    def test_superlatives_with_verb_produced(self):
        """Verify 'produced' combined with loudest, brightest, highest."""
        test_cases = [
            ("The Krakatoa volcanic explosion produced the loudest acoustic sound in recorded history.", "Krakatoa volcanic explosion", "produced", "loudest"),
            ("The hypernova explosion produced the brightest optical flash in the local galactic cluster.", "hypernova explosion", "produced", "brightest"),
            ("The seismic tremor produced the highest peak ground acceleration in the tectonic basin.", "seismic tremor", "produced", "highest"),
            ("The thunderstorm cell produces the highest lightning frequency among regional convective systems.", "thunderstorm cell", "produces", "highest"),
        ]
        for s, ent, verb, sup in test_cases:
            self._assert_superlative_extraction(s, ent, verb, sup)

    def test_superlatives_with_verb_generated(self):
        """Verify 'generated' combined with loudest, brightest, highest."""
        test_cases = [
            ("The Chelyabinsk bolide detonation generated the loudest atmospheric shock wave of the decade.", "Chelyabinsk bolide detonation", "generated", "loudest"),
            ("Supernova SN 1054 generated the brightest apparent magnitude of any historical stellar event.", "Supernova SN 1054", "generated", "brightest"),
            ("The megathrust earthquake generated the highest tsunami wave amplitude along the trench margin.", "megathrust earthquake", "generated", "highest"),
            ("The active galactic nucleus generates the brightest ultraviolet emission in the galaxy cluster.", "active galactic nucleus", "generates", "brightest"),
        ]
        for s, ent, verb, sup in test_cases:
            self._assert_superlative_extraction(s, ent, verb, sup)

    def test_superlatives_with_verb_emitted(self):
        """Verify 'emitted' combined with loudest, brightest, highest."""
        test_cases = [
            ("The solar coronal mass ejection emitted the highest energetic proton flux of the solar cycle.", "solar coronal mass ejection", "emitted", "highest"),
            ("The magnetar giant flare emitted the brightest gamma-ray pulse in recorded astrophysics.", "magnetar giant flare", "emitted", "brightest"),
            ("The submerged acoustic transducer emitted the loudest underwater low-frequency signal in the ocean trench.", "submerged acoustic transducer", "emitted", "loudest"),
            ("The quasar core emits the brightest synchrotron radiation among known extragalactic sources.", "quasar core", "emits", "brightest"),
        ]
        for s, ent, verb, sup in test_cases:
            self._assert_superlative_extraction(s, ent, verb, sup)

    def test_superlatives_with_verb_yielded(self):
        """Verify 'yielded' combined with loudest, brightest, highest."""
        test_cases = [
            ("The underground nuclear test yielded the highest seismic magnitude among artificial explosions.", "underground nuclear test", "yielded", "highest"),
            ("The atmospheric chemical flash yielded the brightest nocturnal illumination in the observation range.", "atmospheric chemical flash", "yielded", "brightest"),
            ("The high-velocity explosive detonation yielded the loudest sonic boom recorded across the salt flats.", "high-velocity explosive detonation", "yielded", "loudest"),
            ("The volcanic caldera collapse yields the highest volume displacement among explosive eruptive events.", "volcanic caldera collapse", "yields", "highest"),
        ]
        for s, ent, verb, sup in test_cases:
            self._assert_superlative_extraction(s, ent, verb, sup)


class TestAntiOverfittingForensicAudit(unittest.TestCase):
    """Forensic verification ensuring zero audited golden strings remain in source code or patterns."""

    BANNED_PHRASES = [
        "maintains a constant tilt of",
        "commenced approximately",
        "arrive first",
        "Out of total water resources",
        "UniverseGalaxySolar System",
        "Planetesimal TheoryNebular HypothesisCopernicus Theory",
        "Three Types of Plate BoundariesThree Types of Plate Boundaries",
    ]

    def test_zero_banned_golden_phrases_in_semantic_extractor(self):
        extractor_path = os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py")
        with open(extractor_path, "r", encoding="utf-8") as f:
            content = f.read()

        for phrase in self.BANNED_PHRASES:
            # Check pattern and code content (ignoring test suite references)
            self.assertNotIn(
                phrase, content,
                f"Forensic violation: Hardcoded golden phrase '{phrase}' found in semantic_extractor.py!"
            )

    def test_zero_banned_golden_phrases_in_normalizer(self):
        normalizer_path = os.path.join(REPO_ROOT, "v13_discovery", "normalizer.py")
        with open(normalizer_path, "r", encoding="utf-8") as f:
            content = f.read()

        for phrase in self.BANNED_PHRASES:
            self.assertNotIn(
                phrase, content,
                f"Forensic violation: Hardcoded golden phrase '{phrase}' found in normalizer.py!"
            )


class TestAdversarialStressAndRejectionGates(unittest.TestCase):
    """Adversarial challenge verifying noise rejection, boundary conditions, and subject-verb plurals."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_interrogative_questions_with_quantity_sequence_superlatives_are_rejected(self):
        """Verify questions with target vocabulary emit 0 nodes (never leak into knowledge graph)."""
        interrogative_samples = [
            "Which celestial body maintains an axial tilt of 23.5 degrees?",
            "Does Mars have an axial inclination of 25.2 degrees?",
            "Why does planetary accretion begin with refractory grains followed by volatiles?",
            "Did the Krakatoa volcanic eruption produce the loudest acoustic sound in recorded history?",
            "Which solar event emitted the highest energetic proton flux of the solar cycle?",
            "Can a collapsed caldera possess a depth of 1200 meters?",
        ]
        for q in interrogative_samples:
            nodes = self.extractor.extract(q)
            self.assertEqual(
                len(nodes), 0,
                f"Adversarial failure: Question leaked as factual knowledge node! Question: '{q}' -> nodes: {nodes}"
            )

    def test_incomplete_syntactic_fragments_are_rejected(self):
        """Verify incomplete fragments lacking required syntactic components emit 0 nodes."""
        fragment_samples = [
            "maintains an axial tilt of 23.5 degrees.",
            "produced the loudest acoustic sound in",
            "possesses an equatorial radius of",
            "exhibits a depth of",
            "has an axial inclination of",
        ]
        for frag in fragment_samples:
            nodes = self.extractor.extract(frag)
            self.assertEqual(
                len(nodes), 0,
                f"Adversarial failure: Incomplete fragment extracted as valid node! Fragment: '{frag}' -> nodes: {nodes}"
            )

    def test_plural_subject_verb_quantity_extractions(self):
        """Verify plural subject-verb forms (maintain, exhibit, have) extract as quantity."""
        plural_samples = [
            ("Terrestrial planets maintain an axial tilt of 25 degrees.", "Terrestrial planets", 25.0),
            ("Oceanic basins exhibit a depth of 4000 meters.", "Oceanic basins", 4000.0),
            ("Continental cratons have a thickness of 150 kilometres.", "Continental cratons", 150.0),
        ]
        for s, ent, val in plural_samples:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Failed plural quantity extraction for: '{s}'")
            node = nodes[0]
            self.assertEqual(canonicalize_intent(node.intent_type), "quantity")
            self.assertIn(ent.lower(), node.primary_entity.lower())
            self.assertIsNotNone(node.quantitative_data)
            self.assertAlmostEqual(node.quantitative_data["value"], val, places=1)

    def test_boundary_plural_possess_regex_limitation(self):
        """Documents empirical boundary condition: singular 'possesses' succeeds, but plural
        'possess' fails due to regex token 'possesses?' matching 'possesse' rather than 'possess'."""
        # Singular form succeeds:
        s_singular = "The oceanic crust possesses a thickness of 7 kilometres."
        nodes_sing = self.extractor.extract(s_singular)
        self.assertGreaterEqual(len(nodes_sing), 1)
        self.assertEqual(canonicalize_intent(nodes_sing[0].intent_type), "quantity")

        # Plural form 'possess' currently returns 0 nodes due to line 738 'possesses?' token:
        s_plural = "Atmospheric layers possess a thickness of 20 kilometres."
        nodes_plural = self.extractor.extract(s_plural)
        self.assertEqual(
            len(nodes_plural), 0,
            "Documented boundary: 'possesses?' regex token requires trailing 'e', failing plural 'possess'"
        )

    def test_boundary_terminal_preposition_by_fragment_limitation(self):
        """Documents empirical boundary condition: terminal 'by' is not included in
        NoiseFilterGate.NOISE_PATTERNS['syntactic_fragment'] (line 545), allowing trailing 'followed by'
        to match Pattern 6 with an empty predicate."""
        s_frag_by = "begins with gravitational collapse followed by"
        # Noise gate currently misses trailing 'by':
        gate_verdict = NoiseFilterGate.audit(s_frag_by)
        self.assertIsNone(
            gate_verdict,
            "Documented boundary: 'by' omitted from terminal preposition list in NoiseFilterGate line 545"
        )
        nodes = self.extractor.extract(s_frag_by)
        self.assertGreaterEqual(
            len(nodes), 1,
            "Documented boundary: Pattern 6 consumes trailing 'followed by' without required subsequent object"
        )

    def test_multi_token_proper_noun_subjects_in_quantity_and_superlatives(self):
        """Verify multi-token capitalized proper nouns cleanly pass noise gating and extract."""
        multi_token_samples = [
            ("The James Webb Space Telescope possesses an equatorial radius of 10 meters.", "quantity", "James Webb Space Telescope"),
            ("The Very Large Array Radio Telescope produced the highest angular resolution in radio astronomy.", "attribute", "Very Large Array Radio Telescope"),
        ]
        for s, expected_intent, ent in multi_token_samples:
            nodes = self.extractor.extract(s)
            self.assertGreaterEqual(len(nodes), 1, f"Multi-token proper noun falsely rejected: '{s}'")
            node = nodes[0]
            self.assertEqual(canonicalize_intent(node.intent_type), expected_intent)
            self.assertIn(ent.lower(), node.primary_entity.lower())


if __name__ == "__main__":
    unittest.main()

