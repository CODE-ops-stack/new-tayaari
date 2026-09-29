#!/usr/bin/env python3
"""
tests/test_v13_adversarial_m3_provenance_stress.py
=================================================
Empirical Adversarial Stress Test Suite for Milestone 3 Unbreakable Provenance.

Authored by Challenger 1 (challenger_m3_1) for Milestone 3 Gate Evaluation.

Adversarially tests:
1. 1-character tamper resistance across all 6 chain links (stem, intent, unit, evidence, source, location)
2. Merklized link hash verification and exact link pinpointing via verify_hash()
3. Strict immutability and FrozenInstanceError enforcement on ProvenanceRecord and LinkHashes
4. Corpus grounding precision: verbatim matching, offset bounds, missing files, out-of-bounds offset detection
5. Fuzzing & automated mutation harness: 100 pseudo-random single-byte mutations
"""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

# Ensure repository root is on sys.path
_cur_dir = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_cur_dir, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.provenance import (
    ProvenanceRecord,
    ProvenanceRegistry,
    ProvenanceTracker,
    LinkHashes,
    verify_provenance_chain,
    validate_provenance_chain,
    audit_provenance_integrity,
    VerificationResult,
    CANONICAL_14_INTENTS,
)


class TestAdversarialTamperResistance(unittest.TestCase):
    """Stress-tests tamper resistance against single-character modifications across all links."""

    def setUp(self):
        self.record = ProvenanceRecord.create(
            question_id="q_geo_404",
            intent_type="definition",
            knowledge_node_id="kn_geo_808",
            evidence_text="A meander is a loop-like bend in the course of a river.",
            source_file="NCERT_Physical_Geography.pdf",
            source_location={"page": 54, "paragraph": 3, "offset": 240},
            question_stem="What is a meander?",
        )

    def test_tamper_single_char_in_stem(self):
        tampered = self.record.to_camel_dict()
        # Alter last character '?' -> '!'
        tampered["questionStem"] = "What is a meander!"
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_tamper_single_char_in_evidence(self):
        tampered = self.record.to_camel_dict()
        # Alter last character '.' -> '!'
        tampered["evidenceText"] = "A meander is a loop-like bend in the course of a river!"
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_tamper_single_char_in_source_file(self):
        tampered = self.record.to_camel_dict()
        # Alter 'f' -> 'd' in pdf
        tampered["sourceFile"] = "NCERT_Physical_Geography.pdd"
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_tamper_single_char_in_intent(self):
        tampered = self.record.to_camel_dict()
        # Alter 'n' -> 'm' in definition
        tampered["intentType"] = "definitiom"
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        # Invalid intent or cryptographic tamper detected
        self.assertTrue(res.tampered or any("not one of 14 valid intents" in err for err in res.errors))

    def test_tamper_single_char_in_knowledge_node_id(self):
        tampered = self.record.to_camel_dict()
        # Alter '8' -> '9'
        tampered["knowledgeNodeId"] = "kn_geo_809"
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)

    def test_tamper_location_coordinate_change(self):
        tampered = self.record.to_camel_dict()
        # Alter offset 240 -> 241
        tampered["sourceLocation"] = {"page": 54, "paragraph": 3, "offset": 241}
        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)


class TestMerklizedBrokenLinkDiagnosis(unittest.TestCase):
    """Stress-tests verify_hash() to ensure exact pinpointing of the corrupted link."""

    def setUp(self):
        self.record = ProvenanceRecord.create(
            question_id="q_atm_10",
            intent_type="cause_effect",
            knowledge_node_id="kn_atm_20",
            evidence_text="Solar radiation heats the Earth unevenly, creating wind.",
            source_file="atmosphere.md",
            source_location={"line": 102, "col": 5},
            question_stem="Why do winds form in the atmosphere?",
        )

    def test_pinpoints_source_location_tampering(self):
        mutant = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location={"line": 103, "col": 5},  # Tampered
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "sourceLocation")

    def test_pinpoints_source_file_tampering(self):
        mutant = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file="atmosphere_v2.md",  # Tampered
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "sourceFile")

    def test_pinpoints_evidence_text_tampering(self):
        mutant = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text="Solar radiation heats the Earth unevenly, creating wind!",  # Tampered
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "evidenceText")

    def test_pinpoints_knowledge_node_id_tampering(self):
        mutant = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id="kn_atm_99",  # Tampered
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "knowledgeNodeId")

    def test_pinpoints_intent_type_tampering(self):
        mutant = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type="attribute",  # Tampered
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "intentType")

    def test_pinpoints_question_stem_or_id_tampering(self):
        mutant_stem = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem="Why do winds form in the troposphere?",  # Tampered
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes,
        )
        is_valid, failing_link = mutant_stem.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "questionId_or_stem")


class TestStrictImmutabilityEnforcement(unittest.TestCase):
    """Verifies that all classes enforce complete immutability via FrozenInstanceError."""

    def test_provenance_record_all_attributes_frozen(self):
        record = ProvenanceRecord.create(
            question_id="q_1",
            intent_type="definition",
            knowledge_node_id="kn_1",
            evidence_text="Delta is a landform formed at the mouth of a river.",
            source_file="landforms.txt",
            source_location={"page": 8},
            question_stem="What is a delta?",
        )
        attrs = [
            ("question_id", "q_2"),
            ("intent_type", "process"),
            ("knowledge_node_id", "kn_2"),
            ("evidence_text", "Altered delta definition."),
            ("source_file", "other.txt"),
            ("source_location", {"page": 9}),
            ("question_stem", "What is an estuary?"),
            ("provenance_hash", "0" * 64),
            ("link_hashes", None),
            ("created_at", "2026-01-01"),
            ("schema_version", "2.0.0"),
            ("metadata", {"modified": True}),
        ]
        for attr, new_val in attrs:
            with self.subTest(attr=attr):
                with self.assertRaises(FrozenInstanceError):
                    setattr(record, attr, new_val)

    def test_link_hashes_all_attributes_frozen(self):
        lh = LinkHashes(
            location_hash="a" * 64,
            source_hash="b" * 64,
            evidence_hash="c" * 64,
            unit_hash="d" * 64,
            intent_hash="e" * 64,
            question_hash="f" * 64,
        )
        fields = ["location_hash", "source_hash", "evidence_hash", "unit_hash", "intent_hash", "question_hash"]
        for f in fields:
            with self.subTest(field=f):
                with self.assertRaises(FrozenInstanceError):
                    setattr(lh, f, "0" * 64)


class TestCorpusGroundingBoundaries(unittest.TestCase):
    """Tests corpus grounding across verbatim, offset precision, and missing file checks."""

    def setUp(self):
        self.corpus = {
            "ncert_geo_ch1.txt": "The planet Earth is the third planet from the Sun.",
            "ncert_geo_ch2.txt": "Sedimentary rocks are formed by the deposition and subsequent cementation of mineral or organic particles.",
        }

    def test_verbatim_grounding_success(self):
        record = ProvenanceRecord.create(
            question_id="q_earth",
            intent_type="attribute",
            knowledge_node_id="kn_earth",
            evidence_text="The planet Earth is the third planet from the Sun.",
            source_file="ncert_geo_ch1.txt",
            source_location={"offset": 0},
        )
        res = verify_provenance_chain(record, source_corpus=self.corpus)
        self.assertTrue(bool(res))
        self.assertTrue(res.grounded)

    def test_missing_file_in_multi_file_corpus(self):
        record = ProvenanceRecord.create(
            question_id="q_earth",
            intent_type="attribute",
            knowledge_node_id="kn_earth",
            evidence_text="The planet Earth is the third planet from the Sun.",
            source_file="ncert_geo_ch99.txt",  # Missing
            source_location={"offset": 0},
        )
        res = verify_provenance_chain(record, source_corpus=self.corpus)
        self.assertFalse(bool(res))
        self.assertFalse(res.grounded)
        self.assertTrue(any("not found in source_corpus" in err for err in res.errors))

    def test_offset_mismatch_detected(self):
        record = ProvenanceRecord.create(
            question_id="q_sed",
            intent_type="process",
            knowledge_node_id="kn_sed",
            evidence_text="Sedimentary rocks are formed by",
            source_file="ncert_geo_ch2.txt",
            source_location={"offset": 10},  # True offset is 0
        )
        res = verify_provenance_chain(record, source_corpus=self.corpus)
        self.assertFalse(bool(res))
        self.assertFalse(res.grounded)
        self.assertTrue(any("offset" in err.lower() for err in res.errors))


class TestAutomatedMutationFuzzing(unittest.TestCase):
    """Runs 100 deterministic pseudo-random single-byte mutations to verify zero false acceptance."""

    def test_100_mutations_tamper_detection(self):
        clean = ProvenanceRecord.create(
            question_id="q_fuzz_base",
            intent_type="definition",
            knowledge_node_id="kn_fuzz_base",
            evidence_text="A glacier is a persistent body of dense ice that is constantly moving under its own gravity.",
            source_file="geology_fuzz.txt",
            source_location={"page": 12, "offset": 45},
            question_stem="What is a glacier?",
        )
        base_dict = clean.to_camel_dict()
        fields_to_mutate = ["questionStem", "evidenceText", "sourceFile", "knowledgeNodeId"]

        detected_count = 0
        total_trials = 100

        for i in range(total_trials):
            field = fields_to_mutate[i % len(fields_to_mutate)]
            tampered = dict(base_dict)
            val = list(tampered[field])
            char_idx = (i * 7) % len(val)
            # Mutate character by altering ASCII code
            val[char_idx] = chr((ord(val[char_idx]) + 1) % 126 or 65)
            tampered[field] = "".join(val)

            res = verify_provenance_chain(tampered)
            if not res.is_valid and res.tampered:
                detected_count += 1

        self.assertEqual(detected_count, total_trials, f"Tamper detection rate was {detected_count}/{total_trials}")


if __name__ == "__main__":
    unittest.main()
