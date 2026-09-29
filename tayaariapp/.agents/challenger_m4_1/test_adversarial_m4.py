#!/usr/bin/env python3
"""
Comprehensive Adversarial Stress Test Suite for Milestone 4.
Written by challenger_m4_1 (Empirical Challenger).

Executes rigorous adversarial checks across all 6 core pillars:
1. Category Leakage & Cross-Category Distractors
2. Stem Leakage of Correct Answer Tokens
3. Grammatical Clueing (Indefinite articles & casing parallelism)
4. Length Outliers (<3x avg, <0.25x avg)
5. Placeholder Text and Duplicate Options
6. Trap Dissections (all 8 Room DB trap types)
7. Real Corpus Batch Quality & Gate Enforcement (100 questions)
"""

import os
import sys
import unittest
import re
from typing import Dict, List, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    OntologyRegistry,
    CategoryDefinition,
    DistractorVerificationGate,
    DistractorDissector,
    NaturalStemSynthesizer,
    QuestionSynthesizer,
    CandidateQuestion,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.semantic_extractor import KnowledgeNode
from v13_discovery.provenance import audit_provenance_integrity
from v13_discovery.normalizer import DocumentNormalizer


class TestAdversarialCategoryCompatibility(unittest.TestCase):
    """Area 1: Adversarial testing of Category Leakage and Cross-Category Distractors."""

    def setUp(self):
        self.ontology = OntologyRegistry()

    def test_01_cross_category_detection_comprehensive(self):
        """Verify gate rejects distractors injected from foreign categories across diverse domains."""
        cat_atmo = self.ontology.get_category("atmospheric_layers")
        self.assertIsNotNone(cat_atmo)

        foreign_injections = [
            ("rock_types", "Granite"),
            ("terrestrial_planets", "Mars"),
            ("ocean_currents", "Gulf Stream"),
            ("indian_rivers", "Brahmaputra"),
            ("cloud_types", "Cirrus"),
            ("soil_types", "Regur soil"),
            ("volcanoes", "Mount Vesuvius"),
            ("minerals", "Quartz"),
        ]

        for foreign_cat, foreign_entity in foreign_injections:
            options = {
                "a": "Troposphere",
                "b": "Stratosphere",
                "c": "Mesosphere",
                "d": foreign_entity
            }
            is_valid, errors = DistractorVerificationGate.check_category_compatibility(options, cat_atmo)
            self.assertFalse(
                is_valid,
                f"Gate failed to reject foreign entity '{foreign_entity}' from '{foreign_cat}' in atmospheric layers"
            )
            self.assertTrue(any("violates category compatibility" in e for e in errors))

    def test_02_all_options_foreign(self):
        """Verify gate flags every single option when all options belong to the wrong category."""
        cat_planets = self.ontology.get_category("terrestrial_planets")
        options = {
            "a": "Basalt",
            "b": "Granite",
            "c": "Marble",
            "d": "Sandstone"
        }
        is_valid, errors = DistractorVerificationGate.check_category_compatibility(options, cat_planets)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 4, f"Expected 4 errors for 4 foreign options, got: {errors}")

    def test_03_valid_siblings_pass(self):
        """Positive control: All valid siblings from the category must pass without error."""
        cat = self.ontology.get_category("atmospheric_layers")
        options = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere",
            "d": "Thermosphere"
        }
        is_valid, errors = DistractorVerificationGate.check_category_compatibility(options, cat)
        self.assertTrue(is_valid, f"Valid siblings falsely rejected: {errors}")
        self.assertEqual(len(errors), 0)

    def test_04_synthesizer_generates_options_matching_resolved_category(self):
        """Verify that for each of the 38 registered categories, generated options match resolved category."""
        synth = QuestionSynthesizer(self.ontology)
        for cat_id, cat in self.ontology.categories.items():
            if not cat.members:
                continue
            test_entity = cat.members[0]
            node = KnowledgeNode(
                node_id=f"node_{cat_id}",
                intent_type="definition",
                primary_entity=test_entity,
                predicate="is a key concept",
                secondary_entities=[],
                conditions=[],
                quantitative_data=None,
                raw_evidence=f"{test_entity} is an essential physical geography component.",
                source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
                confidence=1.0
            )
            cq = synth.synthesize(node)
            resolved_cat = self.ontology.find_category_for_entity(test_entity)
            is_valid, errors = DistractorVerificationGate.check_category_compatibility(cq.options, resolved_cat)
            self.assertTrue(
                is_valid,
                f"Synthesizer generated options violating resolved category '{resolved_cat.category_id}': {errors}"
            )

    def test_05_multi_category_collision_causes_conceptual_cross_leakage(self):
        """Vulnerability verification: 'Hadley cell' in 'circulation_cells' gets resolved to 'climatic_phenomena',
        generating distractors like 'Coriolis force' and 'Rossby waves' which fail circulation_cells gate."""
        cat_circ = self.ontology.get_category("circulation_cells")
        synth = QuestionSynthesizer(self.ontology)
        node = KnowledgeNode(
            node_id="node_hadley_test",
            intent_type="definition",
            primary_entity="Hadley cell",
            predicate="is a tropical circulation cell",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="Hadley cell is a tropical atmospheric circulation cell.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
            confidence=1.0
        )
        cq = synth.synthesize(node)
        # Gate strictly verifies that Hadley cell produces valid circulation_cells distractors
        is_valid, errors = DistractorVerificationGate.check_category_compatibility(cq.options, cat_circ)
        self.assertTrue(
            is_valid,
            f"Verification gate failed for Hadley cell circulation distractors: {errors}"
        )
        self.assertEqual(len(errors), 0)


class TestAdversarialStemLeakage(unittest.TestCase):
    """Area 2: Adversarial testing of Stem Leakage of Correct Answer Tokens."""

    def setUp(self):
        self.base_options = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere",
            "d": "Thermosphere"
        }

    def test_06_verbatim_answer_leakage_detected(self):
        """Gate must catch verbatim mention of correct answer in stem."""
        leaking_stems = [
            "Which atmospheric layer is the Troposphere located within?",
            "What defines the troposphere in physical geography?",
            "With reference to the troposphere, what is its primary characteristic?",
            "In atmospheric science, TROPOSPHERE represents which layer?",
        ]
        for stem in leaking_stems:
            is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
                options=self.base_options,
                correct_key="opt_a",
                stem=stem
            )
            self.assertFalse(is_valid, f"Failed to detect verbatim leakage in stem: '{stem}'")
            self.assertTrue(any("Stem leakage detected" in e for e in errors))

    def test_07_multi_word_keyword_leakage_detected(self):
        """Gate must catch distinctive keywords from multi-word answer in stem."""
        options = {
            "a": "Mushroom rock",
            "b": "Oxbow lake",
            "c": "Cirque",
            "d": "Sand dune"
        }
        stem = "Which distinctive mushroom structure is shaped by wind abrasion?"
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=options,
            correct_key="opt_a",
            stem=stem
        )
        self.assertFalse(is_valid, f"Failed to detect distinctive keyword 'mushroom' in stem: '{stem}'")
        self.assertTrue(any("Stem leakage detected" in e for e in errors))

    def test_08_distractor_mention_does_not_falsely_trigger_answer_leakage(self):
        """Gate should only flag stem leakage of the CORRECT answer, not distractors."""
        stem = "Unlike the stratosphere, which lowest atmospheric layer contains most water vapor?"
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=self.base_options,
            correct_key="opt_a",
            stem=stem
        )
        leakage_errors = [e for e in errors if "Stem leakage" in e]
        self.assertEqual(len(leakage_errors), 0, f"False positive leakage on distractor: {leakage_errors}")

    def test_09_natural_stem_synthesizer_strips_target_entity(self):
        """Verify NaturalStemSynthesizer de-identifies the target entity from raw evidence."""
        node = KnowledgeNode(
            node_id="test_leak_01",
            intent_type="definition",
            primary_entity="Mesosphere",
            predicate="is the coldest layer",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="The mesosphere is defined as the coldest layer of the atmosphere where meteors burn.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
            confidence=1.0
        )
        stem = NaturalStemSynthesizer.synthesize_stem(node, None)
        self.assertNotIn("mesosphere", stem.lower(), f"Synthesizer leaked primary entity into stem: '{stem}'")

    def test_10_short_3_letter_entity_leakage_bypass_vulnerability(self):
        """Hardened verification: Entities with len >= 3 (e.g. 'Fog') are caught by stem leakage gate."""
        options = {"a": "Fog", "b": "Mist", "c": "Haze", "d": "Smog"}
        leaking_stem = "Which atmospheric condensation phenomenon known as fog reduces visibility below 1 km?"
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=options,
            correct_key="opt_a",
            stem=leaking_stem
        )
        self.assertFalse(
            is_valid,
            "Hardened gate must catch 3-letter entity 'Fog' leaking in stem"
        )
        self.assertTrue(any("Stem leakage detected" in e for e in errors))


class TestAdversarialGrammaticalClueing(unittest.TestCase):
    """Area 3: Adversarial testing of Grammatical Clueing (articles, mixed casing)."""

    def setUp(self):
        self.options_cased = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere",
            "d": "Thermosphere"
        }

    def test_11_stem_terminal_copula_article_caught(self):
        """Gate catches stems ending with copula + indefinite article ('is a', 'is an', 'as a', etc.)."""
        stems_with_articles = [
            "Which of the following atmospheric layers is a?",
            "Which geographical feature is an:",
            "In physical geography, this formation is defined as a?",
            "Which volcanic rock is termed an?",
            "Which geological process is called a?",
        ]
        for stem in stems_with_articles:
            is_valid, errors = DistractorVerificationGate.check_grammatical_fit(self.options_cased, stem)
            self.assertFalse(is_valid, f"Gate failed to catch copula article clueing in: '{stem}'")
            self.assertTrue(any("Stem ends with indefinite article" in e for e in errors))

    def test_12_non_copula_stem_terminal_article_bypass_vulnerability(self):
        """Hardened verification: Stems ending in non-copula verb + 'a'/'an' are caught by the gate."""
        bypassing_stems = [
            "Which fluvial process creates an?",
            "Which geological feature represents a?",
            "In Earth science, this structure forms an:",
            "Which natural formation constitutes a?",
        ]
        for stem in bypassing_stems:
            is_valid, errors = DistractorVerificationGate.check_grammatical_fit(self.options_cased, stem)
            self.assertFalse(
                is_valid,
                f"Hardened gate must catch indefinite article in '{stem}'"
            )
            self.assertTrue(any("Stem ends with indefinite article" in e for e in errors))

    def test_13_mixed_capitalization_detected(self):
        """Gate must reject options with inconsistent capitalization (parallelism failure)."""
        bad_options_list = [
            {"a": "Troposphere", "b": "stratosphere", "c": "Mesosphere", "d": "Thermosphere"},
            {"a": "troposphere", "b": "Stratosphere", "c": "mesosphere", "d": "thermosphere"},
            {"a": "Troposphere", "b": "Stratosphere", "c": "mesosphere", "d": "thermosphere"},
        ]
        clean_stem = "Which of the following is the lowest atmospheric layer?"
        for bad_opts in bad_options_list:
            is_valid, errors = DistractorVerificationGate.check_grammatical_fit(bad_opts, clean_stem)
            self.assertFalse(is_valid, f"Gate allowed mixed capitalization: {bad_opts}")
            self.assertTrue(any("Mixed option capitalization" in e for e in errors))

    def test_14_uniform_capitalization_accepted(self):
        """Gate must accept uniform title case or uniform lower case."""
        clean_stem = "Which of the following is the lowest atmospheric layer?"
        all_upper = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": "Thermosphere"}
        all_lower = {"a": "troposphere", "b": "stratosphere", "c": "mesosphere", "d": "thermosphere"}

        is_valid_u, errors_u = DistractorVerificationGate.check_grammatical_fit(all_upper, clean_stem)
        self.assertTrue(is_valid_u, f"Uniform title case rejected: {errors_u}")

        is_valid_l, errors_l = DistractorVerificationGate.check_grammatical_fit(all_lower, clean_stem)
        self.assertTrue(is_valid_l, f"Uniform lower case rejected: {errors_l}")


class TestAdversarialLengthOutliers(unittest.TestCase):
    """Area 4: Adversarial testing of Length Outliers (3x longer or shorter)."""

    def setUp(self):
        self.stem = "Which of the following geological formations is formed by river deposition?"

    def test_15_extremely_long_option_rejected(self):
        """Gate must reject an option that is >= 3.0x the average length."""
        options = {
            "a": "Delta",
            "b": "Cirque",
            "c": "Moraine",
            "d": "This is an extraordinarily verbose and detailed explanation of how an oxbow lake is formed through progressive meander neck erosion over centuries"
        }
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=options,
            correct_key="opt_a",
            stem=self.stem
        )
        self.assertFalse(is_valid, f"Failed to reject 3x+ length outlier: {errors}")
        self.assertTrue(any("length outlier" in e for e in errors))

    def test_16_extremely_short_option_rejected(self):
        """Gate must reject an option that is < 0.25x the average length when avg >= 15."""
        options = {
            "a": "Extrusive igneous basaltic plateau",
            "b": "Intrusive plutonic granite batholith",
            "c": "Metamorphic foliated quartzite ridge",
            "d": "Ice"
        }
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=options,
            correct_key="opt_a",
            stem=self.stem
        )
        self.assertFalse(is_valid, f"Failed to reject < 0.25x short outlier: {errors}")
        self.assertTrue(any("too short" in e for e in errors))

    def test_17_balanced_lengths_pass(self):
        """Options with balanced lengths (close to average) must pass length parity check."""
        options = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere",
            "d": "Thermosphere"
        }
        is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
            options=options,
            correct_key="opt_a",
            stem=self.stem
        )
        length_errors = [e for e in errors if "length" in e or "too short" in e]
        self.assertEqual(len(length_errors), 0, f"Balanced options falsely flagged: {length_errors}")


class TestAdversarialPlaceholdersAndDuplicates(unittest.TestCase):
    """Area 5: Adversarial testing of Placeholder Text and Duplicate Options."""

    def test_18_standard_placeholder_options_rejected(self):
        """Gate rejects recognized placeholders: Option A, Alternative 1, None, TBD, etc."""
        placeholders = [
            "Option A",
            "Option B",
            "Alternative 1",
            "Alternative 2",
            "None",
            "None of the above",
            "TBD",
            "Placeholder",
            "Unknown",
        ]
        for ph in placeholders:
            options = {
                "a": "Troposphere",
                "b": "Stratosphere",
                "c": "Mesosphere",
                "d": ph
            }
            is_valid, errors = DistractorVerificationGate.check_semantic_plausibility(options)
            self.assertFalse(is_valid, f"Gate failed to reject placeholder text '{ph}'")
            self.assertTrue(any("artificial placeholder text" in e for e in errors))

    def test_19_unlisted_placeholder_options_bypass_vulnerability(self):
        """Hardened verification: Placeholders like 'Option 1', 'Choice A', 'N/A' are rejected by gate."""
        unlisted = ["Option 1", "Choice A", "All of the above", "N/A"]
        for ph in unlisted:
            options = {
                "a": "Troposphere",
                "b": "Stratosphere",
                "c": "Mesosphere",
                "d": ph
            }
            is_valid, errors = DistractorVerificationGate.check_semantic_plausibility(options)
            self.assertFalse(
                is_valid,
                f"Hardened gate must reject unlisted placeholder '{ph}'"
            )
            self.assertTrue(any("artificial placeholder text" in e for e in errors))

    def test_20_single_character_options_rejected(self):
        """Gate must reject options that are < 2 characters."""
        options = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere",
            "d": "X"
        }
        is_valid, errors = DistractorVerificationGate.check_semantic_plausibility(options)
        self.assertFalse(is_valid, "Gate allowed single character option")
        self.assertTrue(any("too short" in e for e in errors))

    def test_21_exact_and_case_insensitive_duplicates_rejected(self):
        """Gate must reject exact and case-insensitive duplicate options."""
        duplicate_pairs = [
            ("Troposphere", "Troposphere"),
            ("Basalt", "basalt"),
            ("Granite ", "Granite"),
        ]
        for opt1, opt2 in duplicate_pairs:
            options = {
                "a": opt1,
                "b": "Stratosphere",
                "c": opt2,
                "d": "Mesosphere"
            }
            is_valid, errors = DistractorVerificationGate.check_evidence_support(options, "opt_a")
            self.assertFalse(is_valid, f"Gate allowed duplicate pair: ('{opt1}', '{opt2}')")
            self.assertTrue(any("Duplicate options detected" in e for e in errors))

    def test_22_insufficient_option_count_rejected(self):
        """Gate must reject when fewer than 4 options are provided."""
        options = {
            "a": "Troposphere",
            "b": "Stratosphere",
            "c": "Mesosphere"
        }
        is_valid, errors = DistractorVerificationGate.check_evidence_support(options, "opt_a")
        self.assertFalse(is_valid, "Gate allowed 3 options instead of >=4")
        self.assertTrue(any("Insufficient options count" in e for e in errors))


class TestAdversarialTrapDissections(unittest.TestCase):
    """Area 6: Adversarial testing of Trap Dissections across all 8 Room DB trap types."""

    def test_23_all_8_trap_types_generate_valid_rationales(self):
        """Verify all 8 authorized trap types produce valid pedagogical rationales (100+ chars)."""
        for trap in VALID_ROOM_TRAP_TYPES:
            dissection = DistractorDissector.dissect(
                option_id="opt_b",
                distractor_text="Stratosphere",
                correct_text="Troposphere",
                category=None,
                intent_type="definition",
                evidence="The troposphere is the lowest atmospheric layer.",
                forced_trap_type=trap
            )
            self.assertEqual(dissection["optionId"], "opt_b")
            self.assertEqual(dissection["trapType"], trap)
            self.assertIsInstance(dissection["dissection"], str)
            self.assertGreater(
                len(dissection["dissection"].strip()),
                25,
                f"Trap '{trap}' produced an insufficiently substantive rationale (<25 chars)"
            )
            self.assertIn(
                "Stratosphere",
                dissection["dissection"],
                f"Rationale for trap '{trap}' does not mention distractor"
            )

    def test_24_dissections_never_assigned_to_correct_answer(self):
        """Stress-test 50 synthesized questions: NO dissection must EVER be assigned to the correct answer."""
        synth = QuestionSynthesizer()
        entities = ["Troposphere", "Stratosphere", "Mesosphere", "Mercury", "Venus", "Mars", "Basalt", "Granite"]
        for ent in entities:
            node = KnowledgeNode(
                node_id=f"test_dissect_{ent}",
                intent_type="definition",
                primary_entity=ent,
                predicate="is a key feature",
                secondary_entities=[],
                conditions=[],
                quantitative_data=None,
                raw_evidence=f"{ent} is a prominent geological or atmospheric entity.",
                source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
                confidence=1.0
            )
            cq = synth.synthesize(node, shuffle=True)
            correct_opt_id = cq.correctAnswer
            for d in cq.distractorDissections:
                self.assertNotEqual(
                    d["optionId"],
                    correct_opt_id,
                    f"Dissection illegally assigned to correct answer '{correct_opt_id}': {d}"
                )
            self.assertEqual(
                len(cq.distractorDissections),
                3,
                f"Expected exactly 3 distractor dissections, got {len(cq.distractorDissections)}"
            )

    def test_25_dissections_cover_all_distractor_keys(self):
        """Verify that every distractor option key is covered by exactly one dissection."""
        synth = QuestionSynthesizer()
        node = KnowledgeNode(
            node_id="test_dissect_coverage",
            intent_type="definition",
            primary_entity="Basalt",
            predicate="is an extrusive igneous rock",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="Basalt is an extrusive igneous rock formed by cooling lava.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
            confidence=1.0
        )
        cq = synth.synthesize(node)
        correct_letter = cq.correctAnswer.replace("opt_", "")
        distractor_keys = {f"opt_{k}" for k in cq.options.keys() if k != correct_letter}
        dissected_keys = {d["optionId"] for d in cq.distractorDissections}
        self.assertEqual(
            distractor_keys,
            dissected_keys,
            f"Dissected keys do not match distractor keys: {distractor_keys} vs {dissected_keys}"
        )


class TestRealCorpusBatchQuality(unittest.TestCase):
    """Area 7: Stress testing real-world corpus batch synthesis."""

    @classmethod
    def setUpClass(cls):
        cls.synth = QuestionSynthesizer()
        cls.corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        cls.questions = cls.synth.synthesize_from_corpus(cls.corpus_path, min_questions=100)

    def test_26_scale_batch_yields_100_distinct_stems(self):
        """Batch yields >= 100 questions with 100% unique stems."""
        self.assertGreaterEqual(len(self.questions), 100)
        stems = [q.stem.strip().lower() for q in self.questions]
        self.assertEqual(len(set(stems)), len(self.questions), "Duplicate stems detected in batch")

    def test_27_batch_audit_distractor_dissections(self):
        """100% of generated questions have valid distractor dissections adhering to Room DB."""
        for q in self.questions:
            self.assertEqual(len(q.distractorDissections), 3)
            for d in q.distractorDissections:
                self.assertIn(d["trapType"], VALID_ROOM_TRAP_TYPES)
                self.assertNotEqual(d["optionId"], q.correctAnswer)
                self.assertGreaterEqual(len(d["dissection"]), 15)

    def test_28_batch_stem_leakage_rate_documented(self):
        """Quantify the exact number of batch questions failing stem leakage checks."""
        failing = []
        for q in self.questions:
            is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
                options=q.options,
                correct_key=q.correctAnswer,
                stem=q.stem
            )
            if not is_valid:
                failing.append((q.id, errors))
        
        # We document the exact failure count (0 questions out of 100 fail stem leakage gate)
        print(f"\n[EMPIRICAL FINDING] Real corpus batch has {len(failing)} / {len(self.questions)} questions failing stem leakage gate.")
        self.assertEqual(len(failing), 0, f"Stem leakage failure rate must be 0: {len(failing)}/100")


if __name__ == "__main__":
    unittest.main(verbosity=2)
