#!/usr/bin/env python3
"""
test_eval_adversarial_stress.py
===============================
Empirical Adversarial Stress Harness for Golden Evaluation Dataset & Validation Framework.

Author: teamwork_preview_challenger_m1_1 (EMPIRICAL CHALLENGER)
Target Deliverables Under Test:
- scripts/validate_eval_set.py (Validation Engine & CLI)
- tests/test_golden_eval_set.py (Regression Test Suite)
- data/golden_eval_set.json (Canonical 111-item evaluation set)

Systematically tests failure injection and mutation coverage:
1. Malformed and corrupted JSON structures (syntax errors, non-object roots, invalid items array).
2. Missing mandatory keys (expected_label, intent, provenance, extracted_entities, truth claim, rejection reason).
3. Under-count boundaries (total < 100, positive < 50, negative < 50).
4. Dropped semantic intents (individually verifies rejection for each of the 14 intents).
5. Dropped mandatory negative noise categories (mcq_noise, watermark_noise, incomplete_clause_fragment, ocr_artifact).
6. ID collisions and duplicate / empty text fields.
7. Faulty, placeholder, or trivial provenance coordinates.
8. Real dataset baseline conformity and strict mode audit.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from io import StringIO

# Add repository root to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.validate_eval_set import (
    validate_golden_eval_data,
    CANONICAL_14_INTENTS,
    MANDATORY_NEGATIVE_CATEGORIES,
    ValidationReport,
    normalize_noise_type,
)
from tests.test_golden_eval_set import TestGoldenEvaluationSet


class TestAdversarialStressHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real_dataset_path = os.path.join(REPO_ROOT, "data", "golden_eval_set.json")
        if not os.path.exists(cls.real_dataset_path):
            raise FileNotFoundError(f"Missing golden eval set at {cls.real_dataset_path}")

        with open(cls.real_dataset_path, "r", encoding="utf-8") as f:
            cls.real_data = json.load(f)

        # Baseline items copy
        cls.base_items = cls.real_data.get("items") or cls.real_data.get("examples", [])
        assert len(cls.base_items) >= 100, "Real dataset must have at least 100 items for baseline"

    def _create_temp_dataset_file(self, data_dict_or_list):
        """Helper to create a temporary JSON file and return its path."""
        tf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data_dict_or_list, tf)
        tf.close()
        return tf.name

    def _run_unittest_against_file(self, file_path):
        """Runs test_golden_eval_set.py against a specific JSON file via GOLDEN_EVAL_SET_PATH."""
        env = os.environ.copy()
        env["GOLDEN_EVAL_SET_PATH"] = file_path
        cmd = [sys.executable, "-m", "unittest", "tests.test_golden_eval_set"]
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True
        )
        return proc.returncode, proc.stdout + proc.stderr

    # =========================================================================
    # 1. STRUCTURAL & SCHEMA CORRUPTION
    # =========================================================================

    def test_01_rejects_malformed_json_syntax(self):
        """Verifies CLI validate_eval_set.py fails cleanly on unparseable JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tf:
            tf.write("{ invalid json structure: [unclosed brackets")
            broken_path = tf.name

        try:
            cmd = [sys.executable, "scripts/validate_eval_set.py", broken_path]
            proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 3, f"Expected exit code 3 for JSON parse failure, got {proc.returncode}")
            self.assertIn("Failed to parse JSON file", proc.stderr)
        finally:
            if os.path.exists(broken_path):
                os.remove(broken_path)

    def test_02_rejects_non_object_root(self):
        """Verifies validator rejects non-dict / non-list root elements."""
        for invalid_root in ["string root", 12345, True, None]:
            report = validate_golden_eval_data(invalid_root)
            self.assertFalse(report.passed)
            self.assertTrue(any("Root JSON element must be an object or array" in e for e in report.errors))

    def test_03_rejects_non_list_items_field(self):
        """Verifies validator rejects dataset where 'items' / 'examples' is not a list."""
        mutant = {"version": "1.0", "items": "invalid_not_a_list"}
        report = validate_golden_eval_data(mutant)
        self.assertFalse(report.passed)
        self.assertTrue(any("Missing or invalid 'items' / 'examples' array" in e for e in report.errors))

    def test_04_rejects_non_dict_item_elements(self):
        """Verifies validator rejects non-dict elements inside the items array."""
        mutant_items = copy.deepcopy(self.base_items[:10])
        mutant_items.append("A raw string instead of item object")
        mutant = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant)
        self.assertFalse(report.passed)
        self.assertTrue(any("is not a JSON object" in e for e in report.errors))

    # =========================================================================
    # 2. MISSING MANDATORY KEYS & ATTRIBUTES
    # =========================================================================

    def test_05_rejects_missing_expected_label(self):
        """Verifies validator rejects items missing 'expected_label' / 'label'."""
        mutant_items = copy.deepcopy(self.base_items)
        # Strip label from first item
        del mutant_items[0]["expected_label"]
        if "label" in mutant_items[0]:
            del mutant_items[0]["label"]

        report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
        self.assertFalse(report.passed)
        self.assertTrue(any("Invalid or missing label" in e for e in report.errors))

    def test_06_rejects_invalid_label_value(self):
        """Verifies validator rejects unexpected label values (e.g. 'neutral', 'unknown')."""
        mutant_items = copy.deepcopy(self.base_items)
        mutant_items[0]["expected_label"] = "maybe_positive"

        report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
        self.assertFalse(report.passed)
        self.assertTrue(any("Invalid or missing label: 'maybe_positive'" in e for e in report.errors))

    def test_07_rejects_missing_intent_in_positive_item(self):
        """Verifies validator rejects positive item missing 'expected_intent'."""
        mutant_items = copy.deepcopy(self.base_items)
        pos_idx = next(i for i, it in enumerate(mutant_items) if it.get("expected_label") == "positive")
        mutant_items[pos_idx].pop("intent", None)
        mutant_items[pos_idx].pop("expected_intent", None)

        report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
        self.assertFalse(report.passed)
        self.assertTrue(any("Missing 'expected_intent'" in e for e in report.errors))

    def test_08_rejects_unknown_intent_in_positive_item(self):
        """Verifies validator rejects invalid/unknown semantic intent strings."""
        mutant_items = copy.deepcopy(self.base_items)
        pos_idx = next(i for i, it in enumerate(mutant_items) if it.get("expected_label") == "positive")
        mutant_items[pos_idx]["intent"] = "hypothetical_quantum_entanglement"

        report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
        self.assertFalse(report.passed)
        self.assertTrue(any("Unknown intent 'hypothetical_quantum_entanglement'" in e for e in report.errors))

    def test_09_rejects_missing_source_provenance_object(self):
        """Verifies validator and test suite reject items missing provenance."""
        mutant_items = copy.deepcopy(self.base_items)
        mutant_items[0].pop("provenance", None)
        mutant_items[0].pop("source", None)

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Missing 'source' / 'provenance' object" in e for e in report.errors))

        # Test against test_golden_eval_set.py
        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_08_non_trivial_provenance", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_10_rejects_missing_positive_entities_and_claims(self):
        """Verifies positive items require extracted_entities and expected_truth_claim."""
        # A: Missing entities
        mutant_a = copy.deepcopy(self.base_items)
        pos_idx = next(i for i, it in enumerate(mutant_a) if it.get("expected_label") == "positive")
        mutant_a[pos_idx].pop("semantic_entities", None)
        mutant_a[pos_idx].pop("extracted_entities", None)

        report_a = validate_golden_eval_data({"version": "1.0", "items": mutant_a})
        self.assertFalse(report_a.passed)
        self.assertTrue(any("Missing or empty 'extracted_entities'" in e for e in report_a.errors))

        # B: Missing truth claim / rationale
        mutant_b = copy.deepcopy(self.base_items)
        mutant_b[pos_idx].pop("rationale", None)
        mutant_b[pos_idx].pop("expected_truth_claim", None)

        report_b = validate_golden_eval_data({"version": "1.0", "items": mutant_b})
        self.assertFalse(report_b.passed)
        self.assertTrue(any("Missing or empty 'expected_truth_claim'" in e for e in report_b.errors))

    def test_11_rejects_missing_negative_rejection_reason(self):
        """Verifies negative items require expected_rejection_reason."""
        mutant_items = copy.deepcopy(self.base_items)
        neg_idx = next(i for i, it in enumerate(mutant_items) if it.get("expected_label") == "negative")
        mutant_items[neg_idx].pop("rejection_reason", None)
        mutant_items[neg_idx].pop("expected_rejection_reason", None)

        report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
        self.assertFalse(report.passed)
        self.assertTrue(any("Missing or empty 'expected_rejection_reason'" in e for e in report.errors))

    # =========================================================================
    # 3. UNDERCOUNT BOUNDARIES
    # =========================================================================

    def test_12_rejects_total_items_under_100(self):
        """Verifies validator & test suite fail when total items < 100."""
        # Trim dataset to 99 items (keeping ratio balanced)
        pos = [it for it in self.base_items if it.get("expected_label") == "positive"][:50]
        neg = [it for it in self.base_items if it.get("expected_label") == "negative"][:49]
        mutant_items = pos + neg
        self.assertEqual(len(mutant_items), 99)

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Total items = 99 (must be >= 100)" in e for e in report.errors))

        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_02_total_item_count", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_13_rejects_positives_under_50(self):
        """Verifies validator & test suite fail when positives < 50 even if total >= 100."""
        pos = [it for it in self.base_items if it.get("expected_label") == "positive"][:49]
        neg = [it for it in self.base_items if it.get("expected_label") == "negative"][:55]
        mutant_items = pos + neg
        self.assertEqual(len(mutant_items), 104)

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Positive examples = 49 (must be >= 50)" in e for e in report.errors))

        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_03_positive_and_negative_counts", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_14_rejects_negatives_under_50(self):
        """Verifies validator & test suite fail when negatives < 50 even if total >= 100."""
        pos = [it for it in self.base_items if it.get("expected_label") == "positive"][:56]
        neg = [it for it in self.base_items if it.get("expected_label") == "negative"][:49]
        mutant_items = pos + neg
        self.assertEqual(len(mutant_items), 105)

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Negative examples = 49 (must be >= 50)" in e for e in report.errors))

        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_03_positive_and_negative_counts", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # =========================================================================
    # 4. DROPPED SEMANTIC INTENTS (ALL 14 EXHAUSTIVELY TESTED)
    # =========================================================================

    def test_15_rejects_each_of_14_missing_semantic_intents(self):
        """
        Adversarially removes each one of the 14 required semantic intents individually
        and asserts that BOTH validate_eval_set.py and test_golden_eval_set.py fail
        and specifically identify the dropped intent.
        """
        intents_to_test = sorted(list(CANONICAL_14_INTENTS))
        self.assertEqual(len(intents_to_test), 14, "Must verify all 14 canonical intents")

        for intent_to_drop in intents_to_test:
            with self.subTest(intent_dropped=intent_to_drop):
                # Filter out all positive items matching this intent
                mutant_items = []
                for it in self.base_items:
                    raw_intent = (it.get("intent") or it.get("expected_intent") or "").lower().replace("-", "_").replace("/", "_").replace(" ", "_")
                    if it.get("expected_label") == "positive" and raw_intent == intent_to_drop:
                        continue  # drop it
                    mutant_items.append(it)

                mutant_dict = {"version": "1.0", "items": mutant_items}
                report = validate_golden_eval_data(mutant_dict)
                self.assertFalse(report.passed, f"Validator failed to reject dataset missing intent: {intent_to_drop}")
                self.assertTrue(
                    any(intent_to_drop in e for e in report.errors),
                    f"Error message did not cite dropped intent '{intent_to_drop}': {report.errors}"
                )

                # Test against test_golden_eval_set.py via temp file
                temp_file = self._create_temp_dataset_file(mutant_dict)
                try:
                    retcode, output = self._run_unittest_against_file(temp_file)
                    self.assertNotEqual(retcode, 0, f"test_golden_eval_set should have failed on missing intent: {intent_to_drop}")
                    self.assertIn("test_04_all_14_intents_represented", output)
                    self.assertIn(intent_to_drop, output)
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

    # =========================================================================
    # 5. DROPPED MANDATORY NOISE CATEGORIES
    # =========================================================================

    def test_16_rejects_each_missing_mandatory_noise_category(self):
        """
        Adversarially drops each of the 4 mandatory negative noise categories
        and confirms rejection.
        """
        categories_to_test = sorted(list(MANDATORY_NEGATIVE_CATEGORIES))
        self.assertEqual(len(categories_to_test), 4)

        for cat_to_drop in categories_to_test:
            with self.subTest(category_dropped=cat_to_drop):
                mutant_items = []
                for it in self.base_items:
                    raw_cat = it.get("rejection_category") or it.get("noise_type") or ""
                    canon_cat = normalize_noise_type(str(raw_cat))
                    if it.get("expected_label") == "negative" and canon_cat == cat_to_drop:
                        continue
                    mutant_items.append(it)

                mutant_dict = {"version": "1.0", "items": mutant_items}
                report = validate_golden_eval_data(mutant_dict)
                self.assertFalse(report.passed, f"Validator failed to reject dataset missing noise category: {cat_to_drop}")
                self.assertTrue(
                    any(cat_to_drop in e for e in report.errors),
                    f"Error message did not cite dropped noise '{cat_to_drop}': {report.errors}"
                )

                temp_file = self._create_temp_dataset_file(mutant_dict)
                try:
                    retcode, output = self._run_unittest_against_file(temp_file)
                    self.assertNotEqual(retcode, 0)
                    self.assertIn("test_05_mandatory_negative_categories_present", output)
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

    # =========================================================================
    # 6. DUPLICATE IDS, DUPLICATE TEXT & EMPTY TEXT
    # =========================================================================

    def test_17_rejects_duplicate_ids(self):
        """Verifies duplicate item IDs cause hard validation failure."""
        mutant_items = copy.deepcopy(self.base_items)
        mutant_items[1]["id"] = mutant_items[0]["id"]

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Duplicate IDs detected" in e for e in report.errors))

        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_06_unique_identifiers", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_18_rejects_empty_or_whitespace_text(self):
        """Verifies empty or whitespace-only text fails validation."""
        for bad_text in ["", "   \t\n  "]:
            mutant_items = copy.deepcopy(self.base_items)
            mutant_items[0]["text"] = bad_text

            report = validate_golden_eval_data({"version": "1.0", "items": mutant_items})
            self.assertFalse(report.passed)
            self.assertTrue(any("'text' is empty or missing" in e for e in report.errors))

    def test_19_rejects_duplicate_text_content(self):
        """Verifies duplicate normalized text across different items fails validation."""
        mutant_items = copy.deepcopy(self.base_items)
        mutant_items[1]["text"] = mutant_items[0]["text"].upper()

        mutant_dict = {"version": "1.0", "items": mutant_items}
        report = validate_golden_eval_data(mutant_dict)
        self.assertFalse(report.passed)
        self.assertTrue(any("Duplicate text content detected" in e for e in report.errors))

        temp_file = self._create_temp_dataset_file(mutant_dict)
        try:
            retcode, output = self._run_unittest_against_file(temp_file)
            self.assertNotEqual(retcode, 0)
            self.assertIn("test_07_text_deduplication", output)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # =========================================================================
    # 7. FAULTY PROVENANCE COORDINATES
    # =========================================================================

    def test_20_rejects_trivial_or_placeholder_provenance_file(self):
        """Verifies placeholder provenance file values (test, sample, n/a, todo) fail validation."""
        for placeholder in ["", "test", "sample", "todo", "tbd", "n/a", "none"]:
            mutant_items = copy.deepcopy(self.base_items)
            prov = mutant_items[0].get("provenance") or mutant_items[0].get("source")
            if "source_file" in prov:
                prov["source_file"] = placeholder
            else:
                prov["file"] = placeholder

            mutant_dict = {"version": "1.0", "items": mutant_items}
            report = validate_golden_eval_data(mutant_dict)
            self.assertFalse(report.passed, f"Failed to reject placeholder source.file: '{placeholder}'")
            self.assertTrue(any("'source.file' is trivial or empty" in e for e in report.errors))

    def test_21_rejects_trivial_or_placeholder_line_or_page(self):
        """Verifies placeholder provenance coordinates (0, none, n/a, todo) fail validation."""
        for placeholder in ["", "0", "none", "na", "todo", "tbd"]:
            mutant_items = copy.deepcopy(self.base_items)
            prov = mutant_items[0].get("provenance") or mutant_items[0].get("source")
            prov["line_or_page"] = placeholder

            mutant_dict = {"version": "1.0", "items": mutant_items}
            report = validate_golden_eval_data(mutant_dict)
            self.assertFalse(report.passed, f"Failed to reject placeholder line_or_page: '{placeholder}'")
            self.assertTrue(any("'source.line_or_page' is trivial or empty" in e for e in report.errors))

    # =========================================================================
    # 8. REAL DATASET CONFORMITY & STRICT-MODE AUDIT
    # =========================================================================

    def test_22_real_dataset_passes_standard_validation(self):
        """Empirically confirms the real golden_eval_set.json passes standard validation."""
        report = validate_golden_eval_data(self.real_data, strict_mode=False)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.errors), 0)
        self.assertEqual(report.stats["total_items"], 111)
        self.assertEqual(report.stats["positive_count"], 56)
        self.assertEqual(report.stats["negative_count"], 55)
        self.assertEqual(len(report.stats["intent_distribution"]), 14)

    def test_23_real_dataset_passes_unit_test_suite(self):
        """Empirically confirms test_golden_eval_set.py passes completely on real data."""
        retcode, output = self._run_unittest_against_file(self.real_dataset_path)
        self.assertEqual(retcode, 0, f"Regression test suite failed on real dataset:\n{output}")
        self.assertIn("Ran 10 tests", output)
        self.assertIn("OK", output)

    def test_24_strict_mode_warning_surface_audit(self):
        """
        Adversarial audit of strict mode behavior:
        Quantifies warnings that escalate to errors in strict mode:
        1. 'examples' instead of canonical 'items'
        2. 'provenance' instead of 'source' (Draft-07 schema check)
        3. Short text snippets in negative samples (e.g. MCQ options like '(D)')
        """
        report = validate_golden_eval_data(self.real_data, strict_mode=True)
        # In strict mode, warnings escalate to errors
        self.assertFalse(report.passed)
        self.assertGreater(len(report.errors), 0)
        
        # Verify specific classes of warnings escalated
        has_schema_notice = any("Schema notice" in e for e in report.errors)
        has_examples_array_notice = any("Found 'examples' array" in e for e in report.errors)
        has_short_text_notice = any("Text length is suspiciously short" in e for e in report.errors)

        self.assertTrue(has_schema_notice, "Expected schema notice regarding 'provenance' vs 'source'")
        self.assertTrue(has_examples_array_notice, "Expected notice regarding 'examples' vs 'items'")
        self.assertTrue(has_short_text_notice, "Expected notice regarding short OCR/MCQ option negative texts")


if __name__ == "__main__":
    unittest.main()
