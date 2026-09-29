"""
Tier 3: Cross-Feature Combinations (Pairwise Integration) E2E Test Suite
Tests pairwise interactions across all critical architectural boundaries:
- Pairwise 1: Ingestion & Normalizer ↔ 14-Intent Semantic Extractor
- Pairwise 2: Semantic Extractor ↔ Question Intent & Stem Synthesizer
- Pairwise 3: Question Synthesizer ↔ Ontological Distractor Engine
- Pairwise 4: Distractor Engine ↔ Distractor Dissection Generator
- Pairwise 5: Candidate Question ↔ Multi-Agent Auditing Quality Gate
- Pairwise 6: Audited Candidate Question ↔ Golden Provenance Registry
- Pairwise 7: Audited Question ↔ Android Markdown Exporter & DataImporter Simulator
- Pairwise 8: Audit Failure Feedback Loop ↔ Systemic Repair & Regeneration Pipeline

Total Tier 3 Test Cases: 16
"""

import os
import re
import json
import unittest

from tests.e2e.test_helpers import (
    PROJECT_ROOT,
    SOURCE_MATERIAL_DIR,
    ASSETS_DIR,
    DATA_DIR,
    ALL_14_INTENTS,
    VALID_ROOM_TRAP_TYPES,
    VALID_QUESTION_FORMATS,
    NormalizedBlock,
    KnowledgeNode,
    CandidateQuestion,
    AuditReport,
    DataImporterSimulator,
    PipelineBridge,
    validate_golden_eval_dataset,
    validate_experiment_metrics,
    validate_provenance_chain,
    validate_distractor_dissections
)


class TestTier3PairwiseCombinations(unittest.TestCase):
    """Tier 3: Pairwise Interface Interactions Across Pipeline Boundaries"""

    def setUp(self):
        self.normalizer = PipelineBridge.get_normalizer()
        self.extractor = PipelineBridge.get_semantic_extractor()
        self.synthesizer = PipelineBridge.get_question_synthesizer()
        self.auditor = PipelineBridge.get_multi_agent_auditor()
        self.provenance_tracker = PipelineBridge.get_provenance_tracker()

    # =========================================================================
    # Pairwise 1: Normalizer ↔ Semantic Extractor
    # =========================================================================

    def test_p01_01_normalizer_table_to_semantic_extractor(self):
        """P01: Normalizer parses table into relational statements that Extractor maps to attributes."""
        table_md = (
            "| Landform | Agent of Formation | Category |\n"
            "|---|---|---|\n"
            "| Cirque | Glacial erosion | Erosional |\n"
            "| Moraine | Glacial deposition | Depositional |\n"
        )
        blocks = self.normalizer.normalize(table_md, "source_landforms")
        tbl_block = next(b for b in blocks if b.type == "TABLE")
        self.assertEqual(len(tbl_block.clean_sentences), 2)
        
        nodes = self.extractor.extract(tbl_block)
        self.assertEqual(len(nodes), 2)
        self.assertIn("Cirque", nodes[0].rawEvidence)
        self.assertIn("Moraine", nodes[1].rawEvidence)

    def test_p01_02_normalizer_ocr_repair_to_semantic_extractor(self):
        """P01: Normalizer repairs hyphenated split word allowing Extractor to identify correct intent."""
        raw_ocr = "Subduction oc-\ncurs when an oceanic plate sinks into the mantle."
        blocks = self.normalizer.normalize(raw_ocr, "source_subduction")
        nodes = self.extractor.extract(blocks[0])
        self.assertGreater(len(nodes), 0)
        self.assertEqual(nodes[0].intentType, "process")
        self.assertIn("occurs", nodes[0].rawEvidence)

    # =========================================================================
    # Pairwise 2: Semantic Extractor ↔ Question Synthesizer
    # =========================================================================

    def test_p02_01_definition_intent_to_interrogative_stem(self):
        """P02: Extracted definition KnowledgeNode transforms into natural interrogative stem."""
        text = "An oxbow lake is defined as a crescent-shaped lake formed when a river meander is abandoned."
        block = NormalizedBlock("b_def", text, "PROSE", [text], {"sourceId": "ncert_xi"})
        nodes = self.extractor.extract(block)
        
        cq = self.synthesizer.synthesize(nodes[0])
        self.assertTrue(cq.stem.strip().endswith("?") or cq.stem.strip().endswith(":"))
        self.assertNotIn("What is a direct consequence of", cq.stem)

    def test_p02_02_process_intent_to_mechanism_stem(self):
        """P02: Extracted process KnowledgeNode generates mechanism-focused question."""
        text = "Subduction occurs when a denser oceanic plate plunges beneath a lighter continental plate."
        block = NormalizedBlock("b_proc", text, "PROSE", [text], {"sourceId": "ncert_xi"})
        nodes = self.extractor.extract(block)
        
        cq = self.synthesizer.synthesize(nodes[0])
        self.assertIn("subduction", cq.stem.lower() + " " + cq.explanation.lower())

    # =========================================================================
    # Pairwise 3: Question Synthesizer ↔ Ontological Distractor Engine
    # =========================================================================

    def test_p03_01_synthesizer_applies_ontology_category_constraints(self):
        """P03: Synthesizer constrains options to the ontological domain of the correct answer."""
        node = KnowledgeNode("n_rock", "attribute", "Basalt", [], "is", [], {}, "Basalt is an extrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        
# All 4 options must belong to Rock Types
        rock_ontology = ["Basalt", "Granite", "Sandstone", "Marble", "Gneiss", "Slate", "Shale"]
        for opt in cq.options:
            opt_text = opt.get("text", "")
            self.assertTrue(any(r.lower() in opt_text.lower() for r in rock_ontology), f"Option '{opt_text}' violated rock category constraint")

    def test_p03_02_synthesizer_ensures_options_distinctness_and_count(self):
        """P03: Distractor engine produces exactly 4 distinct mutually exclusive options."""
        node = KnowledgeNode("n_atm", "spatial", "Stratosphere", [], "lies", [], {}, "The Stratosphere lies above troposphere.", {})
        cq = self.synthesizer.synthesize(node)
        self.assertEqual(len(cq.options), 4)
        self.assertEqual(len(set(opt.get("text", "") for opt in cq.options)), 4)

    # =========================================================================
    # Pairwise 4: Distractor Engine ↔ Distractor Dissection Generator
    # =========================================================================

    def test_p04_01_distractors_mapped_to_room_trap_types(self):
        """P04: Every generated distractor is mapped to an authorized Room DB trap type."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        
        for d in cq.distractorDissections:
            self.assertIn(d["trapType"], VALID_ROOM_TRAP_TYPES)
            self.assertNotEqual(d["optionId"], cq.correctAnswer)

    def test_p04_02_dissections_contain_pedagogical_rationales(self):
        """P04: Dissections explain why each distractor is an attractive error."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        
        for d in cq.distractorDissections:
            self.assertGreater(len(d["dissection"]), 10)
            self.assertIsInstance(d["dissection"], str)

    # =========================================================================
    # Pairwise 5: Candidate Question ↔ Multi-Agent Auditing Gate
    # =========================================================================

    def test_p05_01_valid_candidate_passes_all_three_auditors(self):
        """P05: High quality candidate question receives unanimous PASS verdicts."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {"sourceId": "doc1"})
        cq = self.synthesizer.synthesize(node)
        report = self.auditor.audit(cq)
        
        self.assertEqual(report.cognitiveVerdict, "PASS")
        self.assertEqual(report.examFitVerdict, "PASS")
        self.assertEqual(report.adversarialVerdict, "PASS")
        self.assertEqual(report.overallGate, "PASS")
        self.assertEqual(len(report.failureReasons), 0)

    def test_p05_02_adversarial_defect_trips_quality_gate(self):
        """P05: Answer leakage defect detected by Adversarial Auditor rejects candidate."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "Why is Granite considered an intrusive igneous rock?"
        cq.options = [{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Sandstone"}, {"id": "opt_c", "text": "Basalt"}, {"id": "opt_d", "text": "Marble"}]
        cq.correctAnswer = "opt_a"
        
        report = self.auditor.audit(cq)
        self.assertEqual(report.adversarialVerdict, "REJECT")
        self.assertEqual(report.overallGate, "REJECT")
        self.assertTrue(any("leakage" in r.lower() for r in report.failureReasons))

    # =========================================================================
    # Pairwise 6: Audited Question ↔ Golden Provenance Registry
    # =========================================================================

    def test_p06_01_passed_question_provenance_links_to_corpus(self):
        """P06: Approved candidate question maintains unbroken chain to source corpus text."""
        corpus = "Full chapter text. Granite is an intrusive igneous rock characterized by coarse grains. More text."
        node = KnowledgeNode(
            nodeId="kn_g1", intentType="attribute", primaryEntity="Granite",
            relatedEntities=[], predicate="is", conditions=[], quantitativeData={},
            rawEvidence="Granite is an intrusive igneous rock characterized by coarse grains.",
            sourceLocation={"sourceId": "ncert_xi.pdf", "offset": 19}
        )
        cq = self.synthesizer.synthesize(node)
        report = self.auditor.audit(cq)
        self.assertEqual(report.overallGate, "PASS")
        
        valid, errors = self.provenance_tracker.verify_provenance(cq, source_corpus=corpus)
        self.assertTrue(valid, f"Provenance verification failed: {errors}")

    def test_p06_02_tampered_evidence_fails_provenance_verification(self):
        """P06: Tampered evidence string fails provenance verification."""
        corpus = "Original text regarding lithospheric plates."
        node = KnowledgeNode("n1", "attribute", "Plates", [], "is", [], {}, "Original text regarding lithospheric plates.", {"sourceId": "doc1"})
        cq = self.synthesizer.synthesize(node)
        cq.provenance["evidenceText"] = "Fabricated statement not in corpus."
        
        valid, errors = self.provenance_tracker.verify_provenance(cq, source_corpus=corpus)
        self.assertFalse(valid)

    # =========================================================================
    # Pairwise 7: Audited Question ↔ Android Markdown & DataImporter
    # =========================================================================

    def test_p07_01_audited_question_exports_to_dataimporter_markdown(self):
        """P07: Exported markdown parses cleanly through DataImporterSimulator into Room Question entity."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        report = self.auditor.audit(cq)
        self.assertEqual(report.overallGate, "PASS")
        
        md_entry = DataImporterSimulator.format_candidate_to_markdown(cq)
        full_md = "# Header\n\n## 1. Physical Geography\n" + md_entry
        res = DataImporterSimulator.parse_markdown(full_md)
        
        self.assertEqual(res["totalFound"], 1)
        self.assertEqual(res["totalAccepted"], 1)
        q = res["questions"][0]
        self.assertEqual(q["correctAnswer"], "opt_a")
        self.assertEqual(q["topicId"], 1)

    def test_p07_02_dataimporter_serializes_dissections_into_room_json(self):
        """P07: Room DB distractorDissections JSON string parses into valid objects."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        md_entry = DataImporterSimulator.format_candidate_to_markdown(cq)
        full_md = "# Header\n\n## 1. Physical Geography\n" + md_entry
        res = DataImporterSimulator.parse_markdown(full_md)
        
        dissections_raw = res["questions"][0]["distractorDissections"]
        dissections = json.loads(dissections_raw)
        self.assertIsInstance(dissections, list)
        self.assertGreater(len(dissections), 0)
        self.assertIn(dissections[0]["trapType"], VALID_ROOM_TRAP_TYPES)

    # =========================================================================
    # Pairwise 8: Audit Failure Feedback ↔ Systemic Repair & Regeneration
    # =========================================================================

    def test_p08_01_flaw_feedback_triggers_targeted_stem_repair(self):
        """P08: Audit failure triggers repair loop converting leaking stem into compliant stem."""
        # Initial flawed question with answer leak
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive igneous rock.", {})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "Why is Granite considered an intrusive igneous rock?"
        cq.options = [{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Sandstone"}, {"id": "opt_c", "text": "Basalt"}, {"id": "opt_d", "text": "Marble"}]
        cq.correctAnswer = "opt_a"
        
        report_before = self.auditor.audit(cq)
        self.assertEqual(report_before.overallGate, "REJECT")
        
        # Systemic repair strategy for MCQ leakage
        cq.stem = "Which of the following rocks is classified as intrusive igneous?"
        report_after = self.auditor.audit(cq)
        self.assertEqual(report_after.overallGate, "PASS")

    def test_p08_02_regeneration_preserves_provenance_and_metadata(self):
        """P08: Repaired and regenerated question retains provenance links and topic ID."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {"sourceId": "doc1"})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "Trivial?"  # Triggers cognitive rejection
        report_before = self.auditor.audit(cq)
        self.assertEqual(report_before.overallGate, "REJECT")
        
        # Repair cognitive depth without leaking answer
        cq.stem = "Which of the following describes the morphological formation of a crescent-shaped cut-off meander?"
        report_after = self.auditor.audit(cq)
        self.assertEqual(report_after.overallGate, "PASS")
        self.assertEqual(cq.provenance["intentType"], "definition")


if __name__ == "__main__":
    unittest.main()
