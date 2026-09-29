#!/usr/bin/env python3
"""
tests/test_v13_provenance.py
===========================
Comprehensive Test Suite for V13 Unbreakable Provenance Architecture.

Validates:
1. Strict 6-link chain completeness (Question -> Intent -> Node -> Evidence -> Source -> Location)
2. Immutable data model with frozen attributes
3. SHA-256 tamper-evident cryptographic verification on all links
4. Corpus grounding and verbatim text verification (single and multi-file)
5. Non-triviality and placeholder defense
6. Batch audit integrity and failure diagnosis
7. KnowledgeNode and CandidateQuestion integration bridges
"""

import os
import sys
import json
import unittest
from dataclasses import FrozenInstanceError

# Ensure repository root is in sys.path
_cur_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(_cur_dir, "..", "v13_discovery")):
    REPO_ROOT = os.path.abspath(os.path.join(_cur_dir, ".."))
elif os.path.exists(os.path.join(_cur_dir, "..", "..", "v13_discovery")):
    REPO_ROOT = os.path.abspath(os.path.join(_cur_dir, "..", ".."))
else:
    REPO_ROOT = os.getcwd()

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.provenance import (
    ProvenanceRecord,
    ProvenanceRegistry,
    ProvenanceTracker,
    verify_provenance_chain,
    validate_provenance_chain,
    audit_provenance_integrity,
    VerificationResult,
    CANONICAL_14_INTENTS,
    canonicalize_intent,
    to_r2_intent,
)
from v13_discovery.semantic_extractor import KnowledgeNode


class TestProvenance6LinkChain(unittest.TestCase):
    """Tests complete 6-link provenance chain creation, serialization, and completeness."""

    def test_01_valid_6_link_chain_creation(self):
        record = ProvenanceRecord.create(
            question_id="q_geo_101",
            intent_type="definition",
            knowledge_node_id="kn_geo_502",
            evidence_text="An oxbow lake is a U-shaped body of water.",
            source_file="NCERT-Class-11-Geography.pdf",
            source_location={"page": 45, "paragraph": 2, "offset": 120},
            question_stem="What is an oxbow lake?",
        )
        self.assertEqual(record.question_id, "q_geo_101")
        self.assertEqual(record.intent_type, "definition")
        self.assertEqual(record.knowledge_node_id, "kn_geo_502")
        self.assertEqual(record.evidence_text, "An oxbow lake is a U-shaped body of water.")
        self.assertEqual(record.source_file, "NCERT-Class-11-Geography.pdf")
        self.assertEqual(record.source_location, {"page": 45, "paragraph": 2, "offset": 120})
        self.assertEqual(record.question_stem, "What is an oxbow lake?")
        self.assertIsNotNone(record.provenance_hash)
        self.assertEqual(len(record.provenance_hash), 64)
        self.assertIsNotNone(record.link_hashes)

        # Verify chain integrity
        res = verify_provenance_chain(record)
        self.assertTrue(res.is_valid)
        self.assertTrue(bool(res))
        self.assertEqual(len(res.errors), 0)

    def test_02_missing_link_1_question_id(self):
        prov = {
            "questionId": "",  # Missing Link 1
            "intentType": "definition",
            "knowledgeNodeId": "kn_502",
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "geography.pdf",
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 1: Question ID" in err or "questionId" in err for err in res.errors))

    def test_03_missing_link_2_intent_type(self):
        prov = {
            "questionId": "q_101",
            "intentType": "",  # Missing Link 2
            "knowledgeNodeId": "kn_502",
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "geography.pdf",
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 2: Intent Type" in err or "intentType" in err for err in res.errors))

    def test_04_invalid_intent_not_in_14_canonical(self):
        prov = {
            "questionId": "q_101",
            "intentType": "invented_intent_type",  # Invalid intent
            "knowledgeNodeId": "kn_502",
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "geography.pdf",
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("is not one of 14 valid intents" in err for err in res.errors))

    def test_05_missing_link_3_knowledge_node_id(self):
        prov = {
            "questionId": "q_101",
            "intentType": "definition",
            "knowledgeNodeId": "",  # Missing Link 3
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "geography.pdf",
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 3: Knowledge Unit ID" in err or "knowledgeNodeId" in err for err in res.errors))

    def test_06_missing_link_4_evidence_text(self):
        prov = {
            "questionId": "q_101",
            "intentType": "definition",
            "knowledgeNodeId": "kn_502",
            "evidenceText": "",  # Missing Link 4
            "sourceFile": "geography.pdf",
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 4: Evidence Text" in err or "evidenceText" in err for err in res.errors))

    def test_07_missing_link_5_source_file(self):
        prov = {
            "questionId": "q_101",
            "intentType": "definition",
            "knowledgeNodeId": "kn_502",
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "",  # Missing Link 5
            "sourceLocation": {"page": 45},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 5: Source File" in err or "sourceFile" in err for err in res.errors))

    def test_08_missing_link_6_source_location(self):
        prov = {
            "questionId": "q_101",
            "intentType": "definition",
            "knowledgeNodeId": "kn_502",
            "evidenceText": "An oxbow lake is a U-shaped body of water.",
            "sourceFile": "geography.pdf",
            "sourceLocation": {},  # Missing Link 6
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("Link 6: Source Location" in err or "sourceLocation" in err for err in res.errors))


class TestImmutabilityAndTamperEvidence(unittest.TestCase):
    """Tests immutability constraints and cryptographic SHA-256 tamper-evident detection."""

    def test_09_immutability_frozen_dataclass(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="An oxbow lake is a U-shaped body of water.",
            source_file="geography.pdf",
            source_location={"page": 45},
        )
        with self.assertRaises(FrozenInstanceError):
            record.evidence_text = "Mutated evidence string"

        with self.assertRaises(FrozenInstanceError):
            record.intent_type = "attribute"

    def test_10_tamper_detection_on_mutated_question_stem(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="An oxbow lake is a U-shaped body of water.",
            source_file="geography.pdf",
            source_location={"page": 45},
            question_stem="Original question stem",
        )
        tampered = record.to_camel_dict()
        tampered["questionStem"] = "Tampered question stem altering meaning"

        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_11_tamper_detection_on_mutated_intent(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="An oxbow lake is a U-shaped body of water.",
            source_file="geography.pdf",
            source_location={"page": 45},
        )
        tampered = record.to_camel_dict()
        tampered["intentType"] = "attribute"  # Changed intent

        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_12_tamper_detection_on_mutated_evidence_single_char(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="attribute",
            knowledge_node_id="kn_502",
            evidence_text="Granite is an intrusive igneous rock.",
            source_file="geography.pdf",
            source_location={"page": 12},
        )
        tampered = record.to_camel_dict()
        # Single character change ('.' -> '!')
        tampered["evidenceText"] = "Granite is an intrusive igneous rock!"

        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)
        self.assertTrue(any("Cryptographic tamper detected" in err for err in res.errors))

    def test_13_tamper_detection_on_mutated_source_file(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="Granite is an intrusive igneous rock.",
            source_file="geography_vol1.pdf",
            source_location={"page": 12},
        )
        tampered = record.to_camel_dict()
        tampered["sourceFile"] = "geography_vol2.pdf"

        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)

    def test_14_tamper_detection_on_mutated_location(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="Granite is an intrusive igneous rock.",
            source_file="geography.pdf",
            source_location={"page": 12},
        )
        tampered = record.to_camel_dict()
        tampered["sourceLocation"] = {"page": 13}  # Changed page coordinate

        res = verify_provenance_chain(tampered)
        self.assertFalse(bool(res))
        self.assertTrue(res.tampered)

    def test_15_merklized_link_hashes_pinpoint_failing_link(self):
        record = ProvenanceRecord.create(
            question_id="q_101",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="Granite is an intrusive igneous rock.",
            source_file="geography.pdf",
            source_location={"page": 12},
        )
        mutant = ProvenanceRecord(
            question_id=record.question_id,
            intent_type=record.intent_type,
            knowledge_node_id=record.knowledge_node_id,
            evidence_text="Altered evidence text",
            source_file=record.source_file,
            source_location=record.source_location,
            provenance_hash=record.provenance_hash,
            link_hashes=record.link_hashes,
        )
        is_valid, failing_link = mutant.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(failing_link, "evidenceText")

    def test_16_evolve_produces_valid_new_record(self):
        original = ProvenanceRecord.create(
            question_id="q_temp",
            intent_type="definition",
            knowledge_node_id="kn_502",
            evidence_text="Basalt is a mafic extrusive rock.",
            source_file="rocks.md",
            source_location={"line_start": 10},
        )
        evolved = original.evolve(
            question_id="q_final_999",
            question_stem="Which of the following describes Basalt?"
        )
        self.assertEqual(evolved.question_id, "q_final_999")
        self.assertEqual(evolved.question_stem, "Which of the following describes Basalt?")
        self.assertNotEqual(evolved.provenance_hash, original.provenance_hash)
        self.assertTrue(evolved.verify_hash()[0])


class TestCorpusGroundingAndVerbatimVerification(unittest.TestCase):
    """Tests verbatim source corpus grounding in single documents and multi-file corpora."""

    def test_17_verbatim_evidence_in_single_corpus_string(self):
        corpus = "Chapter 4: Rocks and Minerals. Granite is an intrusive igneous rock formed beneath the surface."
        record = ProvenanceRecord.create(
            question_id="q_1",
            intent_type="attribute",
            knowledge_node_id="kn_1",
            evidence_text="Granite is an intrusive igneous rock",
            source_file="chapter4.txt",
            source_location={"offset": 31},
        )
        res = verify_provenance_chain(record, source_corpus=corpus)
        self.assertTrue(bool(res))
        self.assertTrue(res.grounded)

    def test_18_altered_evidence_fails_corpus_grounding(self):
        corpus = "Granite is an intrusive igneous rock."
        tampered_prov = {
            "questionId": "q_102",
            "intentType": "attribute",
            "knowledgeNodeId": "kn_503",
            "evidenceText": "Granite is a metamorphic rock formed by heat.",
            "sourceFile": "corpus.txt",
            "sourceLocation": {"offset": 0},
        }
        res = verify_provenance_chain(tampered_prov, source_corpus=corpus)
        self.assertFalse(bool(res))
        self.assertFalse(res.grounded)
        self.assertTrue(any("not found verbatim in source corpus" in err for err in res.errors))

    def test_19_multi_file_corpus_dictionary_grounding(self):
        corpus_dict = {
            "NCERT_Ch1.txt": "The Earth is an oblate spheroid.",
            "NCERT_Ch2.txt": "Igneous rocks are formed by magma cooling.",
        }
        record = ProvenanceRecord.create(
            question_id="q_2",
            intent_type="process",
            knowledge_node_id="kn_2",
            evidence_text="Igneous rocks are formed by magma cooling.",
            source_file="NCERT_Ch2.txt",
            source_location={"page": 10},
        )
        res = verify_provenance_chain(record, source_corpus=corpus_dict)
        self.assertTrue(bool(res))

        # Check unknown file in corpus
        record_bad_file = ProvenanceRecord.create(
            question_id="q_3",
            intent_type="process",
            knowledge_node_id="kn_3",
            evidence_text="Igneous rocks are formed by magma cooling.",
            source_file="Unknown_Chapter.txt",
            source_location={"page": 10},
        )
        res_bad = verify_provenance_chain(record_bad_file, source_corpus=corpus_dict)
        self.assertFalse(bool(res_bad))
        self.assertTrue(any("not found in source_corpus" in err for err in res_bad.errors))

    def test_20_offset_precision_verification(self):
        corpus = "Prefix padding. The core target proposition occurs here. Suffix text."
        offset = corpus.index("The core target proposition occurs here.")
        record = ProvenanceRecord.create(
            question_id="q_off",
            intent_type="definition",
            knowledge_node_id="kn_off",
            evidence_text="The core target proposition occurs here.",
            source_file="text.txt",
            source_location={"offset": offset},
        )
        res = verify_provenance_chain(record, source_corpus=corpus)
        self.assertTrue(bool(res))

        # Off-by-one offset
        record_bad_off = ProvenanceRecord.create(
            question_id="q_bad_off",
            intent_type="definition",
            knowledge_node_id="kn_off",
            evidence_text="The core target proposition occurs here.",
            source_file="text.txt",
            source_location={"offset": offset + 1},
        )
        res_bad = verify_provenance_chain(record_bad_off, source_corpus=corpus)
        self.assertFalse(bool(res_bad))
        self.assertTrue(any("offset" in err.lower() for err in res_bad.errors))


class TestNonTrivialityAndPlaceholderDefense(unittest.TestCase):
    """Tests rejection of trivial strings, placeholders, and malformed coordinates."""

    def test_21_rejects_trivial_source_files(self):
        trivial_vals = ["test", "sample", "todo", "n/a", "none", "unknown", "0"]
        for trivial_val in trivial_vals:
            with self.subTest(trivial_val=trivial_val):
                prov = {
                    "questionId": "q1",
                    "intentType": "definition",
                    "knowledgeNodeId": "kn1",
                    "evidenceText": "Valid substantive evidence statement.",
                    "sourceFile": trivial_val,
                    "sourceLocation": {"page": 1},
                }
                res = verify_provenance_chain(prov)
                self.assertFalse(bool(res), f"Trivial source file '{trivial_val}' should be rejected")
                self.assertTrue(any("trivial" in err.lower() or "sourcefile" in err.lower() for err in res.errors))

    def test_22_rejects_negative_location_coordinate(self):
        prov = {
            "questionId": "q1",
            "intentType": "definition",
            "knowledgeNodeId": "kn1",
            "evidenceText": "Valid substantive evidence statement.",
            "sourceFile": "ncert_xi.pdf",
            "sourceLocation": {"page": -5},
        }
        res = verify_provenance_chain(prov)
        self.assertFalse(bool(res))
        self.assertTrue(any("cannot be negative" in err for err in res.errors))

    def test_23_zero_offset_location_is_valid(self):
        corpus = "Starting fact text at byte zero."
        prov = {
            "questionId": "q1",
            "intentType": "definition",
            "knowledgeNodeId": "kn1",
            "evidenceText": "Starting fact text at byte zero.",
            "sourceFile": "doc.txt",
            "sourceLocation": {"offset": 0},
        }
        res = verify_provenance_chain(prov, source_corpus=corpus)
        self.assertTrue(bool(res))


class TestKnowledgeNodeAndCandidateQuestionBridges(unittest.TestCase):
    """Tests drop-in interoperability with KnowledgeNode and CandidateQuestion."""

    def test_24_from_knowledge_node_integration(self):
        node = KnowledgeNode(
            node_id="kn_geo_888",
            intent_type="cause_effect",
            primary_entity="Coriolis force",
            predicate="deflects winds",
            raw_evidence="The Coriolis force deflects winds to the right in the Northern Hemisphere.",
            source_location={"sourceId": "ncert_climate.pdf", "page": 78, "sentence_idx": 3},
        )
        record = ProvenanceRecord.from_knowledge_node(
            node=node,
            question_id="q_coriolis_1",
            question_stem="In which direction does the Coriolis force deflect winds in the Northern Hemisphere?"
        )
        self.assertEqual(record.question_id, "q_coriolis_1")
        self.assertEqual(record.intent_type, "cause/effect")
        self.assertEqual(record.knowledge_node_id, "kn_geo_888")
        self.assertEqual(record.source_file, "ncert_climate.pdf")
        self.assertEqual(record.source_location["page"], 78)
        self.assertTrue(record.verify_hash()[0])

    def test_25_provenance_tracker_pipeline_bridge(self):
        class DummyCandidateQuestion:
            def __init__(self, qid, stem):
                self.id = qid
                self.stem = stem
                self.provenance = None

        node = KnowledgeNode(
            node_id="kn_rock_12",
            intent_type="classification",
            primary_entity="Rocks",
            predicate="are classified into three major groups",
            raw_evidence="Rocks are classified into igneous, sedimentary, and metamorphic.",
            source_location={"sourceId": "geology.md", "line_start": 5},
        )
        cq = DummyCandidateQuestion("cq_001", "How are rocks classified?")
        tracker = ProvenanceTracker()
        tracker.bind_candidate_question(cq, node)

        self.assertIsNotNone(cq.provenance)
        self.assertEqual(cq.provenance["questionId"], "cq_001")
        self.assertEqual(cq.provenance["intentType"], "classification")
        self.assertEqual(cq.provenance["knowledgeNodeId"], "kn_rock_12")
        self.assertIn("provenanceHash", cq.provenance)

        # PipelineBridge verification call
        is_valid, errors = tracker.verify_provenance(cq)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestBatchAuditIntegrityAndRegistry(unittest.TestCase):
    """Tests audit_provenance_integrity and ProvenanceRegistry query/persistence."""

    def test_26_clean_batch_audit_returns_pass(self):
        records = [
            ProvenanceRecord.create(
                question_id=f"q_{i}",
                intent_type="definition",
                knowledge_node_id=f"kn_{i}",
                evidence_text=f"Educational fact number {i}.",
                source_file="ncert.txt",
                source_location={"page": i + 1},
            )
            for i in range(10)
        ]
        audit = audit_provenance_integrity(records)
        self.assertEqual(audit["total_records"], 10)
        self.assertEqual(audit["valid_records"], 10)
        self.assertEqual(audit["invalid_records"], 0)
        self.assertEqual(audit["tampered_records"], 0)
        self.assertEqual(audit["integrity_rate"], 1.0)
        self.assertEqual(audit["audit_verdict"], "PASS")

    def test_27_contaminated_batch_audit_detects_all_anomalies(self):
        clean = ProvenanceRecord.create(
            question_id="q_clean",
            intent_type="definition",
            knowledge_node_id="kn_clean",
            evidence_text="Clean fact.",
            source_file="ncert.txt",
            source_location={"page": 1},
        )
        tampered = clean.to_camel_dict()
        tampered["questionId"] = "q_tampered"
        tampered["evidenceText"] = "Altered fact."  # Tamper

        missing_src = {
            "questionId": "q_bad_src",
            "intentType": "definition",
            "knowledgeNodeId": "kn_bad",
            "evidenceText": "Some text.",
            "sourceFile": "",
            "sourceLocation": {"page": 2},
        }

        audit = audit_provenance_integrity([clean, tampered, missing_src])
        self.assertEqual(audit["total_records"], 3)
        self.assertEqual(audit["valid_records"], 1)
        self.assertEqual(audit["invalid_records"], 2)
        self.assertEqual(audit["tampered_records"], 1)
        self.assertEqual(audit["audit_verdict"], "REJECT")
        self.assertEqual(len(audit["failure_details"]), 2)

    def test_28_provenance_registry_indexing_and_export(self):
        reg = ProvenanceRegistry()
        rec1 = ProvenanceRecord.create(
            question_id="q_1",
            intent_type="definition",
            knowledge_node_id="kn_common",
            evidence_text="Fact 1.",
            source_file="fileA.txt",
            source_location={"page": 1},
        )
        rec2 = ProvenanceRecord.create(
            question_id="q_2",
            intent_type="process",
            knowledge_node_id="kn_common",
            evidence_text="Fact 2.",
            source_file="fileA.txt",
            source_location={"page": 2},
        )
        reg.register(rec1)
        reg.register(rec2)

        self.assertEqual(reg.count(), 2)
        self.assertEqual(reg.get_by_question_id("q_1"), rec1)
        self.assertEqual(len(reg.get_by_node_id("kn_common")), 2)
        self.assertEqual(len(reg.get_by_source_file("fileA.txt")), 2)

        # Export and re-import
        json_export = reg.export_json()
        new_reg = ProvenanceRegistry()
        admitted = new_reg.import_json(json_export)
        self.assertEqual(admitted, 2)
        self.assertIsNotNone(new_reg.get_by_question_id("q_2"))


class TestVerificationResultProtocol(unittest.TestCase):
    """Tests VerificationResult protocol compliance (__bool__, __iter__, __eq__)."""

    def test_29_verification_result_bool_and_unpacking(self):
        res_pass = VerificationResult(is_valid=True, errors=[])
        self.assertTrue(bool(res_pass))
        self.assertEqual(res_pass, True)

        # Tuple unpacking test
        valid, errors = res_pass
        self.assertTrue(valid)
        self.assertEqual(errors, [])

        res_fail = VerificationResult(is_valid=False, errors=["Error A", "Error B"])
        self.assertFalse(bool(res_fail))
        self.assertEqual(res_fail, False)

        valid_f, errors_f = res_fail
        self.assertFalse(valid_f)
        self.assertEqual(len(errors_f), 2)


if __name__ == "__main__":
    unittest.main()
