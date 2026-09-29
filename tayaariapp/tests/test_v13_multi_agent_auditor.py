#!/usr/bin/env python3
"""
tests/test_v13_multi_agent_auditor.py
=====================================
Exhaustive Test Suite for Milestone 5:
Multi-Agent Auditing Quality Gate, Independent Veto, and Autonomous Self-Repair Pipeline.

Covers:
1. CognitiveAuditor: Depth, directive calibration, trivial stem rejection (<15 chars), enum checking.
2. ExamFitAuditor: Target exam authorization, civil service formal register, format validation.
3. AdversarialAuditor: MCQ stem leakage, quotation templates (NQ1-NQ5), option count/overlap,
   semantic ambiguity (alias collisions), stem article leakage, distractor dissections.
4. MultiAgentAuditingGate (alias MultiAgentQualityGate): Independent veto, composite scoring,
   structured AuditReport generation, batch auditing.
5. FlawClassifier & QuestionRepairEngine: Flaw clustering, targeted repair routines,
   provenance preservation, explanation formatting.
6. Real Corpus Scale Audit (>=50 Questions): Phase 1 audit, Phase 2 repair, Phase 3 regeneration,
   zero regression, and Room DB export verification via DataImporterSimulator.
"""

import os
import sys
import re
import copy
import json
import unittest
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tests.e2e.test_helpers import (
    CandidateQuestion,
    KnowledgeNode,
    DataImporterSimulator,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.question_synthesizer import (
    QuestionSynthesizer,
    OntologyRegistry,
    CategoryDefinition,
)
from v13_discovery.provenance import ProvenanceTracker, verify_provenance_chain
from v13_discovery.auditors import (
    CognitiveAuditor,
    ExamFitAuditor,
    AdversarialAuditor,
    MultiAgentAuditingGate,
    MultiAgentQualityGate,
    AuditReport,
    AuditViolation,
    AuditorResult,
    FlawClassifier,
    QuestionRepairEngine,
    SelfRepairPipeline,
    AUTHORIZED_EXAMS,
    VALID_COGNITIVE_DEMANDS,
)


class TestCognitiveAuditor(unittest.TestCase):
    """Unit tests for CognitiveAuditor validation logic."""

    def setUp(self):
        self.auditor = CognitiveAuditor()

    def test_cognitive_pass_valid_stem(self):
        cq = CandidateQuestion(
            id="q1",
            stem="In comparative physical geography, which of the following demonstrates the distinction between western and eastern peninsular drainage?",
            options=[{'id': 'opt_a', 'text': "Narmada"}, {'id': 'opt_b', 'text': "Godavari"}, {'id': 'opt_c', 'text': "Krishna"}, {'id': 'opt_d', 'text': "Mahanadi"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct. Narmada flows westward into the Arabian Sea.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="COMPARE",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "PASS")
        self.assertGreaterEqual(res.score, 0.8)
        self.assertEqual(len(res.violations), 0)

    def test_cognitive_reject_trivial_stem(self):
        cq = CandidateQuestion(
            id="q2",
            stem="What is Earth?",  # 14 chars (< 15)
            options=[{'id': 'opt_a', 'text': "Earth"}, {'id': 'opt_b', 'text': "Mars"}, {'id': 'opt_c', 'text': "Venus"}, {'id': 'opt_d', 'text': "Mercury"}],
            correctAnswer="opt_a",
            explanation="Earth is a planet.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("trivial or too short" in v.message for v in res.violations))
        self.assertLess(res.score, 0.5)

    def test_cognitive_reject_invalid_demand_enum(self):
        cq = CandidateQuestion(
            id="q3",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="INVALID_BLOOM_LEVEL",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("Unrecognized cognitive demand" in v.message for v in res.violations))

    def test_cognitive_shallow_recall_warning(self):
        cq = CandidateQuestion(
            id="q4",
            stem="What is defined as an intrusive igneous rock?",  # Shallow recall phrasing with COMPARE demand
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="COMPARE",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        # Warning only: passes overall if no fatal violations
        self.assertEqual(res.verdict, "PASS")
        self.assertTrue(any("Shallow recall" in v.message for v in res.violations))
        self.assertTrue(any(v.severity == "WARNING" for v in res.violations))
        self.assertLess(res.score, 1.0)


class TestExamFitAuditor(unittest.TestCase):
    """Unit tests for ExamFitAuditor scope, register, and format validation."""

    def setUp(self):
        self.auditor = ExamFitAuditor()

    def test_exam_fit_pass_authorized_targets(self):
        for target in ["UPSC-Prelims", "BPSC-Prelims", "SSC-CGL", "General-Competitive"]:
            cq = CandidateQuestion(
                id="q_ok",
                stem="With reference to Earth atmospheric layers, which layer contains the ozone layer?",
                options=[{'id': 'opt_a', 'text': "Stratosphere"}, {'id': 'opt_b', 'text': "Troposphere"}, {'id': 'opt_c', 'text': "Mesosphere"}, {'id': 'opt_d', 'text': "Thermosphere"}],
                correctAnswer="opt_a",
                explanation="Option (A) is correct. Stratosphere contains ozone.",
                distractorDissections=[],
                provenance={},
                cognitiveDemand="UNDERSTAND",
                examTarget=target
            )
            res = self.auditor.audit(cq)
            self.assertEqual(res.verdict, "PASS", f"Failed for {target}")
            self.assertEqual(res.score, 1.0)

    def test_exam_fit_reject_unsupported_target(self):
        cq = CandidateQuestion(
            id="q_bad",
            stem="With reference to Earth atmospheric layers, which layer contains the ozone layer?",
            options=[{'id': 'opt_a', 'text': "Stratosphere"}, {'id': 'opt_b', 'text': "Troposphere"}, {'id': 'opt_c', 'text': "Mesosphere"}, {'id': 'opt_d', 'text': "Thermosphere"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="Kindergarten-Quiz"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("unsupported" in v.message for v in res.violations))
        self.assertLess(res.score, 0.5)

    def test_exam_fit_reject_informal_register(self):
        cq = CandidateQuestion(
            id="q_informal",
            stem="Hey can you tell which rock is intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("Informal or conversational" in v.message for v in res.violations))

    def test_exam_fit_warn_unrecognized_format(self):
        cq = CandidateQuestion(
            id="q_fmt",
            stem="With reference to Earth atmospheric layers, which layer contains the ozone layer?",
            options=[{'id': 'opt_a', 'text': "Stratosphere"}, {'id': 'opt_b', 'text': "Troposphere"}, {'id': 'opt_c', 'text': "Mesosphere"}, {'id': 'opt_d', 'text': "Thermosphere"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims",
            format="Free-Text-Essay"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "PASS")
        self.assertTrue(any(v.category == "INVALID_FORMAT" for v in res.violations))


class TestAdversarialAuditor(unittest.TestCase):
    """Unit tests for AdversarialAuditor stress checks."""

    def setUp(self):
        self.auditor = AdversarialAuditor()

    def test_adversarial_catches_verbatim_stem_leakage(self):
        cq = CandidateQuestion(
            id="q_leak",
            stem="Why is Granite considered an intrusive igneous rock?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Sandstone"}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Basalt"}],
            correctAnswer="opt_a",
            explanation="Granite is intrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("stem leakage" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_token_stem_leakage(self):
        cq = CandidateQuestion(
            id="q_leak_token",
            stem="Which geological feature is formed when an Oxbow curve gets cut off?",
            options=[{'id': 'opt_a', 'text': "Oxbow lake"}, {'id': 'opt_b', 'text': "Gorge"}, {'id': 'opt_c', 'text': "Cirque"}, {'id': 'opt_d', 'text': "Moraine"}],
            correctAnswer="opt_a",
            explanation="Oxbow lake is formed.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("stem leakage" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_quotation_template(self):
        cq = CandidateQuestion(
            id="q_template",
            stem='What is a direct consequence of "Granite formation"?',
            options=[{'id': 'opt_a', 'text': "Plutonic rock"}, {'id': 'opt_b', 'text': "Sediment"}, {'id': 'opt_c', 'text': "Fossil"}, {'id': 'opt_d', 'text': "Lava"}],
            correctAnswer="opt_a",
            explanation="Explanation text.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("quotation template" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_insufficient_options(self):
        cq = CandidateQuestion(
            id="q_few_opts",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}],  # 3 options (<4)
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("insufficient options" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_duplicate_options(self):
        cq = CandidateQuestion(
            id="q_dup_opts",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Granite"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("duplicate options" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_semantic_ambiguity_alias(self):
        # Register a test alias in ontology
        ontology = OntologyRegistry()
        cat = ontology.get_category("rock_types")
        if cat:
            cat.aliases["granite rock"] = "Granite"

        auditor = AdversarialAuditor(ontology=ontology)
        cq = CandidateQuestion(
            id="q_alias",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Granite rock"}, {'id': 'opt_c', 'text': "Basalt"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any("semantic ambiguity" in v.message.lower() for v in res.violations))

    def test_adversarial_catches_terminal_article_leakage(self):
        cq = CandidateQuestion(
            id="q_art",
            stem="Which of the following intrusive rocks is an",  # Ends with 'an'
            options=[{'id': 'opt_a', 'text': "Igneous rock"}, {'id': 'opt_b', 'text': "Sedimentary"}, {'id': 'opt_c', 'text': "Metamorphic"}, {'id': 'opt_d', 'text': "Volcanic"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertTrue(any(v.category == "ARTICLE_LEAKAGE" for v in res.violations))

    def test_adversarial_catches_dissection_leak_on_correct_answer(self):
        cq = CandidateQuestion(
            id="q_diss_leak",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[
                {"optionId": "opt_a", "trapType": "CONCEPT_MIX", "dissection": "Wrongly labeled correct option"}
            ],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "DISSECTION_LEAK" for v in res.violations))

    def test_adversarial_catches_empty_or_whitespace_options(self):
        """Harden check: blank or whitespace-only options must trigger FATAL OPTION_COUNT."""
        cq = CandidateQuestion(
            id="q_blank_opt",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': ""}, {'id': 'opt_c', 'text': "   "}, {'id': 'opt_d', 'text': "Basalt"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        messages = [v.message for v in res.violations]
        self.assertTrue(any("Option 'b' is empty or whitespace" in m for m in messages))
        self.assertTrue(any("Option 'c' is empty or whitespace" in m for m in messages))

    def test_adversarial_catches_short_entity_leakage(self):
        """Harden check: short 3-letter answer appearing in stem must be caught."""
        for short_ent, stem_text in [("Ice", "Which solid form of precipitation is termed Ice?"),
                                      ("Fog", "Why does Fog form over cold ground during winter?")]:
            cq = CandidateQuestion(
                id=f"q_leak_{short_ent.lower()}",
                stem=stem_text,
                options=[{'id': 'opt_a', 'text': short_ent}, {'id': 'opt_b', 'text': "Rain"}, {'id': 'opt_c', 'text': "Sleet"}, {'id': 'opt_d', 'text': "Hail"}],
                correctAnswer="opt_a",
                explanation=f"{short_ent} is precipitation.",
                distractorDissections=[],
                provenance={},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            res = self.auditor.audit(cq)
            self.assertEqual(res.verdict, "REJECT", f"Leakage of {short_ent} was not rejected")
            self.assertTrue(any(v.category == "STEM_LEAKAGE" for v in res.violations))

    def test_adversarial_catches_distractor_to_distractor_alias_collision(self):
        """Harden check: two distinct distractors sharing canonical entity must trigger FATAL SEMANTIC_AMBIGUITY."""
        ontology = OntologyRegistry()
        cat = ontology.get_category("rock_types")
        if cat:
            cat.aliases["granite rock"] = "Granite"

        auditor = AdversarialAuditor(ontology=ontology)
        cq = CandidateQuestion(
            id="q_dist_alias",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Granite rock"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in res.violations))
        self.assertTrue(any("share canonical entity or are aliases" in v.message for v in res.violations))


class TestMultiAgentQualityGate(unittest.TestCase):
    """Unit tests for MultiAgentQualityGate veto and scoring aggregation."""

    def setUp(self):
        self.gate = MultiAgentQualityGate()

    def test_unanimous_pass_produces_pass(self):
        cq = CandidateQuestion(
            id="q_clean",
            stem="Which of the following atmospheric layers is characterized by the highest temperature gradient and radio wave propagation?",
            options=[{'id': 'opt_a', 'text': "Thermosphere"}, {'id': 'opt_b', 'text': "Troposphere"}, {'id': 'opt_c', 'text': "Stratosphere"}, {'id': 'opt_d', 'text': "Mesosphere"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct. Thermosphere reflects radio waves.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Troposphere is weather layer."},
                {"optionId": "opt_c", "trapType": "FACT_DISTORTION", "dissection": "Stratosphere holds ozone."},
                {"optionId": "opt_d", "trapType": "FAMILIARITY_TRAP", "dissection": "Mesosphere is coldest layer."}
            ],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        self.assertEqual(report.cognitiveVerdict, "PASS")
        self.assertEqual(report.examFitVerdict, "PASS")
        self.assertEqual(report.adversarialVerdict, "PASS")
        self.assertEqual(report.overallGate, "PASS")
        self.assertEqual(len(report.failureReasons), 0)
        self.assertGreaterEqual(report.scores["composite"], 0.8)
        self.assertFalse(report.metadata["independentVetoTriggered"])

    def test_independent_veto_rejects_generator_valid_question(self):
        cq = CandidateQuestion(
            id="q_veto",
            stem="Why is Granite considered an intrusive igneous rock?",  # Leakage flaw
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Sandstone"}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Basalt"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        cq.valid = True  # Generator claimed valid
        report = self.gate.audit(cq)
        self.assertEqual(report.overallGate, "REJECT")
        self.assertEqual(report.adversarialVerdict, "REJECT")
        self.assertTrue(report.metadata["independentVetoTriggered"])

    def test_composite_score_computation(self):
        cq = CandidateQuestion(
            id="q_scored",
            stem="Which of the following rocks is classified as intrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        self.assertEqual(report.overallGate, "PASS")
        expected = round(0.30 * report.scores["cognitive"] + 0.30 * report.scores["exam_fit"] + 0.25 * report.scores["adversarial"] + 0.15 * report.scores["semantic_coherence"], 3)
        self.assertAlmostEqual(report.scores["composite"], expected, places=2)

    def test_audit_batch(self):
        cqs = [
            CandidateQuestion(
                id=f"q_batch_{i}",
                stem=f"With reference to physical geography, which feature corresponds to item {i}?",
                options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Shale"}, {'id': 'opt_d', 'text': "Sandstone"}],
                correctAnswer="opt_a",
                explanation="Option (A) is correct.",
                distractorDissections=[],
                provenance={},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            for i in range(5)
        ]
        reports = self.gate.audit_batch(cqs)
        self.assertEqual(len(reports), 5)
        for r in reports:
            self.assertEqual(r.overallGate, "PASS")


class TestFlawClassifierAndQuestionRepairEngine(unittest.TestCase):
    """Unit tests for flaw classification, systemic repair engine, and provenance integrity."""

    def setUp(self):
        self.repair_engine = QuestionRepairEngine()
        self.gate = MultiAgentQualityGate()

    def test_flaw_clustering(self):
        cq = CandidateQuestion(
            id="q_multi_flaw",
            stem='What is a direct consequence of "Granite"?',  # Template + Leakage
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}],  # Option count
            correctAnswer="opt_a",
            explanation="Granite is intrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="Unsupported-Exam"  # Exam target
        )
        report = self.gate.audit(cq)
        clusters = FlawClassifier.classify(report)
        self.assertIn("TEMPLATE", clusters)
        self.assertIn("LEAKAGE", clusters)
        self.assertIn("OPTION_COUNT", clusters)
        self.assertIn("UNSUPPORTED_EXAM", clusters)

    def test_repair_leakage_and_template(self):
        cq = CandidateQuestion(
            id="q_repair_1",
            stem='What is a direct consequence of "Granite"?',
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Sandstone"}, {'id': 'opt_d', 'text': "Marble"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct. Granite is an intrusive rock.",
            distractorDissections=[],
            provenance={"intentType": "attribute", "knowledgeNodeId": "kn_101"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        repaired = self.repair_engine.repair(cq, report)

        post_report = self.gate.audit(repaired)
        self.assertEqual(post_report.overallGate, "PASS")
        self.assertNotIn("Granite", repaired.stem)
        self.assertNotIn('"', repaired.stem)
        self.assertEqual(repaired.provenance["knowledgeNodeId"], "kn_101")

    def test_repair_trivial_stem_and_options(self):
        cq = CandidateQuestion(
            id="q_repair_2",
            stem="What is Earth?",  # Trivial
            options=[{'id': 'opt_a', 'text': "Earth"}, {'id': 'opt_b', 'text': "Mars"}],  # < 4 options
            correctAnswer="opt_a",
            explanation="Option (A) is correct.",
            distractorDissections=[],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_202"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        repaired = self.repair_engine.repair(cq, report)

        post_report = self.gate.audit(repaired)
        self.assertEqual(post_report.overallGate, "PASS")
        self.assertGreaterEqual(len(repaired.stem), 15)
        self.assertEqual(len(repaired.options), 4)
        self.assertEqual(repaired.provenance["knowledgeNodeId"], "kn_202")

    def test_repair_low_cardinality_category_options_are_strictly_unique(self):
        """Harden check: low cardinality category must not duplicate siblings across options."""
        custom_ont = OntologyRegistry()
        custom_ont.register_category(CategoryDefinition(
            category_id="binary_stars",
            domain="astronomy",
            display_name="Binary Stars",
            entity_type="PROPER_NOUN",
            grammatical_number="SINGULAR",
            members=["Sirius A", "Sirius B"],
            descriptions={},
            aliases={},
            default_traps=[]
        ))
        engine = QuestionRepairEngine(ontology=custom_ont)
        cq = CandidateQuestion(
            id="q_low_card",
            stem="Which star is part of a binary system?",
            options=[{'id': 'opt_a', 'text': "Sirius A"}, {'id': 'opt_b', 'text': "Sirius B"}],
            correctAnswer="opt_a",
            explanation="Sirius A is a binary star.",
            distractorDissections=[],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_bin"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        repaired = engine.repair(cq, report)

        self.assertEqual(len(repaired.options), 4)
        # Repaired questions must honour the locked Android contract:
        # list of {"id": "opt_<letter>", "text": "..."}
        self.assertIsInstance(repaired.options, list)
        self.assertEqual(
            [o["id"] for o in repaired.options],
            ["opt_a", "opt_b", "opt_c", "opt_d"],
        )
        self.assertEqual(repaired.correctAnswer, "opt_a")
        opt_values = [o["text"] for o in repaired.options]
        self.assertEqual(len(set(v.lower() for v in opt_values)), 4, f"Options not unique: {opt_values}")

    def test_repair_preserves_domain_coherence_on_rock_candidate(self):
        """Integrity check: rock question with trivial stem 'What is Earth?' must not hallucinate astronomy."""
        cq = CandidateQuestion(
            id="q_coherence_rock",
            stem="What is Earth?",  # Injected trivial stem
            options=[{'id': 'opt_a', 'text': "Sandstone"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Shale"}, {'id': 'opt_d', 'text': "Granite"}],
            correctAnswer="opt_b",
            explanation="Basalt is an extrusive igneous rock.",
            distractorDissections=[],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_rock_2"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        repaired = self.repair_engine.repair(cq, report)

        # Must NOT contain hardcoded astronomy or celestial strings
        self.assertNotIn("planetary astronomy", repaired.stem.lower())
        self.assertNotIn("celestial bodies", repaired.stem.lower())
        self.assertNotIn("oxygen-rich atmosphere", repaired.stem.lower())
        # Must pass audit gate cleanly
        post_report = self.gate.audit(repaired)
        self.assertEqual(post_report.overallGate, "PASS")

    def test_repair_quotation_template_no_double_punctuation(self):
        """Harden check: quotation template stripping must never leave double punctuation like ?? or trailing colons."""
        cq = CandidateQuestion(
            id="q_tmpl_punct",
            stem='What is a direct consequence of "solar energy"?',
            options=[{'id': 'opt_a', 'text': "Photovoltaic effect"}, {'id': 'opt_b', 'text': "Erosion"}, {'id': 'opt_c', 'text': "Sedimentation"}, {'id': 'opt_d', 'text': "Volcanism"}],
            correctAnswer="opt_a",
            explanation="Solar energy drives photovoltaic effects.",
            distractorDissections=[],
            provenance={"intentType": "cause_effect", "knowledgeNodeId": "kn_solar"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        report = self.gate.audit(cq)
        repaired = self.repair_engine.repair(cq, report)

        self.assertFalse(repaired.stem.endswith("??"), f"Double question mark in: {repaired.stem}")
        self.assertNotIn(":?", repaired.stem, f"Trailing colon before question mark in: {repaired.stem}")
        self.assertTrue(repaired.stem.endswith("?"))
        post_report = self.gate.audit(repaired)
        self.assertEqual(post_report.overallGate, "PASS")


class TestRealCorpusScaleAuditAndRegeneration(unittest.TestCase):
    """End-to-End Scale Test: Audits >=50 Real Corpus Questions and Executes Autonomous Regeneration Cycle."""

    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        synthesizer = QuestionSynthesizer()
        cls.raw_candidates = synthesizer.synthesize_from_corpus(corpus_path, min_questions=50)
        cls.pipeline = SelfRepairPipeline()

    def test_scale_generation_and_regeneration_cycle(self):
        self.assertGreaterEqual(len(self.raw_candidates), 50, "Must synthesize >=50 questions from real corpus")

        # Deep-copy candidates to safely inject flaw test slice
        flawed_candidates = [copy.deepcopy(c) for c in self.raw_candidates]

        # Inject leakage flaw into candidate 0
        flawed_candidates[0].stem = "Why is Granite an intrusive rock?"
        flawed_candidates[0].options = [{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Shale"}]
        flawed_candidates[0].correctAnswer = "opt_a"

        # Inject quotation template flaw into candidate 1
        flawed_candidates[1].stem = 'What is a direct consequence of "solar energy"?'

        # Inject trivial stem flaw into candidate 2
        flawed_candidates[2].stem = "What is Earth?"

        # Inject unsupported exam target into candidate 3
        flawed_candidates[3].examTarget = "Kindergarten-Quiz"

        # Execute full 3-phase autonomous cycle
        results = self.pipeline.run_cycle(flawed_candidates)

        initial = results["initial_metrics"]
        final = results["final_metrics"]

        # Phase 1 verification
        self.assertGreater(initial["failed"], 0, "Phase 1 must catch injected and raw flaws")
        self.assertIn("LEAKAGE", initial["flaw_clusters"])
        self.assertIn("TEMPLATE", initial["flaw_clusters"])
        self.assertIn("TRIVIAL_STEM", initial["flaw_clusters"])
        self.assertIn("UNSUPPORTED_EXAM", initial["flaw_clusters"])

        # Phase 3 verification
        self.assertEqual(final["failed"], 0, "Phase 3 must achieve 0 failures post-repair")
        self.assertEqual(final["pass_rate"], 1.0, "Pass rate post-regeneration must be 100%")
        self.assertGreater(final["improvement_pct"], 0.0, "Improvement % must be strictly positive")

        # Room DB Export Verification on all regenerated questions
        for q in results["regenerated_questions"]:
            md = q.to_room_markdown()
            self.assertIn("Explanation:", md)
            self.assertIn("Correct Answer:", md)
            # Ensure Explanation strictly precedes Correct Answer inside code fence
            exp_pos = md.find("Explanation:")
            ans_pos = md.find("Correct Answer:")
            self.assertLess(exp_pos, ans_pos, "Explanation: must precede Correct Answer: for Room DB regex")

            parsed = DataImporterSimulator.parse_markdown("# Header\n\n## 1. Physical Geography\n" + md)
            self.assertEqual(parsed["totalAccepted"], 1, f"Failed DataImporter parse: {parsed['rejections']}")


if __name__ == "__main__":
    unittest.main()
