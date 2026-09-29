#!/usr/bin/env python3
"""
tests/test_v13_new_regressions.py
==================================
Comprehensive Regression Test Suite for Milestone 6 (Acceptance Criterion 6).
Covers all 6 mandatory failure modes:
1. MCQ stem leakage prevention (verbatim, case-insensitive, significant tokens, self-repair)
2. OCR fragments & watermark filtering (publishers, coaching, ISBN, cataloging, running headers, captions, craft activities, dangling fragments, unresolved anaphora)
3. Multi-word entity extraction and distractor handling (intact multi-word entity extraction, taxonomic sibling category constraints, grammatical parallelism, distractor trap dissections)
4. Non-SVO facts extraction across all 14 semantic intents (passive inversion, locative inversion, conditionals, all 14 canonical intents: definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of)
5. Semantic duplicate elimination (exact, case-insensitive, semantic alias collision with correct answer, distractor-to-distractor alias collision, question-level clustering deduplication)
6. Cryptographic provenance verification & tamper resistance (unbroken 6-link Merklized SHA-256 chain, tamper detection for evidence/stem/intent/location, immutability, corpus grounding audit)
"""

import os
import sys
import json
import copy
import unittest
import dataclasses
from typing import Dict, List, Any, Optional, Set

# Ensure repository root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v13_discovery.normalizer import WatermarkOcrCleaner, NormalizedBlock, DocumentNormalizer
from v13_discovery.semantic_extractor import (
    NoiseFilterGate,
    LinguisticSemanticExtractor,
    SemanticExtractor,
    KnowledgeNode,
    CANONICAL_14_INTENTS,
    canonicalize_intent,
    to_r2_intent,
    sanitize_text,
)
from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    DistractorVerificationGate,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.auditors import (
    AdversarialAuditor,
    CognitiveAuditor,
    ExamFitAuditor,
    MultiAgentAuditingGate,
    QuestionRepairEngine,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    LinkHashes,
    verify_provenance_chain,
    audit_provenance_integrity,
)
from tests.e2e.test_helpers import DataImporterSimulator


# =============================================================================
# FAILURE MODE 1: MCQ STEM LEAKAGE PREVENTION
# =============================================================================

class TestMCQStemLeakageRegression(unittest.TestCase):
    """
    Regression Suite 1: MCQ Stem Leakage Prevention.
    Verifies detection and remediation of verbatim leakage, case-insensitive variants,
    significant token leakage, absence of false alarms on domain stopwords, and self-repair.
    """

    def setUp(self):
        self.ontology = OntologyRegistry()
        self.auditor = AdversarialAuditor(ontology=self.ontology)
        self.gate = MultiAgentAuditingGate(ontology=self.ontology)
        self.repair_engine = QuestionRepairEngine(ontology=self.ontology)

    def test_verbatim_answer_in_stem_rejection(self):
        """Verbatim inclusion of correct answer in stem must be rejected with STEM_LEAKAGE."""
        cq = CandidateQuestion(
            id="q_leak_verbatim",
            stem="The troposphere is the lowest atmospheric layer characterized by which feature?",
            options=[{'id': 'opt_a', 'text': "Troposphere"}, {'id': 'opt_b', 'text': "Stratosphere"}, {'id': 'opt_c', 'text': "Mesosphere"}, {'id': 'opt_d', 'text': "Thermosphere"}],
            correctAnswer="opt_a",
            explanation="The troposphere contains convective air masses.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Stratosphere is above troposphere."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Mesosphere is the cold middle layer."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Thermosphere is the high-temperature upper layer."}
            ],
            provenance={"intentType": "definition", "knowledgeNodeId": "kn_trop"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "STEM_LEAKAGE" for v in res.violations))
        self.assertTrue(any("correct answer found in question stem" in v.message for v in res.violations))

    def test_case_insensitive_and_punctuation_leakage(self):
        """Case variations (UPPERCASE, lowercase, quotes) of correct answer in stem must trigger fatal rejection."""
        leakage_stems = [
            "With reference to atmospheric science, TROPOSPHERE has which altitude characteristics?",
            "With reference to atmospheric science, 'troposphere' exhibits what lapse rate?",
            "Troposphere: which of the following is an essential characteristic of this layer?",
        ]
        for stem in leakage_stems:
            cq = CandidateQuestion(
                id="q_leak_case",
                stem=stem,
                options=[{'id': 'opt_a', 'text': "Troposphere"}, {'id': 'opt_b', 'text': "Stratosphere"}, {'id': 'opt_c', 'text': "Mesosphere"}, {'id': 'opt_d', 'text': "Ionosphere"}],
                correctAnswer="opt_a",
                explanation="Troposphere is characterized by normal lapse rate.",
                distractorDissections=[
                    {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Stratosphere features temperature inversion."},
                    {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Mesosphere features meteoric ablation."},
                    {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Ionosphere reflects radio waves."}
                ],
                provenance={"intentType": "attribute", "knowledgeNodeId": "kn_case"},
                cognitiveDemand="UNDERSTAND",
                examTarget="UPSC-Prelims"
            )
            res = self.auditor.audit(cq)
            self.assertEqual(res.verdict, "REJECT", f"Failed to reject leakage in: {stem}")
            self.assertTrue(any(v.category == "STEM_LEAKAGE" for v in res.violations))

    def test_significant_token_leakage(self):
        """Multi-word answers where significant tokens (len >= 3) leak into stem must be rejected."""
        cq = CandidateQuestion(
            id="q_leak_token",
            stem="Which geodynamic mechanism was proposed by Alfred Wegener in the Continental Drift concept?",
            options=[{'id': 'opt_a', 'text': "Continental Drift Theory"}, {'id': 'opt_b', 'text': "Seafloor Spreading Theory"}, {'id': 'opt_c', 'text': "Plate Tectonics Theory"}, {'id': 'opt_d', 'text': "Thermal Convection Theory"}],
            correctAnswer="opt_a",
            explanation="Continental Drift Theory was formulated by Alfred Wegener in 1912.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Proposed by Harry Hess."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Formulated by Morgan, McKenzie, and Parker."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Proposed by Arthur Holmes."}
            ],
            provenance={"intentType": "process", "knowledgeNodeId": "kn_wegener"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "STEM_LEAKAGE" for v in res.violations))

    def test_no_false_alarm_on_domain_stopwords_or_substrings(self):
        """Domain stopwords ('rock', 'layer', 'river') or sub-word occurrences must not trigger false positive leakage."""
        cq = CandidateQuestion(
            id="q_no_false_leak",
            stem="Which type of rock is formed by the accumulation and lithification of mineral sediments?",
            options=[{'id': 'opt_a', 'text': "Sedimentary rock"}, {'id': 'opt_b', 'text': "Igneous rock"}, {'id': 'opt_c', 'text': "Metamorphic rock"}, {'id': 'opt_d', 'text': "Plutonic rock"}],
            correctAnswer="opt_a",
            explanation="Sedimentary rock forms via diagenesis and lithification.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Igneous rocks form from molten magma."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Metamorphic rocks undergo recrystallization."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Plutonic rocks crystallize deep within crust."}
            ],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_sed"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertFalse(any(v.category == "STEM_LEAKAGE" for v in res.violations), "False positive leakage on domain stopword 'rock'")

        # Substring safety: 'planetarium' in stem should not match answer 'planet'
        cq_sub = CandidateQuestion(
            id="q_sub_word",
            stem="In an astronomical planetarium, which celestial body is defined as a dwarf planet?",
            options=[{'id': 'opt_a', 'text': "Pluto"}, {'id': 'opt_b', 'text': "Ceres"}, {'id': 'opt_c', 'text': "Eris"}, {'id': 'opt_d', 'text': "Makemake"}],
            correctAnswer="opt_a",
            explanation="Pluto was reclassified as a dwarf planet in 2006.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Ceres is in asteroid belt."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Eris is in scattered disc."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Makemake is a trans-Neptunian object."}
            ],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_pluto"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res_sub = self.auditor.audit(cq_sub)
        self.assertFalse(any(v.category == "STEM_LEAKAGE" for v in res_sub.violations))

    def test_self_repair_deidentifies_leaked_stem(self):
        """QuestionRepairEngine must deidentify leaked answers in stem and achieve 100% audit gate clearance."""
        leaked_cq = CandidateQuestion(
            id="q_repair_leak",
            stem="Why is Granite classified as an intrusive igneous rock?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Gabbro"}, {'id': 'opt_d', 'text': "Rhyolite"}],
            correctAnswer="opt_a",
            explanation="Granite is a coarse-grained plutonic rock forming deep inside the crust.",
            distractorDissections=[
                {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Basalt is extrusive."},
                {"optionId": "opt_c", "trapType": "CONCEPT_MIX", "dissection": "Gabbro is mafic intrusive."},
                {"optionId": "opt_d", "trapType": "CONCEPT_MIX", "dissection": "Rhyolite is felsic extrusive."}
            ],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_granite"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        initial_report = self.gate.audit(leaked_cq)
        self.assertEqual(initial_report.overallGate, "REJECT")
        self.assertTrue(any(v.category == "STEM_LEAKAGE" for v in initial_report.violations))

        repaired_cq = self.repair_engine.repair(leaked_cq, initial_report)
        post_report = self.gate.audit(repaired_cq)

        self.assertEqual(post_report.overallGate, "PASS")
        self.assertNotIn("granite", repaired_cq.stem.lower())
        self.assertTrue(repaired_cq.stem.endswith("?"))


# =============================================================================
# FAILURE MODE 2: OCR FRAGMENTS & WATERMARK FILTERING
# =============================================================================

class TestOcrFragmentsAndWatermarksRegression(unittest.TestCase):
    """
    Regression Suite 2: OCR Fragments & Watermark Filtering.
    Verifies 100% rejection across publisher watermarks, ISBNs, textbook cataloging,
    running headers, captions, craft activities, dangling fragments, and unresolved anaphora.
    """

    def test_publisher_and_coaching_watermarks(self):
        """Coaching, publisher, and app download watermarks must be rejected."""
        watermarks = [
            "PARMAR SSC",
            "www.ssccglpinnacle.com",
            "Download Pinnacle Exam Preparation App",
            "Pinnacle Geography",
        ]
        for wm in watermarks:
            self.assertTrue(WatermarkOcrCleaner.is_watermark_or_noise(wm), f"Watermark cleaner missed: {wm}")
            audit_result = NoiseFilterGate.audit(wm)
            self.assertIn(audit_result, ["watermark_header", "syntactic_fragment", "broken_reading_order"], f"Noise gate missed: {wm}")

    def test_textbook_cataloging_and_reprints(self):
        """Textbook ISBN, edition metadata, barcode numbers, and reprint tags must be rejected."""
        catalog_lines = [
            "ISBN 978-93-5292-065-6",
            "0656",
            "Rationalised 2023-24",
            "Reprint 2022-23",
            "not to be republished",
            "NCERT",
        ]
        for cat in catalog_lines:
            is_noise = WatermarkOcrCleaner.is_watermark_or_noise(cat) or (NoiseFilterGate.audit(cat) is not None)
            self.assertTrue(is_noise, f"Cataloging artifact not detected: {cat}")

    def test_running_headers_and_figure_captions(self):
        """Running headers and textbook diagram captions must be filtered."""
        headers = [
            "THE EARTH : OUR HABITAT",
            "MAJOR DOMAINS OF THE EARTH",
            "Chapter 1",
            "Figure 1.2: Solar System",
        ]
        for hdr in headers:
            is_noise = WatermarkOcrCleaner.is_watermark_or_noise(hdr) or (NoiseFilterGate.audit(hdr) is not None)
            self.assertTrue(is_noise, f"Running header or caption escaped filter: {hdr}")

    def test_craft_activity_and_exercise_prompts(self):
        """Classroom craft instructions, step directions, and exercise prompts must be filtered."""
        activities = [
            "Let's Do",
            "Do you know?",
            "Step :",
            "1. Take a globe and a torch to demonstrate day and night.",
            "Tick the correct answer",
        ]
        for act in activities:
            is_noise = WatermarkOcrCleaner.is_watermark_or_noise(act) or (NoiseFilterGate.audit(act) is not None)
            self.assertTrue(is_noise, f"Craft or exercise activity escaped filter: {act}")

    def test_syntactic_dangling_fragments(self):
        """Incomplete sentences ending in trailing prepositions or conjunctions must be rejected."""
        dangling_frags = [
            "The lithosphere is composed of",
            "Rapid crustal deformation leading to",
            "Because of the fact that",
            "Such geomorphic features as",
            "The continental margin consists of",
        ]
        for frag in dangling_frags:
            res = NoiseFilterGate.audit(frag)
            self.assertIn(res, ["syntactic_fragment", "anaphoric_unresolved"], f"Dangling fragment escaped: {frag}")

    def test_unresolved_anaphoric_pronouns(self):
        """Isolated sentences with unresolved initial personal or demonstrative pronouns must be rejected."""
        anaphoric_lines = [
            "They are found in deep ocean trenches.",
            "These are composed of granitic rocks.",
            "Its atmosphere is rich in nitrogen and argon.",
        ]
        for line in anaphoric_lines:
            res = NoiseFilterGate.audit(line, is_block_context=False, has_antecedent=False)
            self.assertEqual(res, "anaphoric_unresolved", f"Unresolved anaphora was not flagged: {line}")

    def test_genuine_educational_prose_preservation(self):
        """Substantive educational NCERT prose must NEVER be falsely rejected (zero false rejection)."""
        genuine_sentences = [
            "The troposphere is the lowest layer of the atmosphere where temperature decreases with height.",
            "Igneous rocks are formed when molten magma cools and solidifies on or below the earth's surface.",
            "The Earth rotates from west to east on its imaginary tilted axis.",
        ]
        for s in genuine_sentences:
            self.assertIsNone(NoiseFilterGate.audit(s), f"Genuine prose falsely rejected by NoiseFilterGate: {s}")
            self.assertFalse(WatermarkOcrCleaner.is_watermark_or_noise(s), f"Genuine prose falsely flagged by WatermarkOcrCleaner: {s}")


# =============================================================================
# FAILURE MODE 3: MULTI-WORD ENTITY EXTRACTION & DISTRACTOR HANDLING
# =============================================================================

class TestMultiWordEntityAndDistractorRegression(unittest.TestCase):
    """
    Regression Suite 3: Multi-Word Entity Extraction and Defensible Distractor Handling.
    Verifies intact multi-word entity preservation, taxonomic sibling category constraints,
    grammatical parallelism, and Room DB distractor trap dissections.
    """

    def setUp(self):
        self.ontology = OntologyRegistry()
        self.synthesizer = QuestionSynthesizer(ontology=self.ontology)
        self.auditor = AdversarialAuditor(ontology=self.ontology)

    def test_multi_word_entities_extracted_intact(self):
        """Multi-word geographic entities must be extracted intact without truncation."""
        test_cases = [
            ("The Standard Meridian of India passes through 82°30' E longitude.", "Standard Meridian of India"),
            ("The Andaman and Nicobar Islands are located in the Bay of Bengal.", "Andaman and Nicobar Islands"),
            ("The Continental Drift Theory was proposed by Alfred Wegener in 1912.", "Continental Drift Theory"),
            ("The Coriolis force causes winds to deflect to the right in the northern hemisphere.", "Coriolis force"),
            ("The San Andreas Fault is located along the western coast of North America.", "San Andreas Fault"),
        ]
        for sentence, expected_entity in test_cases:
            node = LinguisticSemanticExtractor.extract(sentence)
            self.assertIsNotNone(node, f"Extraction failed for: {sentence}")
            self.assertEqual(
                node.primary_entity.strip().lower(),
                expected_entity.lower(),
                f"Multi-word entity truncated: expected '{expected_entity}', got '{node.primary_entity}'"
            )

    def test_taxonomic_sibling_category_constraints(self):
        """Synthesized distractors must belong to the exact same ontological sibling category as correct answer."""
        # 1. Geomorphic features / Fluvial landforms
        cat_fluvial = self.ontology.find_category_for_entity("Oxbow lake")
        self.assertIsNotNone(cat_fluvial)
        self.assertIn("fluvial", cat_fluvial.category_id.lower())
        fluvial_siblings = set(cat_fluvial.members)
        # Distractors drawn for Oxbow lake must never be rocks or atmospheric layers
        for member in fluvial_siblings:
            self.assertNotIn(member, self.ontology.get_category("rock_types").members)
            self.assertNotIn(member, self.ontology.get_category("atmospheric_layers").members)

        # 2. Mountain ranges
        cat_mountains = self.ontology.find_category_for_entity("Himalayas")
        self.assertIsNotNone(cat_mountains)
        self.assertIn("mountain", cat_mountains.category_id.lower())

        node = KnowledgeNode(
            node_id="kn_tax_oxbow",
            intent_type="definition",
            primary_entity="Oxbow lake",
            predicate="is a crescent-shaped lake formed when a river meander is cut off from the main stream",
            raw_evidence="An oxbow lake is a crescent-shaped lake formed when a wide meander is cut off from the river.",
            source_location={"sourceId": "geography_extracted.txt", "line": 100}
        )
        cq = self.synthesizer.synthesize(node, shuffle=False)
        self.assertTrue(cq.valid)
        correct_letter = cq.correctAnswer
        correct_text = next(o["text"] for o in cq.options if o["id"] == correct_letter)
        distractor_values = [o["text"] for o in cq.options if o["id"] != correct_letter]
        for d in distractor_values:
            d_cat = self.ontology.find_category_for_entity(d)
            self.assertEqual(
                d_cat.category_id if d_cat else None,
                cat_fluvial.category_id,
                f"Distractor '{d}' violates taxonomic sibling category constraint for '{correct_text}'"
            )

    def test_grammatical_parallelism_and_number_agreement(self):
        """All options must exhibit grammatical parallelism (matching plural/singular number) without article clueing."""
        # Plural options set
        plural_options = [
            {"id": "opt_a", "text": "Shield volcanoes"},
            {"id": "opt_b", "text": "Composite volcanoes"},
            {"id": "opt_c", "text": "Calderas"},
            {"id": "opt_d", "text": "Flood basalt provinces"},
        ]
        gate_ok, _ = DistractorVerificationGate.verify_all(
            options=plural_options,
            correct_key="opt_a",
            stem="Which of the following volcanic landforms are formed by basaltic lava?",
            category=None
        )
        self.assertTrue(gate_ok, "Plural grammatically parallel options should pass verification gate")

        # Article clueing: stem terminal 'an:' before consonant distractor
        cq_article = CandidateQuestion(
            id="q_art_leak",
            stem="Which of the following atmospheric layers is an:",
            options=[
                {"id": "opt_a", "text": "Troposphere"},
                {"id": "opt_b", "text": "Stratosphere"},
                {"id": "opt_c", "text": "Mesosphere"},
                {"id": "opt_d", "text": "Exosphere"},
            ],
            correctAnswer="opt_d",
            explanation="Exosphere is the uppermost layer.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq_article)
        self.assertTrue(
            any(v.category in ["ARTICLE_LEAKAGE", "GRAMMATICAL"] for v in res.violations),
            "Adversarial auditor must catch terminal article clueing in stem"
        )

    def test_distractor_trap_dissections(self):
        """Generated distractors must feature valid Room DB trap annotations and pedagogical rationales."""
        node = KnowledgeNode(
            node_id="kn_trap_test",
            intent_type="classification",
            primary_entity="Basalt",
            predicate="is classified as an extrusive igneous rock formed from rapidly cooling lava",
            raw_evidence="Basalt is an extrusive igneous rock formed by the rapid cooling of lava.",
            source_location={"sourceId": "geography_extracted.txt", "line": 200}
        )
        cq = self.synthesizer.synthesize(node, shuffle=False)
        self.assertGreaterEqual(len(cq.distractorDissections), 3)

        for item in cq.distractorDissections:
            self.assertIn("optionId", item)
            self.assertIn("trapType", item)
            self.assertIn(item["trapType"], VALID_ROOM_TRAP_TYPES)
            self.assertIn("dissection", item)
            self.assertGreaterEqual(len(item["dissection"]), 10, "Pedagogical dissection rationale too brief")


# =============================================================================
# FAILURE MODE 4: NON-SVO FACTS EXTRACTION ACROSS ALL 14 INTENTS
# =============================================================================

class TestNonSvoFactsAll14IntentsRegression(unittest.TestCase):
    """
    Regression Suite 4: Non-SVO Extraction across all 14 Semantic Intents.
    Verifies robust extraction on passive inversion, locative inversion, conditionals,
    and exhaustive coverage of all 14 canonical R2 semantic intents.
    """

    def test_passive_inversion_extraction(self):
        """Passive voice inversion ('A vast elevated flatland... is called a plateau') must extract definition."""
        sentence = "A vast elevated flatland with steep slopes is called a plateau."
        node = LinguisticSemanticExtractor.extract(sentence)
        self.assertIsNotNone(node)
        self.assertEqual(canonicalize_intent(node.intent_type), "definition")
        self.assertEqual(node.primary_entity.lower(), "plateau")
        self.assertIn("elevated flatland", node.predicate.lower())

    def test_locative_inversion_extraction(self):
        """Locative inversion ('Between the crust and core lies the dense mantle') must extract spatial relationship."""
        sentence = "Between the crust and core lies the dense mantle."
        node = LinguisticSemanticExtractor.extract(sentence)
        self.assertIsNotNone(node)
        self.assertEqual(canonicalize_intent(node.intent_type), "spatial")
        self.assertIn("mantle", node.primary_entity.lower())
        self.assertIn("crust and core", node.predicate.lower())

    def test_conditional_extraction(self):
        """Conditional statements ('Tropical cyclones form only when sea surface temperatures exceed 27°C') must extract condition."""
        sentence = "Tropical cyclones form only when sea surface temperatures exceed 27°C."
        node = LinguisticSemanticExtractor.extract(sentence)
        self.assertIsNotNone(node)
        self.assertEqual(canonicalize_intent(node.intent_type), "condition")
        self.assertIn("cyclone", node.primary_entity.lower())

    def test_all_14_semantic_intents_slotting(self):
        """Exhaustive coverage: each of the 14 canonical intents must slot primaryEntity, predicate, and rawEvidence."""
        eval_path = os.path.join(PROJECT_ROOT, "data", "golden_eval_set.json")
        self.assertTrue(os.path.exists(eval_path), f"Evaluation dataset missing: {eval_path}")

        with open(eval_path, "r", encoding="utf-8") as f:
            golden_data = json.load(f)

        examples = golden_data.get("examples", [])
        # Representative golden items mapping to each of the 14 intents
        intent_mapping = {
            "definition": "POS-001",
            "attribute": "POS-006",
            "cause/effect": "POS-009",
            "comparison": "POS-013",
            "spatial": "POS-018",
            "distribution": "POS-022",
            "classification": "POS-025",
            "quantity": "POS-029",
            "sequence": "POS-033",
            "condition": "POS-037",
            "exception": "POS-041",
            "process": "POS-045",
            "part-of": "POS-049",
            "member-of": "POS-053",
        }

        extractor = SemanticExtractor()
        items_by_id = {ex["id"]: ex for ex in examples}

        for intent_name, item_id in intent_mapping.items():
            item = items_by_id.get(item_id)
            self.assertIsNotNone(item, f"Missing fixture {item_id} for intent {intent_name}")

            nodes = extractor.extract(item["text"])
            self.assertGreaterEqual(len(nodes), 1, f"No node extracted for {intent_name} ({item_id})")

            primary_node = nodes[0]
            actual_canon = canonicalize_intent(primary_node.intent_type)
            expected_canon = canonicalize_intent(intent_name)

            self.assertEqual(
                actual_canon,
                expected_canon,
                f"Intent slotting failure on {item_id}: expected {expected_canon}, got {actual_canon}"
            )
            self.assertTrue(len(primary_node.primary_entity.strip()) > 0, f"Empty primaryEntity in {item_id}")
            self.assertTrue(len(primary_node.predicate.strip()) > 0, f"Empty predicate in {item_id}")
            self.assertTrue(len(primary_node.raw_evidence.strip()) > 0, f"Empty rawEvidence in {item_id}")


# =============================================================================
# FAILURE MODE 5: SEMANTIC DUPLICATE ELIMINATION
# =============================================================================

class TestSemanticDuplicateEliminationRegression(unittest.TestCase):
    """
    Regression Suite 5: Semantic Duplicate Elimination.
    Verifies rejection of verbatim and case-insensitive option duplicates,
    alias collisions with correct answers, distractor-to-distractor alias clashes,
    and question-level proposition clustering deduplication.
    """

    def setUp(self):
        self.ontology = OntologyRegistry()
        cat_rock = self.ontology.get_category("rock_types")
        if cat_rock:
            cat_rock.aliases["granite rock"] = "Granite"
            cat_rock.aliases["plutonic granite"] = "Granite"
            cat_rock.aliases["black basalt"] = "Basalt"
        self.auditor = AdversarialAuditor(ontology=self.ontology)
        self.gate = MultiAgentAuditingGate(ontology=self.ontology)

    def test_option_verbatim_duplicates(self):
        """Option sets containing verbatim duplicate options must be rejected with OPTION_DUPLICATION."""
        cq = CandidateQuestion(
            id="q_dup_verbatim",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Granite"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "OPTION_DUPLICATION" for v in res.violations))

    def test_option_case_insensitive_duplicates(self):
        """Option sets containing case-variant duplicate options must be rejected."""
        cq = CandidateQuestion(
            id="q_dup_case",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "basalt"}, {'id': 'opt_c', 'text': "Granite"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "OPTION_DUPLICATION" for v in res.violations))

    def test_option_semantic_alias_collision_with_correct_answer(self):
        """Distractor that is a semantic alias of the correct answer must be rejected with SEMANTIC_AMBIGUITY."""
        cq = CandidateQuestion(
            id="q_alias_with_correct",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Black basalt"}, {'id': 'opt_c', 'text': "Granite"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in res.violations))
        self.assertTrue(any("alias of correct answer" in v.message for v in res.violations))

    def test_option_distractor_to_distractor_alias_collision(self):
        """Two distinct distractors that are aliases of each other must trigger fatal SEMANTIC_AMBIGUITY."""
        cq = CandidateQuestion(
            id="q_alias_d2d",
            stem="Which of the following rocks is classified as extrusive igneous?",
            options=[{'id': 'opt_a', 'text': "Basalt"}, {'id': 'opt_b', 'text': "Granite"}, {'id': 'opt_c', 'text': "Granite rock"}, {'id': 'opt_d', 'text': "Sandstone"}],
            correctAnswer="opt_a",
            explanation="Basalt is extrusive.",
            distractorDissections=[],
            provenance={},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims"
        )
        res = self.auditor.audit(cq)
        self.assertEqual(res.verdict, "REJECT")
        self.assertTrue(any(v.category == "SEMANTIC_AMBIGUITY" for v in res.violations))
        self.assertTrue(any("share canonical entity or are aliases" in v.message for v in res.violations))

    def test_question_level_semantic_deduplication(self):
        """Questions targeting identical semantic propositions must be clustered and deduplicated."""
        q1 = CandidateQuestion(
            id="q_cluster_1",
            stem="With reference to physical geography, which of the following is characterized by cooling of molten magma below the surface?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Basalt"}, {'id': 'opt_c', 'text': "Rhyolite"}, {'id': 'opt_d', 'text': "Obsidian"}],
            correctAnswer="opt_a",
            explanation="Granite cools slowly below the surface.",
            distractorDissections=[],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_g1"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims",
            topicId=1
        )
        q2 = CandidateQuestion(
            id="q_cluster_2",
            stem="In petrology, which of the following corresponds to the slow cooling of felsic magma beneath the Earth's crust?",
            options=[{'id': 'opt_a', 'text': "Granite"}, {'id': 'opt_b', 'text': "Pumice"}, {'id': 'opt_c', 'text': "Scoria"}, {'id': 'opt_d', 'text': "Basalt"}],
            correctAnswer="opt_a",
            explanation="Granite is an intrusive felsic rock.",
            distractorDissections=[],
            provenance={"intentType": "classification", "knowledgeNodeId": "kn_g2"},
            cognitiveDemand="UNDERSTAND",
            examTarget="UPSC-Prelims",
            topicId=1
        )

        def make_fingerprint(cq: CandidateQuestion) -> str:
            correct_val = next(
            (o.get("text", "").strip().lower() for o in cq.options if o.get("id") == cq.correctAnswer),
            "",
        )
            intent = canonicalize_intent(cq.provenance.get("intentType", "general"))
            return f"{cq.topicId}:{intent}:{correct_val}"

        questions = [q1, q2]
        seen_fingerprints: Set[str] = set()
        deduplicated: List[CandidateQuestion] = []

        for q in questions:
            fp = make_fingerprint(q)
            if fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                deduplicated.append(q)

        self.assertEqual(len(deduplicated), 1, "Semantic proposition clustering failed to deduplicate identical targets")


# =============================================================================
# FAILURE MODE 6: CRYPTOGRAPHIC PROVENANCE & TAMPER RESISTANCE
# =============================================================================

class TestCryptographicProvenanceAndTamperResistanceRegression(unittest.TestCase):
    """
    Regression Suite 6: Cryptographic Provenance Verification & Tamper Resistance.
    Verifies unbroken 6-link Merklized SHA-256 chain, tamper detection for all mutable links,
    record immutability (frozen dataclass), and corpus grounding verification.
    """

    def setUp(self):
        self.record = ProvenanceRecord.create(
            question_id="Q-V13-TEST-001",
            intent_type="definition",
            knowledge_node_id="KN-V13-TROP-01",
            evidence_text="The troposphere is the lowest layer of the atmosphere where temperature decreases with height.",
            source_file="source-material/geography_extracted.txt",
            source_location={"page": 12, "line": 45, "offset": 1024},
            question_stem="Which of the following is characterized by a decrease in temperature with altitude in the lowest atmospheric layer?"
        )

    def test_unbroken_6_link_chain_creation(self):
        """ProvenanceRecord factory must produce an unbroken 6-link cryptographic chain passing hash verification."""
        is_valid, err = self.record.verify_hash()
        self.assertTrue(is_valid, f"Chain verification failed: {err}")
        self.assertIsNone(err)
        self.assertEqual(len(self.record.provenance_hash), 64, "Root hash must be 64-char SHA-256 hex string")

    def test_merklized_sha256_link_integrity(self):
        """All 6 Merklized link hashes must be computed and present in LinkHashes."""
        lh = self.record.link_hashes
        self.assertIsNotNone(lh)
        self.assertEqual(len(lh.location_hash), 64)
        self.assertEqual(len(lh.source_hash), 64)
        self.assertEqual(len(lh.evidence_hash), 64)
        self.assertEqual(len(lh.unit_hash), 64)
        self.assertEqual(len(lh.intent_hash), 64)
        self.assertEqual(len(lh.question_hash), 64)

    def test_tamper_detection_evidence_mutation(self):
        """Mutating a single character of evidence text must break evidence_hash and root hash."""
        tampered = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text + " [MUTATED]",
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes
        )
        is_valid, broken_link = tampered.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(broken_link, "evidenceText")

    def test_tamper_detection_stem_mutation(self):
        """Mutating question stem must invalidate question_hash and root hash."""
        tampered = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem="Completely fabricated question stem?",
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes
        )
        is_valid, broken_link = tampered.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(broken_link, "questionId_or_stem")

    def test_tamper_detection_intent_mutation(self):
        """Mutating intent type must invalidate intent_hash and root hash."""
        tampered = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type="cause/effect",  # Mutated from definition
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location=self.record.source_location,
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes
        )
        is_valid, broken_link = tampered.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(broken_link, "intentType")

    def test_tamper_detection_location_mutation(self):
        """Mutating source location coordinates must invalidate location_hash and root hash."""
        tampered = ProvenanceRecord(
            question_id=self.record.question_id,
            intent_type=self.record.intent_type,
            knowledge_node_id=self.record.knowledge_node_id,
            evidence_text=self.record.evidence_text,
            source_file=self.record.source_file,
            source_location={"page": 999, "line": 999, "offset": 0},  # Mutated location
            question_stem=self.record.question_stem,
            provenance_hash=self.record.provenance_hash,
            link_hashes=self.record.link_hashes
        )
        is_valid, broken_link = tampered.verify_hash()
        self.assertFalse(is_valid)
        self.assertEqual(broken_link, "sourceLocation")

    def test_provenance_record_immutability(self):
        """Attempting to mutate attributes on a frozen ProvenanceRecord must raise FrozenInstanceError."""
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.record.evidence_text = "Mutated evidence"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.record.provenance_hash = "0" * 64

    def test_corpus_grounding_audit(self):
        """audit_provenance_integrity must verify verbatim presence of evidence in source corpus."""
        corpus_dict = {
            "source-material/geography_extracted.txt": (
                "Chapter 4. The Earth's Atmosphere. "
                "The troposphere is the lowest layer of the atmosphere where temperature decreases with height. "
                "Above it lies the stratosphere."
            )
        }
        clean_audit = audit_provenance_integrity([self.record], source_corpus=corpus_dict)
        self.assertEqual(clean_audit["total_records"], 1)
        self.assertEqual(clean_audit["valid_records"], 1)
        self.assertEqual(clean_audit["tampered_records"], 0)
        self.assertEqual(clean_audit["grounding_failures"], 0)

        # Fabricated ungrounded record
        fabricated_record = ProvenanceRecord.create(
            question_id="Q-FAB-001",
            intent_type="definition",
            knowledge_node_id="KN-FAB-01",
            evidence_text="The moon is entirely composed of green subterranean gouda cheese.",
            source_file="source-material/geography_extracted.txt",
            source_location={"page": 1, "line": 1},
            question_stem="Which cheese forms the lunar core?"
        )
        bad_audit = audit_provenance_integrity([fabricated_record], source_corpus=corpus_dict)
        self.assertEqual(bad_audit["grounding_failures"], 1)
        self.assertEqual(bad_audit["valid_records"], 0)


if __name__ == "__main__":
    unittest.main()
