#!/usr/bin/env python3
"""
tests/test_v13_challenger_m5_it2_2_adversarial.py
=================================================
Adversarial Challenge & Stress Test Suite authored by challenger_m5_it2_2.

Rigorous empirical validation covering:
1. Scale generation & audit of >=50 questions from source-material/geography_extracted.txt.
2. Execution of SelfRepairPipeline.run_cycle across the 50+ candidates with adversarial flaw injections.
3. 100% pass clearance in Phase 3, zero hardcoded strings in outputs, and domain coherence preservation.
4. Room DB serialization: 'Explanation:' strictly precedes 'Correct Answer:' with format 'Option (X) is correct.' and zero truncation under DataImporterSimulator.
5. All distractor dissections map to 8 Room DB trap types with pedagogical rationales (>10 chars).
6. Adversarial edge cases: multiline explanations, special character options, low-cardinality sibling sets, and Room DB JSON integrity.
"""

import copy
import json
import os
import re
import sys
import unittest
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tests.e2e.test_helpers import (
    DataImporterSimulator,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    CategoryDefinition,
    DistractorDissector,
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
)


class TestRealCorpusScaleAudit50Plus(unittest.TestCase):
    """Generates 50+ questions from geography_extracted.txt and executes SelfRepairPipeline."""

    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        cls.synthesizer = QuestionSynthesizer()
        cls.raw_candidates = cls.synthesizer.synthesize_from_corpus(corpus_path, min_questions=60)
        cls.pipeline = SelfRepairPipeline()
        cls.gate = MultiAgentAuditingGate()

    def test_corpus_yield_and_diversity(self):
        """Must synthesize at least 50 valid questions from real geography corpus."""
        self.assertGreaterEqual(
            len(self.raw_candidates), 50,
            f"Expected >= 50 candidates from corpus, got {len(self.raw_candidates)}"
        )
        # Verify diversity of stems and correct answers
        unique_stems = {c.stem.strip() for c in self.raw_candidates}
        self.assertGreaterEqual(len(unique_stems), 45, "Stems must be substantially distinct")

    def test_scale_cycle_with_adversarial_flaw_battery(self):
        """Injects a 12-flaw adversarial battery into the 50+ corpus questions and executes run_cycle."""
        candidates = [copy.deepcopy(c) for c in self.raw_candidates]
        self.assertGreaterEqual(len(candidates), 50)

        # Injected Flaw 0: Direct stem leakage
        candidates[0].stem = "Why is Granite classified as an intrusive igneous rock?"
        candidates[0].options = [{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Shale"}]
        candidates[0].correctAnswer = "opt_a"

        # Injected Flaw 1: Short entity leakage ('Fog')
        candidates[1].stem = "Why does Fog form over cold ground on clear winter nights?"
        candidates[1].options = [{'id': 'opt_a', 'text': "Fog"}, {'id': 'opt_b', 'text': "Mist"}, {'id': 'opt_c', 'text': "Haze"}, {'id': 'opt_d', 'text': "Smog"}]
        candidates[1].correctAnswer = "opt_a"

        # Injected Flaw 2: Short entity leakage ('Ice')
        candidates[2].stem = "Which solid form of precipitation is termed Ice when frozen?"
        candidates[2].options = [{'id': 'opt_a', 'text': "Ice"}, {'id': 'opt_b', 'text': "Rain"}, {'id': 'opt_c', 'text': "Sleet"}, {'id': 'opt_d', 'text': "Hail"}]
        candidates[2].correctAnswer = "opt_a"

        # Injected Flaw 3: Quotation template
        candidates[3].stem = 'What is a direct consequence of "plate subduction"?'

        # Injected Flaw 4: Trivial stem (< 15 chars)
        candidates[4].stem = "What is Earth?"

        # Injected Flaw 5: Another trivial stem
        candidates[5].stem = "What is rock?"

        # Injected Flaw 6: Unsupported exam target
        candidates[6].examTarget = "Kindergarten-Quiz"

        # Injected Flaw 7: Unsupported cognitive demand
        candidates[7].cognitiveDemand = "MEMORIZE"

        # Injected Flaw 8: Duplicate options
        candidates[8].options = [{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Basalt"}, {'id': 'opt_d', 'text': "Sandstone"}]
        candidates[8].correctAnswer = "opt_a"

        # Injected Flaw 9: Empty option
        candidates[9].options = [{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': ""}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Sandstone"}]
        candidates[9].correctAnswer = "opt_a"

        # Injected Flaw 10: Whitespace option
        candidates[10].options = [{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "   "}, {'id': 'opt_c', 'text': "Marble"}, {'id': 'opt_d', 'text': "Sandstone"}]
        candidates[10].correctAnswer = "opt_a"

        # Injected Flaw 11: Lazy template pattern
        candidates[11].stem = "According to the passage, which river is antecedent in the Himalayas?"

        # Run 3-phase autonomous cycle
        cycle_result = self.pipeline.run_cycle(candidates)
        initial = cycle_result["initial_metrics"]
        final = cycle_result["final_metrics"]

        # Phase 1 Checks: Flaws caught
        self.assertGreaterEqual(initial["failed"], 12, "Phase 1 must catch all 12 injected flaws")
        self.assertLess(initial["pass_rate"], 1.0, "Initial pass rate must reflect detected flaws")
        self.assertIn("LEAKAGE", initial["flaw_clusters"])
        self.assertIn("TEMPLATE", initial["flaw_clusters"])
        self.assertIn("TRIVIAL_STEM", initial["flaw_clusters"])
        self.assertIn("UNSUPPORTED_EXAM", initial["flaw_clusters"])

        # Phase 3 Checks: 100% Clearance
        self.assertEqual(final["failed"], 0, f"Phase 3 must achieve 0 failures, got {final['failed']}")
        self.assertEqual(final["pass_rate"], 1.0, f"Phase 3 pass rate must be 100%, got {final['pass_rate']}")
        self.assertEqual(len(cycle_result["regenerated_questions"]), len(candidates))
        self.assertGreater(final["improvement_pct"], 0.0)

        # Verify every single regenerated question independently via auditing gate
        for idx, cq in enumerate(cycle_result["regenerated_questions"]):
            rep = self.gate.audit(cq)
            self.assertEqual(
                rep.overallGate, "PASS",
                f"Candidate {idx} ('{cq.id}') failed post-regeneration: {rep.failureReasons}"
            )


class TestZeroHardcodedStringsAndDomainCoherence(unittest.TestCase):
    """Verifies that no hardcoded strings exist in QuestionRepairEngine and domain coherence is strictly preserved."""

    def test_zero_hardcoded_entity_strings_in_auditors_py(self):
        """auditors.py QuestionRepairEngine must contain zero hardcoded entity or domain strings."""
        file_path = os.path.join(REPO_ROOT, "v13_discovery", "auditors.py")
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        repair_engine_idx = code.find("class QuestionRepairEngine")
        self.assertGreater(repair_engine_idx, 0)
        repair_section = code[repair_engine_idx:]

        banned_tokens = [
            '"granite"', "'granite'",
            '"oxbow"', "'oxbow'",
            '"earth"', "'earth'",
            '"basalt"', "'basalt'",
            '"celestial bodies"', "'celestial bodies'",
            '"planetary astronomy"', "'planetary astronomy'",
            '"oxygen-rich atmosphere"', "'oxygen-rich atmosphere'"
        ]
        for token in banned_tokens:
            self.assertNotIn(
                token, repair_section.lower(),
                f"Found banned hardcoded string {token} in QuestionRepairEngine"
            )

    def test_domain_coherence_preserved_on_rock_candidate(self):
        """When candidate 2 (topic: rock types, correct answer: Basalt) has stem 'What is Earth?',
        repair must keep it in the rock domain, NOT astronomy."""
        cq = CandidateQuestion(
            id="q_rock_earth_stem",
            stem="What is Earth?",
            options=[{'id': 'opt_a', 'text': "Sandstone"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Shale"}, {'id': 'opt_d', 'text': "Granite"}],
            correctAnswer="opt_b",
            explanation="Basalt is a mafic extrusive igneous rock formed from lava cooling rapidly.",
            distractorDissections=[],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_rock_1"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        gate = MultiAgentAuditingGate()
        engine = QuestionRepairEngine()

        rep = gate.audit(cq)
        self.assertEqual(rep.overallGate, "REJECT")

        repaired = engine.repair(cq, rep)
        self.assertNotIn("astronomy", repaired.stem.lower())
        self.assertNotIn("celestial", repaired.stem.lower())
        self.assertNotIn("oxygen-rich", repaired.stem.lower())
        self.assertNotIn("atmosphere", repaired.stem.lower())

        # Must maintain rock/geology domain or category hypernym
        self.assertTrue(
            any(w in repaired.stem.lower() for w in ["rock", "physical properties", "formation", "igneous", "geological"]),
            f"Repaired stem lacks geological domain coherence: '{repaired.stem}'"
        )

        # Repaired candidate must pass gate
        post_rep = gate.audit(repaired)
        self.assertEqual(post_rep.overallGate, "PASS")

    def test_domain_coherence_preserved_on_river_candidate(self):
        """Repair of trivial stem for a river landform question must not hallucinate celestial bodies."""
        cq = CandidateQuestion(
            id="q_river_stem",
            stem="What is it?",
            options=[{'id': 'opt_a', 'text': "Oxbow lake"}, {'id': 'opt_b', 'text': "Delta"}, {'id': 'opt_c', 'text': "Gorge"}, {'id': 'opt_d', 'text': "Waterfall"}],
            correctAnswer="opt_a",
            explanation="An oxbow lake is a crescent-shaped water body formed when a river meander is cut off.",
            distractorDissections=[],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_river_1"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        gate = MultiAgentAuditingGate()
        engine = QuestionRepairEngine()

        rep = gate.audit(cq)
        repaired = engine.repair(cq, rep)

        self.assertNotIn("celestial", repaired.stem.lower())
        self.assertNotIn("astronomy", repaired.stem.lower())
        self.assertNotIn("planet", repaired.stem.lower())

        post_rep = gate.audit(repaired)
        self.assertEqual(post_rep.overallGate, "PASS")


class TestRoomDBMarkdownSerializationContract(unittest.TestCase):
    """Verifies Room DB serialization ordering, formatting, and zero truncation in DataImporterSimulator."""

    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        synthesizer = QuestionSynthesizer()
        raw_candidates = synthesizer.synthesize_from_corpus(corpus_path, min_questions=55)
        pipeline = SelfRepairPipeline()
        cls.cycle_result = pipeline.run_cycle(raw_candidates)
        cls.questions = cls.cycle_result["regenerated_questions"]

    def test_explanation_strictly_precedes_correct_answer_and_format(self):
        """Contract: 'Explanation:' strictly precedes 'Correct Answer:' with format 'Option (X) is correct.'."""
        self.assertGreaterEqual(len(self.questions), 50)

        for idx, q in enumerate(self.questions):
            md = q.to_room_markdown()

            # Must contain both markers
            self.assertIn("Explanation:", md, f"Question {idx} missing 'Explanation:'")
            self.assertIn("Correct Answer:", md, f"Question {idx} missing 'Correct Answer:'")

            # Sequence: Explanation strictly before Correct Answer
            exp_pos = md.find("Explanation:")
            ans_pos = md.find("Correct Answer:")
            self.assertLess(
                exp_pos, ans_pos,
                f"Question {idx}: 'Explanation:' (pos {exp_pos}) must strictly precede 'Correct Answer:' (pos {ans_pos})"
            )

            # Format check: Explanation starts with 'Option (X) is correct.'
            correct_letter = q.correctAnswer.replace("opt_", "").upper()
            expected_prefix = f"Option ({correct_letter}) is correct."
            self.assertTrue(
                q.explanation.strip().startswith(expected_prefix),
                f"Question {idx} explanation '{q.explanation[:40]}' does not start with '{expected_prefix}'"
            )

            # Correct answer line format: 'Correct Answer: Option X'
            ans_line_match = re.search(r"Correct Answer:\s*Option\s*([A-D])", md)
            self.assertIsNotNone(ans_line_match, f"Question {idx}: malformed Correct Answer line in md")
            self.assertEqual(
                ans_line_match.group(1), correct_letter,
                f"Question {idx}: Correct Answer letter mismatch: expected {correct_letter}, got {ans_line_match.group(1)}"
            )

    def test_zero_truncation_under_data_importer_simulator(self):
        """Verifies DataImporterSimulator parses all 50+ questions with 0 rejections and NO explanation truncation."""
        full_md_blocks = ["# Geography Topic\n\n## 1. Physical Geography\n"]
        for q in self.questions:
            full_md_blocks.append(q.to_room_markdown() + "\n")
        full_md = "\n".join(full_md_blocks)

        parsed = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(
            parsed["totalAccepted"], len(self.questions),
            f"DataImporterSimulator rejected questions: {parsed['rejections']}"
        )
        self.assertEqual(parsed["totalRejected"], 0)

        # Inspect every parsed question entity for zero truncation
        for idx, (orig_q, parsed_q) in enumerate(zip(self.questions, parsed["questions"])):
            parsed_exp = parsed_q["explanation"].strip()
            orig_exp = orig_q.explanation.strip()

            # The parsed explanation must contain the entire original explanation
            self.assertEqual(
                parsed_exp, orig_exp,
                f"Question {idx} explanation was truncated or altered!\nExpected: {orig_exp}\nGot: {parsed_exp}"
            )
            # Question stem must be preserved
            self.assertEqual(parsed_q["questionText"].strip(), orig_q.stem.strip())
            # Correct answer must match
            self.assertEqual(parsed_q["correctAnswer"], orig_q.correctAnswer)


class TestDistractorDissections8TrapTypes(unittest.TestCase):
    """Verifies all distractor dissections map to the 8 valid Room DB trap types with substantive rationales."""

    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        synthesizer = QuestionSynthesizer()
        raw_candidates = synthesizer.synthesize_from_corpus(corpus_path, min_questions=50)
        pipeline = SelfRepairPipeline()
        cls.questions = pipeline.run_cycle(raw_candidates)["regenerated_questions"]

    def test_all_dissections_map_to_valid_room_trap_types(self):
        """Every distractor dissection across all questions must have trapType in VALID_ROOM_TRAP_TYPES."""
        total_dissections = 0

        for q_idx, q in enumerate(self.questions):
            self.assertTrue(len(q.distractorDissections) > 0, f"Question {q_idx} has no distractor dissections")
            correct_opt = q.correctAnswer.lower()

            for d in q.distractorDissections:
                total_dissections += 1
                opt_id = d.get("optionId", "").lower()
                trap_type = d.get("trapType", "")
                rationale = d.get("dissection", "")

                # 1. Never dissect correct answer
                self.assertNotEqual(
                    opt_id, correct_opt,
                    f"Question {q_idx}: Dissection created for correct answer {correct_opt}!"
                )

                # 2. Must be one of the 8 Room DB trap types
                self.assertIn(
                    trap_type, VALID_ROOM_TRAP_TYPES,
                    f"Question {q_idx}: Invalid trap type '{trap_type}' not in VALID_ROOM_TRAP_TYPES"
                )

                # 3. Rationale must be > 10 characters
                self.assertGreater(
                    len(rationale), 10,
                    f"Question {q_idx}: Dissection rationale too short ({len(rationale)} chars): '{rationale}'"
                )

        self.assertGreaterEqual(total_dissections, 150, "Must have verified >= 150 distractor dissections")

    def test_all_8_room_db_trap_types_coverage_and_rationales(self):
        """Verifies that DistractorDissector supports all 8 Room DB trap types with substantive rationales (>10 chars)."""
        onto = OntologyRegistry()
        rock_cat = onto.get_category("rock_types")

        for trap in VALID_ROOM_TRAP_TYPES:
            dissection = DistractorDissector.dissect(
                option_id="opt_b",
                distractor_text="Basalt",
                correct_text="Granite",
                category=rock_cat,
                intent_type="definition",
                evidence="Granite is an intrusive igneous rock.",
                forced_trap_type=trap
            )
            self.assertEqual(dissection["trapType"], trap)
            self.assertGreater(
                len(dissection["dissection"]), 10,
                f"Trap {trap} rationale too short: '{dissection['dissection']}'"
            )
            self.assertIn("opt_b", dissection["optionId"])

    def test_dissection_json_parses_cleanly_under_simulator(self):
        """Verifies distractor dissections serialized into Room DB JSON by DataImporterSimulator are valid JSON."""
        for q in self.questions[:20]:
            md = "# Topic\n\n## 1. Physical Geography\n" + q.to_room_markdown()
            parsed = DataImporterSimulator.parse_markdown(md)
            self.assertEqual(parsed["totalAccepted"], 1)

            dissections_json_str = parsed["questions"][0]["distractorDissections"]
            # Must parse without json.decoder.JSONDecodeError
            decoded = json.loads(dissections_json_str)
            self.assertIsInstance(decoded, list)


class TestAdversarialStressAndEdgeCases(unittest.TestCase):
    """Stress tests boundary cases: special chars, low-cardinality siblings, multiline strings."""

    def test_multiline_explanation_preserves_clean_parsing(self):
        """Multiline explanation must not break DataImporterSimulator or cause premature truncation."""
        cq = CandidateQuestion(
            id="q_multiline_exp",
            stem="Which of the following processes is primarily responsible for oxbow lake formation?",
            options=[{'id': 'opt_a', 'text': "River meandering"}, {'id': 'opt_b', 'text': "Wind abrasion"}, {'id': 'opt_c', 'text': "Glacial plucking"}, {'id': 'opt_d', 'text': "Marine erosion"}],
            correctAnswer="opt_a",
            explanation=(
                "Option (A) is correct. River meandering leads to neck narrowing.\n\n"
                "During high flood stages, the river cuts through the narrow neck,\n"
                "leaving behind an abandoned channel known as an oxbow lake."
            ),
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Wind abrasion causes yardangs not oxbow lakes."},
                {"optionId": "opt_c", "trapType": "FALSE_CORRELATION", "dissection": "Glacial plucking operates in glacial environments."},
                {"optionId": "opt_d", "trapType": "FAMILIARITY_TRAP", "dissection": "Marine erosion operates along coastlines."}
            ],
            provenance={"intentType": "process"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        md = "# Topic\n\n## 1. Physical Geography\n" + cq.to_room_markdown()
        parsed = DataImporterSimulator.parse_markdown(md)
        self.assertEqual(parsed["totalAccepted"], 1, f"Rejection on multiline explanation: {parsed['rejections']}")

        parsed_exp = parsed["questions"][0]["explanation"]
        self.assertIn("neck narrowing", parsed_exp)
        self.assertIn("oxbow lake", parsed_exp)

    def test_special_characters_in_options(self):
        """Options with punctuation (parentheses, slashes, hyphens) parse cleanly without splitting regex."""
        cq = CandidateQuestion(
            id="q_special_opts",
            stem="Which seismic body waves are transverse (shear) in nature and cannot travel through liquid media?",
            options=[{'id': 'opt_a', 'text': "S-waves (Secondary / Shear waves)"}, {'id': 'opt_b', 'text': "P-waves (Primary / Longitudinal waves)"}, {'id': 'opt_c', 'text': "L-waves (Love / Surface waves)"}, {'id': 'opt_d', 'text': "Rayleigh-waves (Elliptical / Rolling waves)"}],
            correctAnswer="opt_a",
            explanation="Option (A) is correct. S-waves are transverse and cannot pass through liquids.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "FACT_DISTORTION", "dissection": "P-waves are longitudinal and travel through liquids."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "L-waves are surface waves."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Rayleigh waves are surface waves."}
            ],
            provenance={"intentType": "classification"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        md = "# Topic\n\n## 1. Physical Geography\n" + cq.to_room_markdown()
        parsed = DataImporterSimulator.parse_markdown(md)
        self.assertEqual(parsed["totalAccepted"], 1, f"Special char options failed parse: {parsed['rejections']}")
        opts_list = json.loads(parsed["questions"][0]["options"])
        self.assertEqual(len(opts_list), 4)
        self.assertEqual(opts_list[0]["text"], "S-waves (Secondary / Shear waves)")

    def test_low_cardinality_category_repair_options_are_strictly_unique(self):
        """Repairing a candidate from a category with <3 siblings must yield 4 strictly unique options."""
        onto = OntologyRegistry()
        small_cat = CategoryDefinition(
            category_id="binary_system",
            domain="geology",
            display_name="Binary System",
            entity_type="COMMON_NOUN",
            grammatical_number="SINGULAR",
            members=["MemberAlpha", "MemberBeta"],  # Only 2 members total
            descriptions={}
        )
        onto.register_category(small_cat)

        engine = QuestionRepairEngine(ontology=onto)
        cq = CandidateQuestion(
            id="q_small_cat",
            stem="Why is MemberAlpha considered unique?",  # Leakage flaw
            options=[{'id': 'opt_a', 'text': "MemberAlpha"}, {'id': 'opt_b', 'text': "MemberBeta"}, {'id': 'opt_c', 'text': "MemberAlpha"}, {'id': 'opt_d', 'text': "MemberBeta"}],
            correctAnswer="opt_a",
            explanation="MemberAlpha is unique.",
            distractorDissections=[],
            provenance={"intentType": "definition"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        gate = MultiAgentAuditingGate(ontology=onto)
        report = gate.audit(cq)
        repaired = engine.repair(cq, report)

        # Check options uniqueness
        opt_values = [o.get("text", "").strip().lower() for o in repaired.options]
        self.assertEqual(len(set(opt_values)), 4, f"Options not strictly unique: {repaired.options}")
        for o in repaired.options:
            self.assertGreaterEqual(len(o.get("text", "").strip()), 2,
                                    f"Option {o.get('id')} too short: '{o.get('text')}'")


if __name__ == "__main__":
    unittest.main()
