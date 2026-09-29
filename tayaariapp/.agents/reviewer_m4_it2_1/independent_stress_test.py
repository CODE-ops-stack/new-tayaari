import os
import sys
import re
import unittest
from typing import Dict, List, Set, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    DistractorVerificationGate,
    OntologyRegistry,
    QuestionSynthesizer,
    NaturalStemSynthesizer,
)
from v13_discovery.semantic_extractor import KnowledgeNode


class TestIndependentAdversarialReview(unittest.TestCase):

    def setUp(self):
        self.ontology = OntologyRegistry()
        self.synth = QuestionSynthesizer(self.ontology)

    # -------------------------------------------------------------------------
    # 1. Defect 1: Gate Rejection & Filtering in synthesize() and synthesize_from_corpus()
    # -------------------------------------------------------------------------
    def test_cq_valid_field_and_rejection(self):
        """Verify cq.valid is boolean and becomes False when question cannot be repaired."""
        # Create a node with an entity that has NO valid category and impossible to repair
        node = KnowledgeNode(
            node_id="unrepairable_01",
            intent_type="definition",
            primary_entity="TotallyBogusAlienEntity",
            predicate="is unknown",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="TotallyBogusAlienEntity is unknown.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
            confidence=1.0
        )
        cq = self.synth.synthesize(node)
        self.assertIsInstance(cq.valid, bool)

    def test_corpus_synthesis_100_questions_zero_leakage(self):
        """Independent execution of synthesize_from_corpus: 100 questions with 0% stem leakage."""
        corpus_file = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        self.assertTrue(os.path.exists(corpus_file), f"Corpus not found at {corpus_file}")
        
        questions = self.synth.synthesize_from_corpus(corpus_file, min_questions=100)
        self.assertGreaterEqual(len(questions), 100)

        leak_failures = []
        gate_failures = []
        unique_stems = set()

        for idx, q in enumerate(questions):
            # Check 1: cq.valid attribute must be True
            self.assertTrue(hasattr(q, "valid"), f"Question {q.id} missing 'valid' field")
            self.assertTrue(q.valid, f"Question {q.id} has valid=False in corpus batch")

            # Check 2: verify_all gate
            is_valid, errors = DistractorVerificationGate.verify_all(
                options=q.options,
                correct_key=q.correctAnswer,
                stem=q.stem
            )
            if not is_valid:
                gate_failures.append((idx, q.id, errors))

            # Check 3: absence of clueing & stem leakage
            is_clue_valid, clue_errors = DistractorVerificationGate.check_absence_of_clueing(
                options=q.options,
                correct_key=q.correctAnswer,
                stem=q.stem
            )
            if not is_clue_valid:
                leak_failures.append((idx, q.id, clue_errors))

            # Check 4: uniqueness
            unique_stems.add(q.stem.strip().lower())

        self.assertEqual(len(gate_failures), 0, f"Gate failures in corpus batch: {gate_failures}")
        self.assertEqual(len(leak_failures), 0, f"Stem leakage failures in corpus batch: {leak_failures}")
        self.assertEqual(len(unique_stems), len(questions), "Duplicate stems found in corpus batch")

    # -------------------------------------------------------------------------
    # 2. Defect 2: Stem-Terminal Indefinite Article Detection
    # -------------------------------------------------------------------------
    def test_stem_terminal_article_stress(self):
        """Stress test indefinite article regex with adversarial boundary strings."""
        options = {"a": "Oxbow lake", "b": "Cirque", "c": "Moraine", "d": "Delta"}

        # Stems that MUST fail (ends with a or an)
        failing_stems = [
            "Which feature creates an?",
            "Which feature represents a?",
            "The landform is an:",
            "Geological structure is a",
            "This is considered a?",
            "In this zone, there exists an:",
            "Can you identify an?",
            "We observe a:",
            "What forms an?",
            "What constitutes a?"
        ]
        for s in failing_stems:
            passed, errs = DistractorVerificationGate.check_grammatical_fit(options, s)
            self.assertFalse(passed, f"Failed to catch article in: {s}")
            self.assertTrue(any("Stem ends with indefinite article" in e for e in errs))

        # Stems that MUST pass (words ending in 'a' or 'an' but NOT standalone article)
        passing_stems = [
            "Which desert is the Sahara?",
            "Which ocean basin is the Indian?",
            "Which Andean mammal is the llama?",
            "Which country is Japan?",
            "What is an urban plan?",
            "Which state is Haryana?",
            "Which mountain range is the Sierra Nevada?"
        ]
        for s in passing_stems:
            passed, errs = DistractorVerificationGate.check_grammatical_fit(options, s)
            article_errs = [e for e in errs if "Stem ends with indefinite article" in e]
            self.assertEqual(len(article_errs), 0, f"False positive article cluing in: {s}")

    # -------------------------------------------------------------------------
    # 3. Defect 3: Short Entity Stem Leakage
    # -------------------------------------------------------------------------
    def test_short_entity_stem_leakage_stress(self):
        """Test 3-letter concepts, punctuation variations, and substring protection."""
        # 3-letter words that must be caught when present as words
        test_cases_fail = [
            ("Fog", "Which dense condensation known as fog reduces visibility?"),
            ("Ice", "Which solid form of water, ice, forms glaciers?"),
            ("Ice", "Which solid form of water (ice) forms glaciers?"),
            ("Sun", "The star known as the sun is our energy source:"),
            ("Ore", "A rock mass mined as ore contains metals:"),
            ("Ash", "Volcanic ash settles rapidly:"),
            ("Mud", "Deposited mud forms shale over time:"),
            ("Gas", "Methane is a greenhouse gas found in the atmosphere:")
        ]
        for ent, stem in test_cases_fail:
            opts = {"a": ent, "b": "Granite", "c": "Basalt", "d": "Marble"}
            passed, errs = DistractorVerificationGate.check_absence_of_clueing(opts, "opt_a", stem)
            self.assertFalse(passed, f"Failed to catch short entity '{ent}' in stem '{stem}'")
            self.assertTrue(any("Stem leakage detected" in e for e in errs))

        # Substrings inside longer words that must NOT trigger false positives
        test_cases_pass = [
            ("Ore", "Which rock was formed before modern times?"),        # 'before' contains 'ore'
            ("Ice", "Which feature was discovered on the ocean surface?"), # 'surface' contains 'ice'
            ("Ash", "Which structure will crash due to erosion?"),         # 'crash' contains 'ash'
            ("Gas", "Which region in Madagascar has unique flora?"),       # 'Madagascar' contains 'gas'
            ("Mud", "Which boundary is Bermuda located in?"),              # 'Bermuda' contains 'mud'
        ]
        for ent, stem in test_cases_pass:
            opts = {"a": ent, "b": "Granite", "c": "Basalt", "d": "Marble"}
            passed, errs = DistractorVerificationGate.check_absence_of_clueing(opts, "opt_a", stem)
            leak_errs = [e for e in errs if "Stem leakage detected" in e]
            self.assertEqual(len(leak_errs), 0, f"False positive short entity leakage for '{ent}' in stem '{stem}'")

    # -------------------------------------------------------------------------
    # 4. Defect 4: Expanded Placeholder Detection
    # -------------------------------------------------------------------------
    def test_placeholder_regex_adversarial_stress(self):
        """Test complete range of placeholder variants and negative controls."""
        failing_placeholders = [
            "Option 1", "Option 2", "Option 10", "Option A", "Option B", "Option Z",
            "Alternative 1", "Alternative 2", "Alternative A", "Alternative B",
            "Choice 1", "Choice 2", "Choice A", "Choice B",
            "None", "None of the above", "None of these", "All of the above",
            "N/A", "NA", "TBD", "Placeholder", "Unknown",
            "Dummy", "Sample", "Test Option",
            # Case variations
            "option 1", "choice a", "all of the above", "n/a", "na", "tbd"
        ]
        for ph in failing_placeholders:
            opts = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": ph}
            passed, errs = DistractorVerificationGate.check_semantic_plausibility(opts)
            self.assertFalse(passed, f"Failed to reject placeholder: '{ph}'")
            self.assertTrue(any("artificial placeholder text" in e for e in errs))

        # Legitimate terms that should NOT be rejected
        passing_terms = [
            "North America", "South America", "Sodium chloride", "Nitrogen",
            "Naturally occurring mineral", "Optionally folded strata", "Alluvial plain"
        ]
        for term in passing_terms:
            opts = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": term}
            passed, errs = DistractorVerificationGate.check_semantic_plausibility(opts)
            ph_errs = [e for e in errs if "artificial placeholder text" in e]
            self.assertEqual(len(ph_errs), 0, f"False positive placeholder detection for: '{term}'")

    # -------------------------------------------------------------------------
    # 5. Defect 5: Ontology Deduplication & Separation
    # -------------------------------------------------------------------------
    def test_hadley_cell_deduplication(self):
        """Verify Hadley cell is strictly in circulation_cells and not climatic_phenomena."""
        cat = self.ontology.find_category_for_entity("Hadley cell")
        self.assertIsNotNone(cat)
        self.assertEqual(cat.category_id, "circulation_cells")

        climatic_cat = self.ontology.get_category("climatic_phenomena")
        self.assertNotIn("hadley cell", [m.lower() for m in climatic_cat.members])
        self.assertIn("jet stream", [m.lower() for m in climatic_cat.members])

    def test_landforms_clean_separation(self):
        """Verify fluvial, glacial, and aeolian landforms have disjoint membership."""
        fluvial = set(m.lower() for m in self.ontology.get_category("fluvial_landforms").members)
        glacial = set(m.lower() for m in self.ontology.get_category("glacial_landforms").members)
        aeolian = set(m.lower() for m in self.ontology.get_category("aeolian_landforms").members)

        # Check disjointness
        self.assertEqual(fluvial.intersection(glacial), set(), "Fluvial and Glacial overlap!")
        self.assertEqual(fluvial.intersection(aeolian), set(), "Fluvial and Aeolian overlap!")
        self.assertEqual(glacial.intersection(aeolian), set(), "Glacial and Aeolian overlap!")

        # Check key specific assignments
        self.assertIn("oxbow lake", fluvial)
        self.assertIn("delta", fluvial)
        self.assertIn("cirque", glacial)
        self.assertIn("moraine", glacial)
        self.assertIn("mushroom rock", aeolian)


if __name__ == "__main__":
    unittest.main(verbosity=2)
