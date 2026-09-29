#!/usr/bin/env python3
"""
tests/test_v13_challenger_m5_it2_stress.py
=========================================
Adversarial Stress Test Suite authored by challenger_m5_it2_1.

Empirically tests and verifies:
1. Whitespace, empty, single-character, and malformed options rejection.
2. Short-entity leakage rejection (Fog, Ice, Sun, Ore, Ash, Mud) with word boundary precision.
3. Distractor-to-distractor and distractor-to-correct alias collisions.
4. Banned quotation templates and repair punctuation integrity.
5. Independent Veto: 100% rejection rate across defective questions marked valid=True by generator.
6. Integrity & Generalization: zero hardcoded entity strings in repair logic, low-cardinality uniqueness.
7. End-to-end self-repair and Room DB export compliance on all adversarially flawed questions.
"""

import os
import sys
import re
import unittest
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tests.e2e.test_helpers import (
    CandidateQuestion,
    DataImporterSimulator,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.question_synthesizer import (
    OntologyRegistry,
    CategoryDefinition,
)
from v13_discovery.auditors import (
    CognitiveAuditor,
    ExamFitAuditor,
    AdversarialAuditor,
    MultiAgentAuditingGate,
    AuditReport,
    AuditViolation,
    FlawClassifier,
    QuestionRepairEngine,
    SelfRepairPipeline,
    AUTHORIZED_EXAMS,
    VALID_COGNITIVE_DEMANDS,
    BANNED_LAZY_STEM_PATTERNS,
)


class TestWhitespaceAndEmptyOptionsRejection(unittest.TestCase):
    """Stress tests option integrity: empty strings, pure whitespace, single char, missing keys, non-strings."""

    def setUp(self):
        self.auditor = AdversarialAuditor()
        self.gate = MultiAgentAuditingGate()
        self.repair_engine = QuestionRepairEngine()

    def _make_candidate(self, options: Dict[str, Any], correct_key: str = "opt_a") -> CandidateQuestion:
        cq = CandidateQuestion(
            id="q_opt_stress",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=options,
            correctAnswer=correct_key,
            explanation="Option (A) is correct. Granite is intrusive igneous.",
            distractorDissections=[],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_test"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        cq.valid = True
        return cq

    def test_empty_string_options_rejected(self):
        empty_variants = ["", "   ", "\t", "\n", "\r\n", " \t \n "]
        for empty_val in empty_variants:
            for bad_key in ["b", "c", "d"]:
                opts = {"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"}
                opts[bad_key] = empty_val
                cq = self._make_candidate(opts)
                rep = self.gate.audit(cq)
                self.assertEqual(rep.overallGate, "REJECT", f"Failed to reject option {bad_key}='{repr(empty_val)}'")
                self.assertTrue(rep.metadata["independentVetoTriggered"])
                self.assertTrue(any(f"Option '{bad_key}' is empty or whitespace" in r for r in rep.failureReasons))

    def test_single_char_option_rejected(self):
        """Single character options (< 2 chars) must be rejected."""
        opts = {"a": "Granite", "b": "X", "c": "Sandstone", "d": "Marble"}
        cq = self._make_candidate(opts)
        rep = self.gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")
        self.assertTrue(any("Option 'b' is empty or whitespace" in r for r in rep.failureReasons))

    def test_non_string_option_types_rejected(self):
        """Non-string types (None, int, dict) must trigger fatal rejection."""
        bad_types = [None, 123, 45.6, ["invalid"], {"sub": "dict"}]
        for bad_val in bad_types:
            opts = {"a": "Granite", "b": bad_val, "c": "Sandstone", "d": "Marble"}
            cq = self._make_candidate(opts)
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT", f"Failed to reject non-string type: {type(bad_val)}")
            self.assertTrue(any("Option 'b' is empty or whitespace" in r for r in rep.failureReasons))

    def test_missing_option_keys_rejected(self):
        """Option sets missing required keys ('a', 'b', 'c', 'd') must trigger fatal OPTION_COUNT."""
        incomplete_sets = [
            {"a": "Granite", "b": "Basalt", "c": "Sandstone"},  # missing d
            {"b": "Basalt", "c": "Sandstone", "d": "Marble"},    # missing a
            {"a": "Granite", "d": "Marble"},                     # missing b, c
        ]
        for opts in incomplete_sets:
            cq = self._make_candidate(opts)
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT")
            self.assertTrue(any("empty or whitespace" in r or "insufficient options" in r.lower() for r in rep.failureReasons))

    def test_repair_clears_whitespace_options(self):
        """QuestionRepairEngine must repair candidates with whitespace options into valid 4-option sets."""
        cq = self._make_candidate({"a": "Granite", "b": "   ", "c": "", "d": "\t"})
        rep = self.gate.audit(cq)
        repaired = self.repair_engine.repair(cq, rep)
        post_rep = self.gate.audit(repaired)
        self.assertEqual(post_rep.overallGate, "PASS")
        self.assertEqual(len(repaired.options), 4)
        # Repaired questions honour the locked Android contract: list of
        # {"id": "opt_<letter>", "text": "..."}
        self.assertIsInstance(repaired.options, list)
        for opt in repaired.options:
            opt_text = opt["text"]
            self.assertTrue(isinstance(opt_text, str) and len(opt_text.strip()) >= 2)


class TestShortEntityLeakageRejection(unittest.TestCase):
    """Stress tests short entity leakage (Fog, Ice, Sun, Ore, Ash, Mud)."""

    def setUp(self):
        self.gate = MultiAgentAuditingGate()
        self.repair_engine = QuestionRepairEngine()

    def test_short_entities_in_stem_rejected(self):
        test_cases = [
            ("Fog", "Why does Fog form over cold ground during clear winter nights?",
             {"a": "Fog", "b": "Mist", "c": "Haze", "d": "Smog"}),
            ("Ice", "Which solid form of precipitation is termed Ice when frozen?",
             {"a": "Ice", "b": "Rain", "c": "Sleet", "d": "Hail"}),
            ("Sun", "Which celestial star is known as the Sun in our solar system?",
             {"a": "Sun", "b": "Sirius", "c": "Proxima", "d": "Polaris"}),
            ("Ore", "Which rock deposit containing minerals is mined as an Ore?",
             {"a": "Ore", "b": "Slag", "c": "Flux", "d": "Gangue"}),
            ("Ash", "Which fine volcanic particulate matter is termed Ash after eruption?",
             {"a": "Ash", "b": "Lava", "c": "Lapilli", "d": "Pumice"}),
            ("Mud", "Which fine-grained wet sediment is referred to as Mud in estuaries?",
             {"a": "Mud", "b": "Sand", "c": "Gravel", "d": "Cobble"}),
        ]
        for entity, stem, options in test_cases:
            cq = CandidateQuestion(
                id=f"leak_{entity.lower()}",
                stem=stem,
                options=options,
                correctAnswer="opt_a",
                explanation=f"{entity} is correct.",
                distractorDissections=[],
                provenance={"intentType": "definition", "knowledgeNodeId": f"kn_{entity.lower()}", "primaryEntity": entity},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            cq.valid = True
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT", f"Short entity '{entity}' leakage was NOT rejected in stem: '{stem}'")
            self.assertTrue(rep.metadata["independentVetoTriggered"])
            self.assertTrue(any("stem leakage" in r.lower() for r in rep.failureReasons))

            # Verify repair clears leakage and passes gate
            repaired = self.repair_engine.repair(cq, rep)
            post_rep = self.gate.audit(repaired)
            self.assertEqual(post_rep.overallGate, "PASS", f"Repaired '{entity}' failed: {post_rep.failureReasons}")
            self.assertNotIn(entity.lower(), repaired.stem.lower())

    def test_case_insensitive_short_leakage(self):
        """Leakage must be detected regardless of casing (FOG, fog, Fog)."""
        stems = [
            "Why does FOG form over cold ground?",
            "Why does fog form over cold ground?",
            "Why does Fog form over cold ground?",
        ]
        for stem in stems:
            cq = CandidateQuestion(
                id="leak_fog_casing",
                stem=stem,
                options=[{'id': 'opt_a', 'text': "Fog"}, {'id': 'opt_b', 'text': "Mist"}, {'id': 'opt_c', 'text': "Haze"}, {'id': 'opt_d', 'text': "Smog"}],
                correctAnswer="opt_a",
                explanation="Fog forms over cold ground.",
                distractorDissections=[],
                provenance={},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT")
            self.assertTrue(any("stem leakage" in r.lower() for r in rep.failureReasons))

    def test_word_boundary_avoids_false_positives(self):
        """Word 'Ore' must not falsely match 'before' or 'shore'."""
        cq = CandidateQuestion(
            id="fp_ore_test",
            stem="Before modern industrial methods developed, which mineral extraction technique was utilized near the sea shore?",
            options=[{'id': 'opt_a', 'text': "Ore"}, {'id': 'opt_b', 'text': "Slag"}, {'id': 'opt_c', 'text': "Flux"}, {'id': 'opt_d', 'text': "Gangue"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        rep = self.gate.audit(cq)
        leakage_violations = [v for v in rep.violations if v.category == "STEM_LEAKAGE"]
        self.assertEqual(len(leakage_violations), 0, "False positive leakage detected on 'before' or 'shore'")

    def test_multi_word_short_token_leakage(self):
        """If correct answer is 'Iron Ore', mentioning 'ore' in stem must be caught."""
        cq = CandidateQuestion(
            id="multi_word_leak",
            stem="Which metallic resource is extracted from hematite ore deposits?",
            options=[{'id': 'opt_a', 'text': "Iron Ore"}, {'id': 'opt_b', 'text': "Copper Ore"}, {'id': 'opt_c', 'text': "Bauxite"}, {'id': 'opt_d', 'text': "Lignite"}],
            correctAnswer="opt_a",
            explanation="Iron Ore is extracted from hematite.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        rep = self.gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")
        self.assertTrue(any("stem leakage" in r.lower() for r in rep.failureReasons))


class TestDistractorAliasCollisions(unittest.TestCase):
    """Stress tests distractor-to-distractor and distractor-to-correct alias collisions."""

    def setUp(self):
        self.ontology = OntologyRegistry()
        cat = self.ontology.get_category("rock_types")
        if cat:
            cat.aliases["granite rock"] = "Granite"
            cat.aliases["plutonic granite"] = "Granite"
            cat.aliases["black basalt"] = "Basalt"
            cat.aliases["volcanic basalt"] = "Basalt"
        self.gate = MultiAgentAuditingGate(ontology=self.ontology)
        self.repair_engine = QuestionRepairEngine(ontology=self.ontology)

    def test_distractor_to_distractor_canonical_alias_collision(self):
        """Distractor 'Granite' and distractor 'Granite rock' must be rejected as SEMANTIC_AMBIGUITY."""
        cq = CandidateQuestion(
            id="q_alias_d2d_1",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Granite rock"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive igneous.",
            distractorDissections=[],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_alias1"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        rep = self.gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in rep.violations))
        self.assertTrue(any("share canonical entity or are aliases" in r for r in rep.failureReasons))

        # Test repair resolves collision cleanly
        repaired = self.repair_engine.repair(cq, rep)
        post_rep = self.gate.audit(repaired)
        self.assertEqual(post_rep.overallGate, "PASS")

    def test_distractor_to_distractor_both_aliases_collision(self):
        """Two distractors both being aliases of the same canonical entity (e.g. 'Plutonic granite' and 'Granite rock')."""
        cq = CandidateQuestion(
            id="q_alias_d2d_both",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Plutonic granite"}, {'id': 'opt_c', 'text': "Granite rock"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive igneous.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        rep = self.gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in rep.violations))
        self.assertTrue(any("share canonical entity or are aliases" in r for r in rep.failureReasons))

    def test_distractor_to_correct_alias_collision(self):
        """Distractor being an alias of correct answer must be rejected."""
        cq = CandidateQuestion(
            id="q_alias_d2c",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Black basalt"}, {'id': 'opt_c', 'text': "Granite"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive igneous.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        rep = self.gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in rep.violations))
        self.assertTrue(any("alias of correct answer" in r for r in rep.failureReasons))


class TestQuotationTemplatesAndPunctuation(unittest.TestCase):
    """Stress tests banned quotation templates and verifies clean repair without punctuation artifacts."""

    def setUp(self):
        self.gate = MultiAgentAuditingGate()
        self.repair_engine = QuestionRepairEngine()

    def test_all_lazy_patterns_rejected(self):
        patterns = [
            'What is a direct consequence of "volcanism"?',
            "What is a direct consequence of 'volcanism'?",
            'Which of the following is true regarding "tectonic plates"?',
            "Which of the following is true regarding 'tectonic plates'?",
            'Consider the following statement "Metamorphic rocks are layered"',
            "According to the passage, which river is antecedent?",
            "As stated in the text, how do oxbow lakes form?",
            "Based on the quote, identify the soil type:",
            "From the provided paragraph, which mountain range is fold?",
            "Refer to the excerpt to classify the sedimentary structure:"
        ]
        for stem in patterns:
            cq = CandidateQuestion(
                id="q_lazy",
                stem=stem,
                options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
                correctAnswer="opt_a",
                explanation="Granite is intrusive.",
                distractorDissections=[],
                provenance={},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            cq.valid = True
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT", f"Lazy pattern '{stem}' not rejected")
            self.assertTrue(rep.metadata["independentVetoTriggered"])

    def test_repair_quotation_produces_no_punctuation_glitches(self):
        """Repairing quotation stems must not produce '??', ':?', or missing closing '?'."""
        test_stems = [
            'What is a direct consequence of "continental drift"?',
            'What is a direct consequence of "plate subduction":?',
            'Which of the following is true regarding "granite formation"??',
        ]
        for stem in test_stems:
            cq = CandidateQuestion(
                id="q_repair_punct",
                stem=stem,
                options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
                correctAnswer="opt_a",
                explanation="Basalt is extrusive.",
                distractorDissections=[],
                provenance={"intentType": "cause_effect", "knowledgeNodeId": "kn_drift"},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            rep = self.gate.audit(cq)
            repaired = self.repair_engine.repair(cq, rep)

            self.assertFalse(repaired.stem.endswith("??"), f"Double question mark in: '{repaired.stem}'")
            self.assertNotIn(":?", repaired.stem, f"Colon before question mark in: '{repaired.stem}'")
            self.assertNotIn('"', repaired.stem, f"Quotes remaining in: '{repaired.stem}'")
            self.assertTrue(repaired.stem.endswith("?"), f"Missing ending question mark: '{repaired.stem}'")

            post_rep = self.gate.audit(repaired)
            self.assertEqual(post_rep.overallGate, "PASS")


class TestIndependentVetoAndRejectionRate(unittest.TestCase):
    """Verifies 100% rejection rate on defective questions marked valid=True by generator."""

    def setUp(self):
        self.gate = MultiAgentAuditingGate()

    def test_100_percent_veto_rate_across_comprehensive_matrix(self):
        """Generates 120 defective candidate questions with generator valid=True covering all flaw types."""
        defects = [
            # 1. Whitespace option
            {"stem": "Which of the following rocks is classified as intrusive igneous?",
             "options": {"a": "Granite", "b": "Basalt", "c": "   ", "d": "Marble"}, "correct": "opt_a"},
            # 2. Empty option
            {"stem": "Which of the following rocks is classified as intrusive igneous?",
             "options": {"a": "Granite", "b": "", "c": "Sandstone", "d": "Marble"}, "correct": "opt_a"},
            # 3. Short entity leakage - Fog
            {"stem": "Why does Fog form over cold ground during clear winter nights?",
             "options": {"a": "Fog", "b": "Mist", "c": "Haze", "d": "Smog"}, "correct": "opt_a"},
            # 4. Short entity leakage - Ice
            {"stem": "Which solid form of precipitation is termed Ice?",
             "options": {"a": "Ice", "b": "Rain", "c": "Sleet", "d": "Hail"}, "correct": "opt_a"},
            # 5. Short entity leakage - Sun
            {"stem": "Which star is known as the Sun in our solar system?",
             "options": {"a": "Sun", "b": "Sirius", "c": "Vega", "d": "Polaris"}, "correct": "opt_a"},
            # 6. Short entity leakage - Ore
            {"stem": "Which mineral resource is extracted as an Ore?",
             "options": {"a": "Ore", "b": "Slag", "c": "Flux", "d": "Gangue"}, "correct": "opt_a"},
            # 7. Verbatim stem leakage
            {"stem": "Why is Granite considered an intrusive igneous rock?",
             "options": {"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"}, "correct": "opt_a"},
            # 8. Quotation template
            {"stem": 'What is a direct consequence of "igneous intrusion"?',
             "options": {"a": "Batholith", "b": "Syncline", "c": "Graben", "d": "Moraine"}, "correct": "opt_a"},
            # 9. Duplicate options
            {"stem": "Which of the following rocks is classified as intrusive igneous?",
             "options": {"a": "Granite", "b": "Basalt", "c": "Granite", "d": "Marble"}, "correct": "opt_a"},
            # 10. Trivial stem (< 15 chars)
            {"stem": "What is rock?",
             "options": {"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"}, "correct": "opt_a"},
            # 11. Unsupported exam target
            {"stem": "Which of the following rocks is classified as intrusive igneous?",
             "options": {"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"}, "correct": "opt_a",
             "examTarget": "Middle-School-Quiz"},
            # 12. Informal register
            {"stem": "Hey can you tell which rock is intrusive igneous?",
             "options": {"a": "Granite", "b": "Basalt", "c": "Sandstone", "d": "Marble"}, "correct": "opt_a"},
        ]

        total_tested = 0
        veto_triggered_count = 0

        # Repeat each defect pattern 10 times with varied identifiers
        for i in range(10):
            for d in defects:
                total_tested += 1
                cq = CandidateQuestion(
                    id=f"veto_matrix_{total_tested}",
                    stem=d["stem"],
                    options=dict(d["options"]),
                    correctAnswer=d["correct"],
                    explanation="Option (A) is correct.",
                    distractorDissections=[],
                    provenance={},
                    cognitiveDemand=d.get("cognitiveDemand", "UNDERSTAND"),
                    examTarget=d.get("examTarget", "UPSC-Prelims")
                )
                cq.valid = True  # Generator claim: question is valid

                rep = self.gate.audit(cq)
                if rep.overallGate == "REJECT" and rep.metadata["independentVetoTriggered"]:
                    veto_triggered_count += 1

        self.assertEqual(total_tested, 120)
        self.assertEqual(veto_triggered_count, total_tested,
                         f"Independent veto failed! Expected 100% rejection rate, got {veto_triggered_count}/{total_tested}")


class TestCodeIntegrityAndGeneralization(unittest.TestCase):
    """Empirical verification that auditors.py contains zero hardcoded entity strings."""

    def test_zero_hardcoded_entity_strings_in_repair(self):
        auditors_file = os.path.join(REPO_ROOT, "v13_discovery", "auditors.py")
        with open(auditors_file, "r", encoding="utf-8") as f:
            code = f.read()

        # Find QuestionRepairEngine definition
        repair_idx = code.find("class QuestionRepairEngine")
        self.assertGreater(repair_idx, 0, "QuestionRepairEngine class not found")
        repair_code = code[repair_idx:]

        # Must not contain hardcoded entity names or astronomy strings in repair logic
        banned_hardcoded = [
            '"granite"', "'granite'",
            '"oxbow"', "'oxbow'",
            '"earth"', "'earth'",
            '"basalt"', "'basalt'",
            '"celestial bodies"', "'celestial bodies'",
            '"planetary astronomy"', "'planetary astronomy'",
            '"oxygen-rich atmosphere"', "'oxygen-rich atmosphere'"
        ]
        for token in banned_hardcoded:
            self.assertNotIn(token, repair_code.lower(),
                             f"Integrity failure: Hardcoded string {token} found in QuestionRepairEngine")


class TestRoomDBExportComplianceOnAdversarialRepairs(unittest.TestCase):
    """Verifies that all repaired questions conform to Room DB markdown and DataImporter parsing."""

    def setUp(self):
        self.gate = MultiAgentAuditingGate()
        self.repair_engine = QuestionRepairEngine()

    def test_repaired_questions_pass_dataimporter(self):
        flawed_questions = [
            # Flaw 1: Leakage + Whitespace option
            CandidateQuestion(
                id="f_leak_ws",
                stem="Why is Granite an intrusive igneous rock?",
                options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "   "}, {'id': 'opt_d', 'text': "Marble"}],
                correctAnswer="opt_a",
                explanation="Granite is intrusive.",
                distractorDissections=[],
                provenance={"intentType": "classification", "knowledgeNodeId": "kn_flaw1"},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            ),
            # Flaw 2: Short entity leakage Fog
            CandidateQuestion(
                id="f_fog",
                stem="Why does Fog form over cold ground?",
                options=[{'id': 'opt_a', 'text': "Fog"}, {'id': 'opt_b', 'text': "Mist"}, {'id': 'opt_c', 'text': "Haze"}, {'id': 'opt_d', 'text': "Smog"}],
                correctAnswer="opt_a",
                explanation="Fog is condensation.",
                distractorDissections=[],
                provenance={"intentType": "definition", "knowledgeNodeId": "kn_flaw2", "primaryEntity": "Fog"},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            ),
            # Flaw 3: Quotation template + punctuation
            CandidateQuestion(
                id="f_tmpl",
                stem='What is a direct consequence of "volcanism":?',
                options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
                correctAnswer="opt_a",
                explanation="Basalt forms from volcanism.",
                distractorDissections=[],
                provenance={"intentType": "cause_effect", "knowledgeNodeId": "kn_flaw3"},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            ),
        ]

        for cq in flawed_questions:
            rep = self.gate.audit(cq)
            self.assertEqual(rep.overallGate, "REJECT")
            repaired = self.repair_engine.repair(cq, rep)
            post_rep = self.gate.audit(repaired)
            self.assertEqual(post_rep.overallGate, "PASS")

            # Verify markdown formatting and DataImporter parsing
            md = repaired.to_room_markdown()
            self.assertIn("Explanation:", md)
            self.assertIn("Correct Answer:", md)
            self.assertLess(md.find("Explanation:"), md.find("Correct Answer:"))

            parsed = DataImporterSimulator.parse_markdown("# Topic\n\n## 1. Geography\n" + md)
            self.assertEqual(parsed["totalAccepted"], 1, f"Failed parse on {cq.id}: {parsed['rejections']}")


if __name__ == "__main__":
    unittest.main()
