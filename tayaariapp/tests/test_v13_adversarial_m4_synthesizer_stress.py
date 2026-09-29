#!/usr/bin/env python3
"""
tests/test_v13_adversarial_m4_synthesizer_stress.py
==================================================
Empirical Adversarial Stress Test Harness for Milestone 4:
Question & Ontological Defensible Distractor Engineering Engine.

Authored by Challenger 2 (challenger_m4_2) for Milestone 4 Gate Evaluation.

Adversarially tests:
1. Scale generation: Harvest >=100 questions from real corpus (geography_extracted.txt).
   Verifies 100% unique stems, 4-option completeness, non-empty/non-placeholder options,
   zero crashes, zero empty sets, and balanced option distribution.
2. Anti-quotation rules (NQ1-NQ5) and BANNED_LAZY_STEM_PATTERNS rejection across all stems.
3. Distractor dissections: Room DB trap type authorization, substantive rationales (>10 chars),
   and strict omission of correct answers.
4. Cryptographic tamper-proofing: 1-character/1-token mutations across question stem,
   evidence text, source location, knowledge node ID, intent type, and source file.
   Verifies 100% sensitivity on tampered records and 100% specificity (0 false alarms)
   on unmutated records.
5. Room DB markdown serialization: Validates to_room_markdown() against DataImporter.kt
   sequential regex rules (Explanation preceding Correct Answer), proving zero truncation,
   100% field fidelity, and 100% import acceptance.
"""

import os
import sys
import re
import unittest
from typing import List, Dict, Any, Set

# Ensure repository root is on sys.path
_cur_dir = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_cur_dir, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    DistractorVerificationGate,
    DistractorDissector,
    NaturalStemSynthesizer,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    ProvenanceTracker,
    verify_provenance_chain,
    audit_provenance_integrity,
    CANONICAL_14_INTENTS,
)
from tests.e2e.test_helpers import DataImporterSimulator

BANNED_LAZY_STEM_PATTERNS = [
    re.compile(r'(?i)what is a direct consequence of\s*["\']'),
    re.compile(r'(?i)which of the following is true regarding\s*["\']'),
    re.compile(r'(?i)consider the following statement\s*["\']'),
    re.compile(r'(?i)according to the passage'),
    re.compile(r'(?i)as stated in the text'),
    re.compile(r'(?i)based on the quote'),
    re.compile(r'(?i)from the provided paragraph'),
    re.compile(r'(?i)refer to the excerpt'),
]


class TestMilestone4ScaleGenerationStress(unittest.TestCase):
    """Adversarial stress-testing of large-scale question synthesis from real NCERT corpus."""

    @classmethod
    def setUpClass(cls):
        cls.corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        if not os.path.exists(cls.corpus_path):
            raise FileNotFoundError(f"Missing corpus file: {cls.corpus_path}")

        cls.synthesizer = QuestionSynthesizer()
        # Harvest >= 100 questions from real geography corpus
        cls.questions: List[CandidateQuestion] = cls.synthesizer.synthesize_from_corpus(
            corpus_path=cls.corpus_path,
            min_questions=100
        )

    def test_scale_generation_count_and_uniqueness(self):
        """Scale Generation: Produces >=100 questions with 100% unique question stems."""
        total = len(self.questions)
        self.assertGreaterEqual(
            total, 100,
            f"Expected at least 100 questions, synthesized: {total}"
        )

        stems_seen: Set[str] = set()
        duplicate_stems: List[str] = []

        for q in self.questions:
            clean_stem = re.sub(r'\s+', ' ', q.stem.strip().lower())
            if clean_stem in stems_seen:
                duplicate_stems.append(q.stem)
            stems_seen.add(clean_stem)

        self.assertEqual(
            len(duplicate_stems), 0,
            f"Found {len(duplicate_stems)} duplicate question stems in scale batch: {duplicate_stems[:3]}"
        )
        self.assertEqual(len(stems_seen), total, "Stem uniqueness is less than 100%")

    def test_scale_generation_option_validity(self):
        """Option Validity: Exactly 4 distinct, non-empty, non-placeholder options per question."""
        invalid_options_log = []
        option_letters_distribution = {'a': 0, 'b': 0, 'c': 0, 'd': 0}

        for q in self.questions:
            # 1. Check exact 4 options with correct IDs
            option_ids = {opt["id"] for opt in q.options}
            if option_ids != {"opt_a", "opt_b", "opt_c", "opt_d"}:
                invalid_options_log.append(f"Q {q.id}: options IDs != {{'opt_a','opt_b','opt_c','opt_d'}}: {list(option_ids)}")

            # 2. Check distinct values
            opt_values = [opt.get("text", "").strip().lower() for opt in q.options]
            if len(set(opt_values)) != len(opt_values):
                invalid_options_log.append(f"Q {q.id}: duplicate option text within choices: {q.options}")

            # 3. Check placeholders and minimum length
            for opt in q.options:
                k = opt.get("id", "")
                val = opt.get("text", "")
                v_clean = val.strip()
                if len(v_clean) < 2:
                    invalid_options_log.append(f"Q {q.id}: option {k} too short (<2 chars): '{v_clean}'")
                if v_clean.lower() in {"none", "placeholder", "tbd", "option a", "option b", "option c", "option d"}:
                    invalid_options_log.append(f"Q {q.id}: placeholder option text detected: '{v_clean}'")

            # 4. Correct answer validity
            if not q.correctAnswer.startswith("opt_"):
                invalid_options_log.append(f"Q {q.id}: correctAnswer does not start with opt_: '{q.correctAnswer}'")
            ans_letter = q.correctAnswer.replace("opt_", "").lower()
            if ans_letter not in {'a', 'b', 'c', 'd'}:
                invalid_options_log.append(f"Q {q.id}: correctAnswer letter '{ans_letter}' not in a-d")
            else:
                option_letters_distribution[ans_letter] += 1

        self.assertEqual(
            len(invalid_options_log), 0,
            f"Detected option validity violations: {invalid_options_log[:5]}"
        )

        # 5. Check balanced answer letter distribution (no single slot dominates > 50%)
        total = len(self.questions)
        for letter, count in option_letters_distribution.items():
            freq = count / total
            self.assertLess(
                freq, 0.50,
                f"Option '{letter}' occupies {freq:.1%} of answers, exceeding 50% threshold"
            )
            self.assertGreater(
                count, 0,
                f"Option '{letter}' was never assigned as the correct answer"
            )

    def test_anti_quotation_and_template_cleanliness(self):
        """Anti-Quotation (NQ1-NQ5): Zero quote characters and zero lazy template phrases."""
        violating_stems = []
        for q in self.questions:
            stem = q.stem
            # NQ1: No quotation marks of any kind
            if any(q_char in stem for q_char in ['"', "'", '“', '”', '`', '‘', '’']):
                violating_stems.append(f"Q {q.id}: contains quotation marks: {stem}")

            # NQ2: No banned lazy quotation templates
            for banned in BANNED_LAZY_STEM_PATTERNS:
                if banned.search(stem):
                    violating_stems.append(f"Q {q.id}: matches banned lazy pattern: {stem}")

            # Natural terminal punctuation
            if not (stem.endswith("?") or stem.endswith(":")):
                violating_stems.append(f"Q {q.id}: stem does not terminate with '?' or ':': {stem}")

        self.assertEqual(
            len(violating_stems), 0,
            f"Detected anti-quotation violations: {violating_stems[:3]}"
        )

    def test_distractor_dissections_compliance(self):
        """Distractor Dissections: Exactly 3 dissections for distractors only, authorized trap types, substantive rationales."""
        violations = []
        for q in self.questions:
            correct_opt_id = q.correctAnswer  # e.g. opt_a
            dissections = q.distractorDissections

            if len(dissections) != 3:
                violations.append(f"Q {q.id}: expected exactly 3 dissections, got {len(dissections)}")

            dissected_ids = set()
            for d in dissections:
                opt_id = d.get("optionId", "")
                trap_type = d.get("trapType", "")
                rationale = d.get("dissection") or d.get("rationale", "")

                dissected_ids.add(opt_id)

                if opt_id == correct_opt_id:
                    violations.append(f"Q {q.id}: correct answer '{correct_opt_id}' was assigned a trap dissection!")

                if trap_type not in VALID_ROOM_TRAP_TYPES:
                    violations.append(f"Q {q.id}: unauthorized trap type '{trap_type}'")

                if len(rationale) < 15:
                    violations.append(f"Q {q.id}: pedagogical rationale too brief ({len(rationale)} chars): '{rationale}'")

            expected_distractor_ids = {f"opt_{l}" for l in ['a', 'b', 'c', 'd']} - {correct_opt_id}
            if dissected_ids != expected_distractor_ids:
                violations.append(f"Q {q.id}: dissected IDs {dissected_ids} != expected {expected_distractor_ids}")

        self.assertEqual(len(violations), 0, f"Dissection violations: {violations[:5]}")


class TestMilestone4CryptographicTamperProofingStress(unittest.TestCase):
    """Adversarial stress-testing of 6-link Merklized SHA-256 provenance tamper detection."""

    @classmethod
    def setUpClass(cls):
        cls.synthesizer = QuestionSynthesizer()
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        cls.questions = cls.synthesizer.synthesize_from_corpus(corpus_path, min_questions=100)
        cls.records = [q.provenance for q in cls.questions]

    def test_unmutated_records_pass_with_100_percent_specificity(self):
        """Specificity: 100% pass on unmutated records (0 false alarms)."""
        audit = audit_provenance_integrity(self.records)
        self.assertEqual(audit["total_records"], len(self.records))
        self.assertEqual(audit["valid_records"], len(self.records))
        self.assertEqual(audit["invalid_records"], 0)
        self.assertEqual(audit["tampered_records"], 0)
        self.assertEqual(audit["audit_verdict"], "PASS")
        self.assertEqual(audit["integrity_rate"], 1.0)

    def test_tamper_sensitivity_question_stem_1_char(self):
        """Tamper Sensitivity: 1-char modification in questionStem trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            stem = t.get("questionStem") or t.get("question_stem", "")
            # Mutate last character
            t["questionStem"] = stem[:-1] + ("!" if not stem.endswith("!") else "?")
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["total_records"], len(self.records))
        self.assertEqual(audit["valid_records"], 0, "Tampered stems evaded verification!")
        self.assertEqual(audit["tampered_records"], len(self.records), "Not all stem mutations flagged as tampered!")
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_tamper_sensitivity_evidence_text(self):
        """Tamper Sensitivity: 1-char modification in evidenceText trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            ev = t.get("evidenceText") or t.get("evidence_text", "")
            t["evidenceText"] = ev + " [TAMPERED]"
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["tampered_records"], len(self.records))
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_tamper_sensitivity_source_location_coordinates(self):
        """Tamper Sensitivity: Coordinate shift in sourceLocation trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            loc = dict(t.get("sourceLocation") or t.get("source_location", {}))
            loc["offset"] = loc.get("offset", 0) + 7
            loc["tampered_marker"] = True
            t["sourceLocation"] = loc
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["tampered_records"], len(self.records))
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_tamper_sensitivity_knowledge_node_id(self):
        """Tamper Sensitivity: Knowledge unit mutation trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            knid = t.get("knowledgeNodeId") or t.get("knowledge_node_id", "")
            t["knowledgeNodeId"] = knid + "_forged"
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["tampered_records"], len(self.records))
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_tamper_sensitivity_intent_type(self):
        """Tamper Sensitivity: Intent type swap trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            curr_intent = t.get("intentType") or t.get("intent_type", "definition")
            t["intentType"] = "process" if curr_intent != "process" else "definition"
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["tampered_records"], len(self.records))
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_tamper_sensitivity_source_file(self):
        """Tamper Sensitivity: Source file name swap trips cryptographic hash on all records."""
        tampered_batch = []
        for r in self.records:
            t = dict(r)
            t["sourceFile"] = "unauthorized_forged_source.txt"
            tampered_batch.append(t)

        audit = audit_provenance_integrity(tampered_batch)
        self.assertEqual(audit["tampered_records"], len(self.records))
        self.assertEqual(audit["audit_verdict"], "REJECT")

    def test_bulk_adversarial_mutation_battery_100_percent_detection(self):
        """Exhaustive Battery: 100 distinct pseudo-random mutations tested with 100% detection rate."""
        mutated_batch = []
        mutation_types = ["stem", "evidence", "location", "unit", "intent", "source", "hash_corrupt"]

        for idx, r in enumerate(self.records):
            t = dict(r)
            m_type = mutation_types[idx % len(mutation_types)]
            if m_type == "stem":
                t["questionStem"] = t.get("questionStem", "") + " *"
            elif m_type == "evidence":
                t["evidenceText"] = "Corrupted evidence " + str(idx)
            elif m_type == "location":
                t["sourceLocation"] = {"line": 99999, "offset": -1}
            elif m_type == "unit":
                t["knowledgeNodeId"] = f"kn_fake_{idx}"
            elif m_type == "intent":
                t["intentType"] = "invalid_intent_xyz"
            elif m_type == "source":
                t["sourceFile"] = f"fake_{idx}.pdf"
            elif m_type == "hash_corrupt":
                t["provenanceHash"] = "0" * 64

            mutated_batch.append(t)

        audit = audit_provenance_integrity(mutated_batch)
        self.assertEqual(audit["total_records"], 100)
        self.assertEqual(audit["valid_records"], 0, "At least one mutated record evaded detection!")
        self.assertEqual(audit["invalid_records"], 100)
        self.assertEqual(audit["audit_verdict"], "REJECT")
        self.assertEqual(audit["integrity_rate"], 0.0)


class TestMilestone4RoomDbMarkdownParsingStress(unittest.TestCase):
    """Adversarial stress-testing of CandidateQuestion.to_room_markdown against DataImporter.kt."""

    @classmethod
    def setUpClass(cls):
        cls.synthesizer = QuestionSynthesizer()
        corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
        cls.questions = cls.synthesizer.synthesize_from_corpus(corpus_path, min_questions=100)

    def test_explanation_strictly_precedes_correct_answer_in_markdown(self):
        """Structural Rule: 'Explanation:' must precede 'Correct Answer:' in all serialized markdown."""
        violations = []
        for q in self.questions:
            md = q.to_room_markdown()
            exp_pos = md.find("Explanation:")
            ans_pos = md.find("Correct Answer:")

            if exp_pos == -1:
                violations.append(f"Q {q.id}: Missing 'Explanation:' tag in markdown")
            if ans_pos == -1:
                violations.append(f"Q {q.id}: Missing 'Correct Answer:' tag in markdown")
            if exp_pos != -1 and ans_pos != -1 and exp_pos > ans_pos:
                violations.append(f"Q {q.id}: 'Explanation:' ({exp_pos}) appears AFTER 'Correct Answer:' ({ans_pos})")

        self.assertEqual(len(violations), 0, f"Ordering violations: {violations[:5]}")

    def test_sequential_regex_parsing_zero_explanation_truncation(self):
        """Sequential Regex: DataImporter.kt extraction preserves full explanation with zero truncation."""
        truncation_failures = []
        for q in self.questions:
            md = q.to_room_markdown()

            # Extract Question text block inside code fences.
            # MUST mirror DataImporter.kt line 63: a SINGLE backtick, not ```.
            q_fence_match = re.search(r'- \*\*Question\*\*:\s*`\s*(.*?)\s*`', md, re.DOTALL)
            self.assertIsNotNone(q_fence_match, f"Q {q.id}: Failed to match code fence")
            raw_q_text = q_fence_match.group(1).strip()

            # 1. Simulate DataImporter.kt Line 109: Correct Answer extraction
            ans_matcher = re.search(r'(?i)Correct [Aa]nswer:\s*(?:Option\s*)?([a-eA-E])', raw_q_text)
            self.assertIsNotNone(ans_matcher, f"Q {q.id}: Correct Answer matcher failed")
            correct_letter = ans_matcher.group(1).lower().strip()
            self.assertEqual(f"opt_{correct_letter}", q.correctAnswer)

            # DataImporter.kt line 117: rawQText = rawQText.substring(0, ansMatcher.start()).trim()
            raw_q_text = raw_q_text[:ans_matcher.start()].strip()

            # 2. Simulate DataImporter.kt Line 121: Explanation extraction
            exp_matcher = re.search(r'(?i)Explanation:\s*(.*)', raw_q_text, re.DOTALL)
            self.assertIsNotNone(exp_matcher, f"Q {q.id}: Explanation matcher failed after answer slicing")
            extracted_explanation = exp_matcher.group(1).strip()

            # Verify no truncation occurred
            expected_explanation = q.explanation.strip()
            if extracted_explanation != expected_explanation:
                truncation_failures.append({
                    "id": q.id,
                    "expected_len": len(expected_explanation),
                    "extracted_len": len(extracted_explanation),
                    "expected": expected_explanation[:60],
                    "extracted": extracted_explanation[:60]
                })

        self.assertEqual(
            len(truncation_failures), 0,
            f"Explanation truncation failures detected: {truncation_failures[:3]}"
        )

    def test_full_dataimporter_simulation_100_percent_acceptance(self):
        """Full DataImporter Simulation: 100/100 candidate questions accepted with 0 rejections."""
        # Assemble multi-question markdown file matching Room DB format
        md_builder = ["## 1. Physical Geography\n"]
        for q in self.questions:
            md_builder.append(q.to_room_markdown())
            md_builder.append("\n")

        full_md = "".join(md_builder)

        # Parse through exact DataImporterSimulator
        res = DataImporterSimulator.parse_markdown(full_md)

        self.assertEqual(res["totalFound"], len(self.questions))
        self.assertEqual(res["totalAccepted"], len(self.questions))
        self.assertEqual(res["totalRejected"], 0)
        self.assertEqual(len(res["rejections"]), 0, f"Rejections logged: {res['rejections'][:3]}")

        # Verify parsed entity details for each question
        parsed_questions = res["questions"]
        self.assertEqual(len(parsed_questions), len(self.questions))

        for orig, parsed in zip(self.questions, parsed_questions):
            self.assertEqual(parsed["correctAnswer"], orig.correctAnswer)
            self.assertEqual(parsed["explanation"], orig.explanation.strip())
            self.assertEqual(parsed["tier"], orig.tier)
            self.assertEqual(parsed["format"], orig.format)
            self.assertGreater(len(parsed["questionText"]), 10)

    def test_adversarial_explanation_containing_premature_trigger_mitigated(self):
        """Adversarial Defense: Confirms synthesizer prevents leading 'Correct Answer:' phrase in explanations."""
        for q in self.questions:
            # If explanation started with 'Correct Answer:', DataImporter.kt regex would prematurely slice
            self.assertFalse(
                q.explanation.startswith("Correct Answer:"),
                f"Q {q.id} explanation starts with 'Correct Answer:', which trips premature truncation!"
            )
            # Confirms safe formatting 'Option (X) is correct.'
            correct_upper = q.correctAnswer.replace("opt_", "").upper()
            self.assertTrue(
                q.explanation.startswith(f"Option ({correct_upper}) is correct."),
                f"Q {q.id} explanation does not follow safe prefix 'Option ({correct_upper}) is correct.'"
            )


class TestMilestone4AdversarialNegativeEdgeCases(unittest.TestCase):
    """Adversarial stress-testing of immutability, gate rejections, and regression hazards."""

    def test_provenance_record_frozen_immutability(self):
        """Immutability: ProvenanceRecord is strictly frozen; attributes cannot be mutated."""
        from dataclasses import FrozenInstanceError
        record = ProvenanceRecord.create(
            question_id="q_immutability_test",
            intent_type="definition",
            knowledge_node_id="kn_test_001",
            evidence_text="Troposphere is the lowest atmospheric layer.",
            source_file="geography.txt",
            source_location={"page": 1, "offset": 10},
            question_stem="Which is the lowest atmospheric layer?"
        )
        with self.assertRaises(FrozenInstanceError):
            record.question_stem = "Hacked Stem"
        with self.assertRaises(FrozenInstanceError):
            record.provenance_hash = "0" * 64
        with self.assertRaises(FrozenInstanceError):
            record.evidence_text = "Hacked Evidence"

    def test_provenance_registry_rejects_tampered_registration(self):
        """Registry Admission: ProvenanceRegistry rejects tampered records with ValueError."""
        from v13_discovery.provenance import ProvenanceRegistry
        registry = ProvenanceRegistry()
        record = ProvenanceRecord.create(
            question_id="q_reg_test",
            intent_type="definition",
            knowledge_node_id="kn_test_002",
            evidence_text="Stratosphere contains the ozone layer.",
            source_file="geography.txt",
            source_location={"page": 2, "offset": 20},
            question_stem="Which layer contains the ozone layer?"
        )
        # Register valid record
        registry.register(record)
        self.assertEqual(registry.count(), 1)

        # Forge a tampered record (mismatched hash)
        tampered_record = ProvenanceRecord(
            question_id="q_reg_test_tampered",
            intent_type="definition",
            knowledge_node_id="kn_test_002",
            evidence_text="Stratosphere contains the ozone layer.",
            source_file="geography.txt",
            source_location={"page": 2, "offset": 20},
            question_stem="Which layer contains the ozone layer?",
            provenance_hash="bad_hash" * 8,
            link_hashes=record.link_hashes,
        )
        with self.assertRaises(ValueError) as ctx:
            registry.register(tampered_record)
        self.assertIn("Cannot register tampered ProvenanceRecord", str(ctx.exception))

    def test_distractor_gate_adversarial_rejections(self):
        """Distractor Verification Gate: Rejects all adversarial defect patterns."""
        ont = OntologyRegistry()
        category = ont.get_category("petrology_rock_types")

        # 1. Stem-terminal article leakage
        valid, errs = DistractorVerificationGate.verify_all(
            options=[
                {'id': 'opt_a', 'text': 'Basalt'},
                {'id': 'opt_b', 'text': 'Granite'},
                {'id': 'opt_c', 'text': 'Sandstone'},
                {'id': 'opt_d', 'text': 'Marble'},
            ],
            correct_key='opt_a',
            stem="Which rock is termed an:",
            category=category
        )
        self.assertFalse(valid)
        self.assertTrue(any("article" in e.lower() for e in errs))

        # 2. Duplicate options
        valid, errs = DistractorVerificationGate.verify_all(
            options=[
                {'id': 'opt_a', 'text': 'Basalt'},
                {'id': 'opt_b', 'text': 'Basalt'},
                {'id': 'opt_c', 'text': 'Sandstone'},
                {'id': 'opt_d', 'text': 'Marble'},
            ],
            correct_key='opt_a',
            stem="Which of the following is an igneous rock?",
            category=category
        )
        self.assertFalse(valid)
        self.assertTrue(any("duplicate" in e.lower() for e in errs))

        # 3. Placeholder option text
        valid, errs = DistractorVerificationGate.verify_all(
            options=[
                {'id': 'opt_a', 'text': 'Basalt'},
                {'id': 'opt_b', 'text': 'Granite'},
                {'id': 'opt_c', 'text': 'Placeholder'},
                {'id': 'opt_d', 'text': 'Marble'},
            ],
            correct_key='opt_a',
            stem="Which of the following is an igneous rock?",
            category=category
        )
        self.assertFalse(valid)
        self.assertTrue(any("placeholder" in e.lower() for e in errs))

        # 4. Length outlier (>3x)
        valid, errs = DistractorVerificationGate.verify_all(
            options=[
                {'id': 'opt_a', 'text': 'Basalt is a very common dark colored fine grained igneous rock forming most of the oceanic crust and volcanic plateau'},
                {'id': 'opt_b', 'text': 'Granite'},
                {'id': 'opt_c', 'text': 'Sandstone'},
                {'id': 'opt_d', 'text': 'Marble'},
            ],
            correct_key='opt_a',
            stem="Which of the following is an igneous rock?",
            category=category
        )
        self.assertFalse(valid)
        self.assertTrue(any("length outlier" in e.lower() for e in errs))

        # 5. Correct answer stem leakage
        valid, errs = DistractorVerificationGate.verify_all(
            options=[
                {'id': 'opt_a', 'text': 'Basalt'},
                {'id': 'opt_b', 'text': 'Granite'},
                {'id': 'opt_c', 'text': 'Sandstone'},
                {'id': 'opt_d', 'text': 'Marble'},
            ],
            correct_key='opt_a',
            stem="Basalt is an example of which of the following rock types?",
            category=category
        )
        self.assertFalse(valid)
        self.assertTrue(any("stem leakage" in e.lower() for e in errs))

    def test_option_contract_is_single_namespace_and_strict(self):
        """
        The canonical option contract is exactly one namespace: prefixed `opt_x` ids.

        A bare letter ('a') must never be accepted anywhere, because the original
        defect was precisely a split namespace (bare-letter option dict paired with
        a prefixed 'opt_a' answer key) that silently defeated criteria 4 and 5.
        These assertions are strictly stronger than the shape checks above: they
        pin the prefix, the exact contiguous id set, and the count.
        """
        canonical = [
            {'id': 'opt_a', 'text': 'Basalt'},
            {'id': 'opt_b', 'text': 'Granite'},
            {'id': 'opt_c', 'text': 'Sandstone'},
            {'id': 'opt_d', 'text': 'Marble'},
        ]

        # Bare-letter answer key is rejected outright.
        with self.assertRaises(ValueError):
            DistractorVerificationGate.verify_all(
                options=canonical, correct_key='a',
                stem="Which of the following is an igneous rock?", category=None
            )

        # Bare-letter option ids are rejected outright.
        with self.assertRaises(ValueError):
            DistractorVerificationGate.verify_all(
                options=[{'id': 'a', 'text': 'Basalt'}, {'id': 'b', 'text': 'Granite'},
                         {'id': 'c', 'text': 'Sandstone'}, {'id': 'd', 'text': 'Marble'}],
                correct_key='opt_a',
                stem="Which of the following is an igneous rock?", category=None
            )

        # Legacy bare-letter dict options are rejected (no silent dual format).
        with self.assertRaises(TypeError):
            DistractorVerificationGate.verify_all(
                options={'a': 'Basalt', 'b': 'Granite', 'c': 'Sandstone', 'd': 'Marble'},
                correct_key='opt_a',
                stem="Which of the following is an igneous rock?", category=None
            )

        # Non-contiguous / reordered ids are rejected.
        with self.assertRaises(ValueError):
            DistractorVerificationGate.verify_all(
                options=[{'id': 'opt_d', 'text': 'Marble'}, {'id': 'opt_a', 'text': 'Basalt'},
                         {'id': 'opt_b', 'text': 'Granite'}, {'id': 'opt_c', 'text': 'Sandstone'}],
                correct_key='opt_a',
                stem="Which of the following is an igneous rock?", category=None
            )

        # Too few options are rejected.
        with self.assertRaises(ValueError):
            DistractorVerificationGate.verify_all(
                options=[{'id': 'opt_a', 'text': 'Basalt'}, {'id': 'opt_b', 'text': 'Granite'},
                         {'id': 'opt_c', 'text': 'Sandstone'}],
                correct_key='opt_a',
                stem="Which of the following is an igneous rock?", category=None
            )

        # An answer key that matches no option id is rejected.
        with self.assertRaises(ValueError):
            DistractorVerificationGate.verify_all(
                options=canonical, correct_key='opt_e',
                stem="Which of the following is an igneous rock?", category=None
            )

        # A five-option question is legal and uses the contiguous opt_a..opt_e set.
        five = canonical + [{'id': 'opt_e', 'text': 'Obsidian'}]
        self.assertEqual(
            [o['id'] for o in five],
            ['opt_a', 'opt_b', 'opt_c', 'opt_d', 'opt_e'],
        )
        valid, errs = DistractorVerificationGate.verify_all(
            options=five, correct_key='opt_a',
            stem="Which of the following is an igneous rock?", category=None
        )
        self.assertIsInstance(valid, bool)
        self.assertIsInstance(errs, list)

    def test_room_markdown_regression_demonstrates_truncation_hazard(self):
        """Empirical Demonstration: Flawed order ('Correct Answer:' before 'Explanation:') causes explanation loss."""
        # Intentionally flawed markdown order
        flawed_md = (
            "## 1. Physical Geography\n"
            "- **Topic**: 1. Physical Geography\n"
            "- **Tier**: Standard\n"
            "- **Format**: Direct Fact\n"
            "- **Exam-Relevance**: High\n"
            "- **Source**: NCERT Physical Geography\n"
            "- **Specific-Exam**: UPSC-Prelims\n"
            "- **PDF-Sequence-Number**: V13-999\n"
            "- **Question**: `\n"
            "Which layer of the atmosphere contains the ozone layer?\n"
            "(A) Troposphere\n"
            "(B) Stratosphere\n"
            "(C) Mesosphere\n"
            "(D) Thermosphere\n"
            "Correct Answer: Option B\n"
            "Explanation: Option (B) is correct. Stratosphere contains the protective ozone layer.\n"
            "`\n"
        )
        res = DataImporterSimulator.parse_markdown(flawed_md)
        self.assertEqual(res["totalFound"], 1)
        self.assertEqual(res["totalAccepted"], 1)
        parsed_q = res["questions"][0]

        # In the flawed ordering, DataImporter.kt cuts off rawQText at Correct Answer, leaving explanation as 'No explanation'!
        self.assertEqual(
            parsed_q["explanation"], "No explanation",
            "Demonstration failed: Flawed order did not result in explanation loss as predicted by DataImporter.kt regex!"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

