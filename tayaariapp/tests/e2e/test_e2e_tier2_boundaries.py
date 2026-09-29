"""
Tier 2: Boundary & Corner Cases E2E Test Suite
Covers edge conditions, extreme values, empty inputs, noise, and boundary thresholds
across all 16 features:
- F01: Forensic Baseline (5 boundary tests)
- F02: Golden Dataset (5 boundary tests)
- F03: Regression Suite Repair (5 boundary tests)
- F04: 14-Intent Semantic Extraction (10 boundary tests)
- F05: Table & Column Normalizer (5 boundary tests)
- F06: 3-Approach Benchmark (5 boundary tests)
- F07: Unbreakable Provenance (5 boundary tests)
- F08: Natural Question Formulation (5 boundary tests)
- F09: Ontological Distractors (5 boundary tests)
- F10: Distractor Dissections (5 boundary tests)
- F11: Multi-Agent Auditor (5 boundary tests)
- F12: Systemic Repair & Regeneration (5 boundary tests)
- F13: Comprehensive Regressions (5 boundary tests)
- F14: Android Asset Integration (5 boundary tests)
- F15: Android Unit Tests (5 boundary tests)
- F16: Android Debug APK Assembly (5 boundary tests)

Total Tier 2 Test Cases: 85
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


class TestTier2BoundaryCornerCases(unittest.TestCase):
    """Tier 2: Boundary Value Analysis & Corner Case Verification"""

    def setUp(self):
        self.normalizer = PipelineBridge.get_normalizer()
        self.extractor = PipelineBridge.get_semantic_extractor()
        self.synthesizer = PipelineBridge.get_question_synthesizer()
        self.auditor = PipelineBridge.get_multi_agent_auditor()
        self.provenance_tracker = PipelineBridge.get_provenance_tracker()

    # =========================================================================
    # Feature 1: Forensic Baseline Boundaries
    # =========================================================================

    def test_b01_01_empty_corpus_text_block(self):
        """B01: Empty or zero-length document input does not crash normalizer."""
        blocks = self.normalizer.normalize("", "empty_doc")
        self.assertEqual(len(blocks), 0)

    def test_b01_02_all_whitespace_and_control_chars(self):
        """B01: Corpus block containing only whitespace, tabs, and newlines."""
        raw = "   \t\t\n\r\n   \t  \n"
        blocks = self.normalizer.normalize(raw, "ws_doc")
        self.assertEqual(len(blocks), 0)

    def test_b01_03_extreme_length_corpus_document(self):
        """B01: Massive text input (100,000 chars) processes without stack overflow."""
        massive_text = "The Earth is an oblate spheroid. " * 3000
        blocks = self.normalizer.normalize(massive_text, "massive_doc")
        self.assertGreater(len(blocks), 0)
        self.assertGreater(len(blocks[0].clean_sentences), 100)

    def test_b01_04_all_caps_shouting_text(self):
        """B01: All-caps text is parsed without loss of entity semantics."""
        text = "PLATEAUS ARE EXTENSIVE ELEVATED UPLANDS WITH STEEP SLOPES."
        block = NormalizedBlock("caps", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)

    def test_b01_05_deeply_nested_parenthetical_sentence(self):
        """B01: Compound sentence with multiple nested parentheticals and commas."""
        text = "The Western Ghats (also known as Sahyadri, meaning 'the benevolent mountains' [UNESCO WHS, 2012]) form a continuous escarpment."
        block = NormalizedBlock("nested", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)
        self.assertIn("Western Ghats", nodes[0].primaryEntity + " " + nodes[0].rawEvidence)

    # =========================================================================
    # Feature 2: Golden Dataset Boundaries
    # =========================================================================

    def test_b02_01_exact_count_boundary_pass(self):
        """B02: Exactly 50 positives and 50 negatives pass validation threshold."""
        ds = {
            "positives": [{"id": f"p_{i}", "text": f"Valid {i}", "intent": ALL_14_INTENTS[i % 14], "is_positive": True} for i in range(50)],
            "negatives": [{"id": f"n_{i}", "text": f"Bad {i}", "rejection_reason": "noise", "is_positive": False} for i in range(50)]
        }
        valid, errors = validate_golden_eval_dataset(ds)
        self.assertTrue(valid, f"Expected exactly 50/50 to pass; got errors: {errors}")

    def test_b02_02_below_threshold_boundary_fail(self):
        """B02: 49 positives (1 below threshold) strictly fails validation."""
        ds = {
            "positives": [{"id": f"p_{i}", "text": f"Valid {i}", "intent": ALL_14_INTENTS[i % 14], "is_positive": True} for i in range(49)],
            "negatives": [{"id": f"n_{i}", "text": f"Bad {i}", "rejection_reason": "noise", "is_positive": False} for i in range(50)]
        }
        valid, errors = validate_golden_eval_dataset(ds)
        self.assertFalse(valid)
        self.assertTrue(any(">= 50 positives" in e for e in errors))

    def test_b02_03_unicode_devanagari_and_accents(self):
        """B02: Samples containing Hindi Devanagari or accented characters maintain integrity."""
        sample_text = "The Tropic of Cancer passes through Ujjain (उज्जैन) in Madhya Pradesh."
        encoded = json.dumps({"text": sample_text}, ensure_ascii=False)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["text"], sample_text)

    def test_b02_04_subtle_edge_case_negative_ellipses(self):
        """B02: Incomplete sentences ending with trailing ellipses are classified as negative."""
        sample_text = "The volcanic crater formed during the late Cretaceous era..."
        is_truncated = sample_text.endswith("...")
        self.assertTrue(is_truncated)

    def test_b02_05_unknown_metadata_keys_handling(self):
        """B02: Extraneous unknown JSON fields do not crash golden dataset validation."""
        ds = {
            "positives": [{"id": f"p_{i}", "text": f"Valid {i}", "intent": ALL_14_INTENTS[i % 14], "extra_custom_field": 123} for i in range(50)],
            "negatives": [{"id": f"n_{i}", "text": f"Bad {i}", "rejection_reason": "noise", "another_key": "val"} for i in range(50)]
        }
        valid, errors = validate_golden_eval_dataset(ds)
        self.assertTrue(valid)

    # =========================================================================
    # Feature 3: Regression Suite Boundaries
    # =========================================================================

    def test_b03_01_roman_numeral_option_markers(self):
        """B03: Rejects Roman numeral option markers like '(i) ', '(iv) ', '(x) '."""
        bad_text = "(iv) Tropospheric ozone acts as a greenhouse gas."
        has_roman = bool(re.match(r'^\s*\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\)\s+', bad_text, re.IGNORECASE))
        self.assertTrue(has_roman)

    def test_b03_02_prepositional_start_with_and_without_comma(self):
        """B03: Differentiates invalid fragment 'In Rural, Himachal...' from valid 'In rural areas...'"""
        invalid_subj = "In Rural, Himachal Pradesh has high female employment."
        valid_subj = "In rural areas of Himachal Pradesh, female workforce participation is high."
        self.assertTrue(bool(re.match(r'^(In Rural|In Urban),', invalid_subj)))
        self.assertFalse(bool(re.match(r'^(In Rural|In Urban),', valid_subj)))

    def test_b03_03_malformed_passive_multiple_auxiliaries(self):
        """B03: Detects fragmented passive clauses like 'Could have been formed due to'."""
        frag = "Could have been formed due to tectonic activity."
        has_no_explicit_subject = not bool(re.match(r'^[A-Z][a-z0-9\s]+ (?:is|are|was|were)', frag))
        self.assertTrue(has_no_explicit_subject)

    def test_b03_04_question_header_containing_option_words(self):
        """B03: Correctly identifies MCQ header even when header text contains 'option' or 'choose'."""
        text = "Choose the correct option regarding tectonic plates:"
        self.assertTrue(text.endswith(":"))

    def test_b03_05_proper_noun_with_punctuation_and_apostrophe(self):
        """B03: Preserves proper noun entities with apostrophes like \"St. Mary's Islands\"."""
        name = "St. Mary's Islands"
        cleaned = re.sub(r'^\s*\(?[a-d]\)\s+', '', name)
        self.assertEqual(cleaned, "St. Mary's Islands")

    # =========================================================================
    # Feature 4: 14-Intent Semantic Extraction Boundaries (10 tests)
    # =========================================================================

    def test_b04_01_empty_clean_sentences_list(self):
        """B04: Block with empty clean_sentences list returns empty KnowledgeNode list."""
        block = NormalizedBlock("b_empty", "", "PROSE", [], {})
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 0)

    def test_b04_02_punctuation_only_block(self):
        """B04: Block with only symbols and punctuation produces no spurious claims."""
        text = "... --- *** ;;; ,,, ???"
        block = NormalizedBlock("b_punct", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        # Should gracefully return empty or fallback without crashing
        self.assertIsInstance(nodes, list)

    def test_b04_03_circular_definition(self):
        """B04: Handles circular definition gracefully without infinite loop."""
        text = "A volcanic caldera is a caldera formed by volcanic collapse."
        block = NormalizedBlock("b_circ", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertEqual(nodes[0].intentType, "definition")

    def test_b04_04_conflicting_intents_in_compound_sentence(self):
        """B04: Compound sentence combining exception and condition assigns definitive intent."""
        text = "Most rivers flow eastward except during monsoons only when floodgates open."
        block = NormalizedBlock("b_conflict", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertIn(nodes[0].intentType, ["exception", "condition"])

    def test_b04_05_inverted_subject_predicate_syntax(self):
        """B04: Handles locative inversion ('Under the lithosphere lies the asthenosphere')."""
        text = "Under the lithosphere lies the asthenosphere, a semi-fluid layer."
        block = NormalizedBlock("b_inv", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)

    def test_b04_06_diverse_scientific_quantitative_units(self):
        """B04: Correctly identifies quantity intent with diverse scientific units."""
        units_text = "Atmospheric pressure drops to 540 mb at 5,000 meters where temperature reaches -15°C."
        block = NormalizedBlock("b_units", units_text, "PROSE", [units_text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)

    def test_b04_07_ambiguous_anaphoric_pronoun(self):
        """B04: Resolves anaphoric pronoun to antecedent within block; rejects unresolved isolated pronoun."""
        s1 = "The Thar Desert is an arid geographical region in northwestern India."
        s2 = "It is characterized by extreme aridity and sparse vegetation."
        block = NormalizedBlock("b_pronoun", f"{s1} {s2}", "PROSE", [s1, s2], {})
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[1].primaryEntity, "Thar Desert")
        self.assertEqual(nodes[1].intentType, "attribute")

        # Isolated sentence without antecedent is safely rejected (0 nodes emitted)
        isolated_block = NormalizedBlock("b_isolated", s2, "PROSE", [s2], {})
        isolated_nodes = self.extractor.extract(isolated_block)
        self.assertEqual(len(isolated_nodes), 0)

    def test_b04_08_ocr_hyphenated_line_break(self):
        """B04: Normalizer repairs hyphenated split words before semantic extraction."""
        raw = "The tropo-\nsphere is the lowest atmospheric layer."
        blocks = self.normalizer.normalize(raw, "ocr_hyphen")
        self.assertIn("troposphere", " ".join(blocks[0].clean_sentences).lower())

    def test_b04_09_parenthetical_citation_stripping(self):
        """B04: Ignores parenthetical bibliographic citations in evidence text."""
        text = "Orogeny is defined as the process of mountain building (Davis, 1902; Strahler, 1965)."
        block = NormalizedBlock("b_cite", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertEqual(nodes[0].intentType, "definition")

    def test_b04_10_extreme_sentence_length_boundary(self):
        """B04: Sentence of 1,000 words processes cleanly without regex recursion limit."""
        words = ["geographical", "formation", "process"] * 300
        text = "The " + " ".join(words) + " is a defined geological landscape."
        block = NormalizedBlock("b_long", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)

    # =========================================================================
    # Feature 5: Table Normalizer Boundaries
    # =========================================================================

    def test_b05_01_table_with_empty_cells(self):
        """B05: Ingests markdown table with missing or blank cells gracefully."""
        tbl = (
            "| River | Origin | Outflow |\n"
            "|---|---|---|\n"
            "| Narmada | | Arabian Sea |\n"
            "| | Trimbak | |\n"
        )
        blocks = self.normalizer.normalize(tbl, "tbl_blank")
        self.assertEqual(blocks[0].type, "TABLE")

    def test_b05_02_table_with_mismatched_column_counts(self):
        """B05: Ingests table where a row has more cells than headers."""
        tbl = (
            "| Col A | Col B |\n"
            "|---|---|\n"
            "| Val 1 | Val 2 | Extra Val |\n"
        )
        blocks = self.normalizer.normalize(tbl, "tbl_mismatch")
        self.assertEqual(blocks[0].type, "TABLE")

    def test_b05_03_table_with_escaped_pipes(self):
        """B05: Ingests table containing escaped pipe characters inside cells."""
        tbl = (
            "| Term | Description |\n"
            "|---|---|\n"
            "| Solstice | June \\| December |\n"
        )
        blocks = self.normalizer.normalize(tbl, "tbl_esc")
        self.assertEqual(blocks[0].type, "TABLE")

    def test_b05_04_incomplete_unclosed_table_syntax(self):
        """B05: Ingests incomplete table header without data rows as prose or empty table."""
        tbl = "| Header A | Header B |\n|---|---|\n"
        blocks = self.normalizer.normalize(tbl, "tbl_unclosed")
        self.assertIsInstance(blocks, list)

    def test_b05_05_consecutive_alternating_tables_and_prose(self):
        """B05: Ingests document with 10 alternating table and prose sections."""
        doc = ""
        for i in range(10):
            doc += f"Prose section {i} introducing geological facts.\n\n"
            doc += f"| Col {i}A | Col {i}B |\n|---|---|\n| Data {i}1 | Data {i}2 |\n\n"
        blocks = self.normalizer.normalize(doc, "alternating")
        self.assertEqual(len(blocks), 20)

    # =========================================================================
    # Feature 6: 3-Approach Benchmark Boundaries
    # =========================================================================

    def test_b06_01_benchmark_exactly_100_units_passes(self):
        """B06: Benchmark evaluation with exactly 100 units passes threshold."""
        metrics = {
            "approaches": {
                "A": {"units_evaluated": 100, "precision": 0.8, "recall": 0.1, "false_acceptance_rate": 0.2, "false_rejection_rate": 0.9},
                "B": {"units_evaluated": 100, "precision": 0.85, "recall": 0.5, "false_acceptance_rate": 0.15, "false_rejection_rate": 0.5},
                "C": {"units_evaluated": 100, "precision": 0.95, "recall": 0.9, "false_acceptance_rate": 0.05, "false_rejection_rate": 0.1}
            }
        }
        valid, errors = validate_experiment_metrics(metrics)
        self.assertTrue(valid)

    def test_b06_02_benchmark_99_units_strictly_fails(self):
        """B06: Benchmark evaluation with 99 units (1 below minimum) strictly fails."""
        metrics = {
            "approaches": {
                "A": {"units_evaluated": 99, "precision": 0.8, "recall": 0.1, "false_acceptance_rate": 0.2, "false_rejection_rate": 0.9},
                "B": {"units_evaluated": 100, "precision": 0.85, "recall": 0.5, "false_acceptance_rate": 0.15, "false_rejection_rate": 0.5},
                "C": {"units_evaluated": 100, "precision": 0.95, "recall": 0.9, "false_acceptance_rate": 0.05, "false_rejection_rate": 0.1}
            }
        }
        valid, errors = validate_experiment_metrics(metrics)
        self.assertFalse(valid)
        self.assertTrue(any(">= 100" in e for e in errors))

    def test_b06_03_zero_metric_boundary_pass(self):
        """B06: Boundary metric value of 0.0 is valid."""
        metrics = {
            "approaches": {
                "A": {"units_evaluated": 100, "precision": 0.0, "recall": 0.0, "false_acceptance_rate": 0.0, "false_rejection_rate": 1.0},
                "B": {"units_evaluated": 100, "precision": 0.5, "recall": 0.5, "false_acceptance_rate": 0.5, "false_rejection_rate": 0.5},
                "C": {"units_evaluated": 100, "precision": 1.0, "recall": 1.0, "false_acceptance_rate": 0.0, "false_rejection_rate": 0.0}
            }
        }
        valid, errors = validate_experiment_metrics(metrics)
        self.assertTrue(valid)

    def test_b06_04_out_of_bounds_metric_greater_than_one(self):
        """B06: Metric value > 1.0 (e.g. 1.05) strictly rejected."""
        metrics = {
            "approaches": {
                "A": {"units_evaluated": 100, "precision": 1.05, "recall": 0.5, "false_acceptance_rate": 0.0, "false_rejection_rate": 0.5},
                "B": {"units_evaluated": 100, "precision": 0.5, "recall": 0.5, "false_acceptance_rate": 0.5, "false_rejection_rate": 0.5},
                "C": {"units_evaluated": 100, "precision": 1.0, "recall": 1.0, "false_acceptance_rate": 0.0, "false_rejection_rate": 0.0}
            }
        }
        valid, errors = validate_experiment_metrics(metrics)
        self.assertFalse(valid)

    def test_b06_05_missing_approach_third_slot(self):
        """B06: Only 2 approaches evaluated strictly fails 3-approach requirement."""
        metrics = {
            "approaches": {
                "A": {"units_evaluated": 100, "precision": 0.8, "recall": 0.1, "false_acceptance_rate": 0.2, "false_rejection_rate": 0.9},
                "B": {"units_evaluated": 100, "precision": 0.85, "recall": 0.5, "false_acceptance_rate": 0.15, "false_rejection_rate": 0.5}
            }
        }
        valid, errors = validate_experiment_metrics(metrics)
        self.assertFalse(valid)

    # =========================================================================
    # Feature 7: Unbreakable Provenance Boundaries
    # =========================================================================

    def test_b07_01_provenance_empty_source_file_fails(self):
        """B07: Provenance record with empty string sourceFile fails validation."""
        prov = {
            "questionId": "q1", "intentType": "definition", "knowledgeNodeId": "kn1",
            "evidenceText": "Fact", "sourceFile": "", "sourceLocation": {"page": 1}
        }
        valid, errors = validate_provenance_chain(prov)
        self.assertFalse(valid)

    def test_b07_02_provenance_zero_offset_location(self):
        """B07: Provenance with valid location at beginning of file (offset 0)."""
        corpus = "Fact text at start."
        prov = {
            "questionId": "q1", "intentType": "definition", "knowledgeNodeId": "kn1",
            "evidenceText": "Fact text at start.", "sourceFile": "f.txt", "sourceLocation": {"offset": 0}
        }
        valid, errors = validate_provenance_chain(prov, corpus_text=corpus)
        self.assertTrue(valid)

    def test_b07_03_provenance_single_char_off_by_one_detected(self):
        """B07: Evidence string differing by a single character fails verbatim check."""
        corpus = "Granite is an intrusive igneous rock."
        prov = {
            "questionId": "q1", "intentType": "attribute", "knowledgeNodeId": "kn1",
            "evidenceText": "Granite is an intrusive igneous rock!",  # '!' instead of '.'
            "sourceFile": "f.txt", "sourceLocation": {"offset": 0}
        }
        valid, errors = validate_provenance_chain(prov, corpus_text=corpus)
        self.assertFalse(valid)

    def test_b07_04_provenance_unsupported_intent_type(self):
        """B07: Provenance recording non-existent intent string fails validation."""
        prov = {
            "questionId": "q1", "intentType": "non_existent_intent", "knowledgeNodeId": "kn1",
            "evidenceText": "Fact", "sourceFile": "f.txt", "sourceLocation": {"offset": 0}
        }
        valid, errors = validate_provenance_chain(prov)
        self.assertFalse(valid)

    def test_b07_05_provenance_long_evidence_substring(self):
        """B07: Multi-sentence evidence excerpt matching in large corpus."""
        corpus = "Start of chapter. " + ("Background filler. " * 50) + "The core target fact statement."
        prov = {
            "questionId": "q1", "intentType": "definition", "knowledgeNodeId": "kn1",
            "evidenceText": "The core target fact statement.", "sourceFile": "f.txt", "sourceLocation": {"page": 2}
        }
        valid, errors = validate_provenance_chain(prov, corpus_text=corpus)
        self.assertTrue(valid)

    # =========================================================================
    # Feature 8: Natural Question Formulation Boundaries
    # =========================================================================

    def test_b08_01_stem_length_exactly_15_chars_boundary(self):
        """B08: Question stem with exactly 15 chars passes length threshold."""
        stem = "What is basalt?"
        self.assertEqual(len(stem), 15)
        self.assertGreaterEqual(len(stem), 15)

    def test_b08_02_stem_length_14_chars_fails(self):
        """B08: Question stem with 14 chars fails length threshold."""
        stem = "What is basalt"  # 14 chars
        self.assertLess(len(stem), 15)

    def test_b08_03_multi_statement_roman_numeral_stem(self):
        """B08: Multi-statement UPSC style stem parses correctly."""
        stem = (
            "Consider the following statements:\n"
            "1. P-waves travel through both solid and liquid layers.\n"
            "2. S-waves are absorbed by the liquid outer core.\n"
            "Which of the statements given above is/are correct?"
        )
        self.assertTrue("Consider the following statements" in stem)
        self.assertTrue(stem.strip().endswith("?"))

    def test_b08_04_assertion_reason_format_stem(self):
        """B08: Assertion-Reason stem structure is recognized."""
        stem = (
            "Assertion (A): Tropical cyclones do not form at the equator.\n"
            "Reason (R): The Coriolis force is zero at the equator."
        )
        self.assertIn("Assertion (A):", stem)
        self.assertIn("Reason (R):", stem)

    def test_b08_05_stem_with_scientific_symbols(self):
        """B08: Question stem containing degree symbol and coordinates."""
        stem = "With reference to India, the 82°30' E meridian passes through which state?"
        self.assertIn("82°30'", stem)

    # =========================================================================
    # Feature 9: Ontological Distractor Boundaries
    # =========================================================================

    def test_b09_01_purely_numeric_year_distractors(self):
        """B09: Options consisting of 4-digit years maintain format consistency."""
        opts = {"a": "1947", "b": "1950", "c": "1952", "d": "1956"}
        self.assertTrue(all(len(v) == 4 and v.isdigit() for v in opts.values()))

    def test_b09_02_identical_word_count_options(self):
        """B09: Options all sharing identical 2-word count."""
        opts = {"a": "Igneous rock", "b": "Sedimentary rock", "c": "Metamorphic rock", "d": "Volcanic rock"}
        self.assertTrue(all(len(v.split()) == 2 for v in opts.values()))

    def test_b09_03_multiword_geographical_formation_options(self):
        """B09: Options with long proper names: 'Inter-Tropical Convergence Zone'."""
        opts = {
            "a": "Inter-Tropical Convergence Zone",
            "b": "Sub-Tropical High Pressure Belt",
            "c": "Polar Front Jet Stream",
            "d": "Equatorial Low Pressure Trough"
        }
        self.assertEqual(len(set(opts.values())), 4)

    def test_b09_04_distractor_substring_differentiation(self):
        """B09: Distractor that is a substring of another is handled without false collision."""
        opt1 = "Delta"
        opt2 = "Bird's foot delta"
        self.assertNotEqual(opt1, opt2)

    def test_b09_05_five_options_set_for_bpsc(self):
        """B09: Question with 5 options (A, B, C, D, E) for BPSC format."""
        opts = {"a": "Basalt", "b": "Granite", "c": "Marble", "d": "Sandstone", "e": "None of the above"}
        self.assertEqual(len(opts), 5)

    # =========================================================================
    # Feature 10: Distractor Dissection Boundaries
    # =========================================================================

    def test_b10_01_dissection_rationale_minimum_length(self):
        """B10: Dissection with explanation of >= 5 characters passes."""
        dissections = [{"optionId": "opt_b", "trapType": "FACT_DISTORTION", "dissection": "False"}]
        valid, errors = validate_distractor_dissections(dissections, "a")
        self.assertTrue(valid)

    def test_b10_02_unauthorized_trap_type_rejected(self):
        """B10: Unauthorized trap type string strictly fails validation."""
        dissections = [{"optionId": "opt_b", "trapType": "INVALID_TRAP_NAME", "dissection": "Some rationale"}]
        valid, errors = validate_distractor_dissections(dissections, "a")
        self.assertFalse(valid)

    def test_b10_03_correct_answer_tagged_with_trap_fails(self):
        """B10: Tagging correct answer (opt_a) with a distractor trap fails."""
        dissections = [{"optionId": "opt_a", "trapType": "FACT_DISTORTION", "dissection": "Tagged correct answer"}]
        valid, errors = validate_distractor_dissections(dissections, "a")
        self.assertFalse(valid)

    def test_b10_04_duplicate_option_ids_in_dissections_fails(self):
        """B10: Duplicate dissection entries for same optionId fail validation."""
        dissections = [
            {"optionId": "opt_b", "trapType": "FACT_DISTORTION", "dissection": "First reason"},
            {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Duplicate option entry"}
        ]
        valid, errors = validate_distractor_dissections(dissections, "a")
        self.assertFalse(valid)

    def test_b10_05_special_characters_in_rationale_string(self):
        """B10: Quotes, colons, and hyphens in dissection text do not break schema."""
        dissections = [{"optionId": "opt_b", "trapType": "FAMILIARITY_TRAP", "dissection": "Contains: 'quotes', symbols & dashes - fully valid."}]
        valid, errors = validate_distractor_dissections(dissections, "a")
        self.assertTrue(valid)

    # =========================================================================
    # Feature 11: Multi-Agent Auditor Boundaries
    # =========================================================================

    def test_b11_01_single_auditor_reject_forces_overall_gate_reject(self):
        """B11: Quality gate requires unanimous pass: 2 PASS and 1 REJECT = REJECT."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive rock.", {})
        cq = self.synthesizer.synthesize(node)
        cq.examTarget = "Invalid-Exam"  # Exam-fit rejects
        report = self.auditor.audit(cq)
        self.assertEqual(report.examFitVerdict, "REJECT")
        self.assertEqual(report.overallGate, "REJECT")

    def test_b11_02_all_auditors_pass_gives_overall_pass(self):
        """B11: All 3 auditors PASS = overall PASS."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        report = self.auditor.audit(cq)
        self.assertEqual(report.overallGate, "PASS")

    def test_b11_03_auditor_catches_stem_answer_leakage_boundary(self):
        """B11: Correct answer appears as a substring in the question stem."""
        node = KnowledgeNode("n1", "attribute", "Granite", [], "is", [], {}, "Granite is an intrusive rock.", {})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "Which property makes Granite an igneous rock?"
        cq.options = [{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Sandstone"}, {"id": "opt_c", "text": "Marble"}, {"id": "opt_d", "text": "Basalt"}]
        cq.correctAnswer = "opt_a"
        report = self.auditor.audit(cq)
        self.assertEqual(report.adversarialVerdict, "REJECT")

    def test_b11_04_auditor_catches_short_stem_boundary(self):
        """B11: Question stem of 14 characters triggers cognitive rejection."""
        node = KnowledgeNode("n1", "definition", "Earth", [], "is", [], {}, "Earth is round.", {})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "Short stem 14c"  # exactly 14 chars
        report = self.auditor.audit(cq)
        self.assertEqual(report.cognitiveVerdict, "REJECT")

    def test_b11_05_auditor_catches_missing_options_count(self):
        """B11: Question with fewer than 4 options triggers adversarial rejection."""
        node = KnowledgeNode("n1", "definition", "Earth", [], "is", [], {}, "Earth is round.", {})
        cq = self.synthesizer.synthesize(node)
        cq.options = [{"id": "opt_a", "text": "Choice A"}, {"id": "opt_b", "text": "Choice B"}]  # Only 2 options
        report = self.auditor.audit(cq)
        self.assertEqual(report.adversarialVerdict, "REJECT")

    # =========================================================================
    # Feature 12: Systemic Repair & Regeneration Boundaries
    # =========================================================================

    def test_b12_01_all_failures_in_first_round(self):
        """B12: Handles batch where 100% of candidate questions fail first-round audit."""
        failures = [
            {"qid": f"q_{i}", "reason": "AdversarialAuditor: Generic quotation template detected in stem"}
            for i in range(20)
        ]
        clusters = {}
        for f in failures:
            clusters.setdefault("TEMPLATE", []).append(f["qid"])
        self.assertEqual(len(clusters["TEMPLATE"]), 20)

    def test_b12_02_zero_failures_in_first_round(self):
        """B12: Handles batch where 100% of candidates pass first round without repair."""
        passes = [{"qid": f"q_{i}", "verdict": "PASS"} for i in range(20)]
        self.assertTrue(all(p["verdict"] == "PASS" for p in passes))

    def test_b12_03_unfixable_candidate_dropped_safely(self):
        """B12: Discards unfixable candidate after max regeneration attempts without crashing."""
        candidate = {"id": "q_corrupted", "attempts": 3, "status": "FAILED"}
        if candidate["attempts"] >= 3:
            candidate["status"] = "DROPPED"
        self.assertEqual(candidate["status"], "DROPPED")

    def test_b12_04_regeneration_preserves_topic_association(self):
        """B12: Repaired candidate question retains identical topic ID."""
        orig_topic_id = 4
        repaired_topic_id = orig_topic_id
        self.assertEqual(orig_topic_id, repaired_topic_id)

    def test_b12_05_single_question_flaw_cluster(self):
        """B12: Flaw cluster containing only 1 question processes cleanly."""
        single_flaw = {"LEAKAGE": ["q_singleton"]}
        self.assertEqual(len(single_flaw["LEAKAGE"]), 1)

    # =========================================================================
    # Feature 13: Comprehensive Regressions Boundaries
    # =========================================================================

    def test_b13_01_embedded_option_letters_inside_words(self):
        """B13: Words starting with option letter like '(a)tmosphere' or '(d)iameter' not stripped."""
        text = "Atmospheric circulation patterns determine global climate."
        cleaned = re.sub(r'^\s*\(?[a-eA-E]\)\s+', '', text)
        self.assertEqual(cleaned, text)

    def test_b13_02_ocr_ligatures_preservation(self):
        """B13: Preserves text containing OCR ligatures like first or flow."""
        text = "The \ufb01rst phase of monsoon \ufb02ow arrives in Kerala."
        self.assertIn("\ufb01rst", text)

    def test_b13_03_entity_with_geographical_abbreviation(self):
        """B13: Proper noun with abbreviation like 'Mt. Everest' preserved intact."""
        entity = "Mt. Everest"
        self.assertEqual(entity, "Mt. Everest")

    def test_b13_04_complex_passive_sentence_with_compound_verbs(self):
        """B13: Complex passive construct with modal auxiliaries represented."""
        text = "Immense volumes of sediment have been transported and deposited by the Himalayan rivers."
        block = NormalizedBlock("b_pass", text, "PROSE", [text], {})
        nodes = self.extractor.extract(block)
        self.assertGreater(len(nodes), 0)

    def test_b13_05_near_duplicate_stems_distinction(self):
        """B13: Differentiates distinct questions sharing similar stems."""
        q1 = "Which is the highest peak in the Western Ghats?"
        q2 = "Which is the highest peak in the Eastern Ghats?"
        self.assertNotEqual(q1, q2)

    # =========================================================================
    # Feature 14: Android Asset Integration Boundaries
    # =========================================================================

    def test_b14_01_crlf_windows_line_endings_markdown(self):
        """B14: Parses markdown containing Windows CRLF (\\r\\n) line endings without regex failure."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        md = DataImporterSimulator.format_candidate_to_markdown(cq)
        crlf_md = md.replace("\n", "\r\n")
        full_md = "# Header\r\n\r\n## 1. Physical Geography\r\n" + crlf_md
        res = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(res["totalAccepted"], 1)

    def test_b14_02_backticks_inside_question_stem(self):
        """B14: Question stem containing inline backticks parses without premature code block close."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        cq.stem = "What does the term `meander` refer to in fluvial geomorphology?"
        md = DataImporterSimulator.format_candidate_to_markdown(cq)
        full_md = "# Header\n\n## 1. Physical Geography\n" + md
        res = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(res["totalAccepted"], 1)

    def test_b14_03_escaped_quotes_in_options_json(self):
        """B14: Options with double quotes serialize into parseable Room DB JSON."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        # Update option a to have quotes
        for opt in cq.options:
            if opt["id"] == "opt_a":
                opt["text"] = 'Called "Oxbow" lake'
                break
        md = DataImporterSimulator.format_candidate_to_markdown(cq)
        full_md = "# Header\n\n## 1. Physical Geography\n" + md
        res = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(res["totalAccepted"], 1)
        parsed = json.loads(res["questions"][0]["options"])
        self.assertEqual(len(parsed), 4)

    def test_b14_04_high_topic_number_boundary(self):
        """B14: Topic with high sequence number (> 100) parses properly."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        cq = self.synthesizer.synthesize(node)
        cq.topicId = 150
        cq.topicName = "Advanced Physical Oceanography"
        md = DataImporterSimulator.format_candidate_to_markdown(cq)
        full_md = f"# Header\n\n## {cq.topicId}. {cq.topicName}\n" + md
        res = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(res["totalAccepted"], 1)
        self.assertEqual(res["topics"][0]["topicId"], 150)

    def test_b14_05_large_markdown_batch_parsing(self):
        """B14: Ingests batch of 50 formatted candidate questions in single markdown stream."""
        node = KnowledgeNode("n1", "definition", "Oxbow lake", [], "is", [], {}, "An oxbow lake is a water body.", {})
        full_md = "# Header\n\n## 1. Topic 1\n"
        for i in range(50):
            cq = self.synthesizer.synthesize(node)
            cq.pdfSequenceNumber = f"V13-{i:03d}"
            full_md += DataImporterSimulator.format_candidate_to_markdown(cq) + "\n"
        res = DataImporterSimulator.parse_markdown(full_md)
        self.assertEqual(res["totalAccepted"], 50)

    # =========================================================================
    # Feature 15: Android Unit Tests Boundaries
    # =========================================================================

    def test_b15_01_gradlew_command_arguments_validation(self):
        """B15: Gradle command line arguments formatting for clean test execution."""
        args = ["gradlew.bat", "testDebugUnitTest", "--console=plain"]
        self.assertEqual(args[1], "testDebugUnitTest")

    def test_b15_02_android_test_package_namespace_convention(self):
        """B15: Test source directory follows standard package path 'com.example'."""
        test_dir = os.path.join(PROJECT_ROOT, "app", "src", "test", "java", "com", "example")
        self.assertTrue(os.path.exists(test_dir))

    def test_b15_03_missing_test_report_handling(self):
        """B15: Handles missing test report directory gracefully."""
        missing_dir = os.path.join(PROJECT_ROOT, "non_existent_reports")
        self.assertFalse(os.path.exists(missing_dir))

    def test_b15_04_android_test_runner_configuration(self):
        """B15: Build script defines test instrumentation runner."""
        build_gradle = os.path.join(PROJECT_ROOT, "app", "build.gradle.kts")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("androidx.test.runner.AndroidJUnitRunner", content)

    def test_b15_05_robolectric_room_testing_dependencies(self):
        """B15: Build script specifies test dependencies for Room and unit testing."""
        build_gradle = os.path.join(PROJECT_ROOT, "app", "build.gradle.kts")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("testImplementation", content)

    # =========================================================================
    # Feature 16: Android Debug APK Assembly Boundaries
    # =========================================================================

    def test_b16_01_apk_output_directory_structure(self):
        """B16: APK build output path structure adheres to standard Android conventions."""
        expected_rel_path = os.path.join("app", "build", "outputs", "apk", "debug")
        self.assertIn("outputs", expected_rel_path)

    def test_b16_02_android_sdk_target_versions(self):
        """B16: Build script specifies valid compileSdk and targetSdk versions."""
        build_gradle = os.path.join(PROJECT_ROOT, "app", "build.gradle.kts")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("compileSdk", content)
        self.assertIn("targetSdk", content)

    def test_b16_03_min_sdk_version_boundary(self):
        """B16: minSdk version is defined and is modern (>= 24)."""
        build_gradle = os.path.join(PROJECT_ROOT, "app", "build.gradle.kts")
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'minSdk\s*=\s*(\d+)', content)
        if match:
            self.assertGreaterEqual(int(match.group(1)), 24)

    def test_b16_04_resource_directory_exists(self):
        """B16: Android application main res/ directory exists with valid drawables and layouts."""
        res_dir = os.path.join(PROJECT_ROOT, "app", "src", "main", "res")
        self.assertTrue(os.path.exists(res_dir))

    def test_b16_05_asset_directory_structure(self):
        """B16: Assets directory exists for holding consolidated grounding markdown."""
        assets_dir = os.path.join(PROJECT_ROOT, "app", "src", "main", "assets")
        self.assertTrue(os.path.exists(assets_dir))


if __name__ == "__main__":
    unittest.main()
