#!/usr/bin/env python3
"""
test_golden_eval_set.py
=======================
Automated Regression Test Suite for Golden Evaluation Dataset (data/golden_eval_set.json).

Designed to be placed at tests/test_golden_eval_set.py and executed with:
    python -m pytest tests/test_golden_eval_set.py
    python -m unittest tests.test_golden_eval_set
"""

import unittest
import os
import json
import re
from collections import Counter

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

CANONICAL_14_INTENTS = {
    "definition",
    "attribute",
    "cause_effect",
    "comparison",
    "spatial",
    "distribution",
    "classification",
    "quantity",
    "sequence",
    "condition",
    "exception",
    "process",
    "part_of",
    "member_of",
}

INTENT_ALIASES = {
    "definition": "definition",
    "attribute": "attribute",
    "cause/effect": "cause_effect",
    "cause-effect": "cause_effect",
    "cause_effect": "cause_effect",
    "cause and effect": "cause_effect",
    "comparison": "comparison",
    "spatial": "spatial",
    "distribution": "distribution",
    "classification": "classification",
    "quantity": "quantity",
    "sequence": "sequence",
    "condition": "condition",
    "exception": "exception",
    "process": "process",
    "part-of": "part_of",
    "part_of": "part_of",
    "member-of": "member_of",
    "member_of": "member_of",
}

MANDATORY_NEGATIVE_CATEGORIES = {
    "mcq_noise",
    "watermark_noise",
    "incomplete_clause_fragment",
    "ocr_artifact",
}

NOISE_ALIASES = {
    "mcq_noise": "mcq_noise",
    "mcq_leakage": "mcq_noise",
    "option_marker": "mcq_noise",
    "option_marker_artifact": "mcq_noise",
    "watermark_noise": "watermark_noise",
    "watermark": "watermark_noise",
    "watermark_header": "watermark_noise",
    "header_footer": "watermark_noise",
    "header_footer_metadata": "watermark_noise",
    "incomplete_clause_fragment": "incomplete_clause_fragment",
    "syntactic_fragment": "incomplete_clause_fragment",
    "fragment": "incomplete_clause_fragment",
    "ocr_artifact": "ocr_artifact",
    "ocr_noise": "ocr_artifact",
    "broken_reading_order": "ocr_artifact",
    "column_break": "ocr_artifact",
    "multi_column_break": "ocr_artifact",
    "table_artifact": "table_artifact",
    "table_formatting_artifact": "table_artifact",
    "pure_table_formatting": "table_artifact",
    "anaphoric_reference": "anaphoric_reference",
    "anaphoric_unresolved": "anaphoric_reference",
}

TRIVIAL_STRINGS = {"test", "sample", "foo", "bar", "n/a", "na", "todo", "tbd", "unknown", "none", "0"}


class TestGoldenEvaluationSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Flexible path resolution for data/golden_eval_set.json
        candidate_paths = [
            os.environ.get("GOLDEN_EVAL_SET_PATH"),
            os.path.abspath(os.path.join(os.getcwd(), "data", "golden_eval_set.json")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "golden_eval_set.json")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "golden_eval_set.json")),
        ]
        
        cls.eval_path = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                cls.eval_path = p
                break
                
        if not cls.eval_path:
            # Default to canonical repo location
            cls.eval_path = os.path.abspath(os.path.join(os.getcwd(), "data", "golden_eval_set.json"))

        if os.path.exists(cls.eval_path):
            with open(cls.eval_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                cls.data = {"version": "1.0", "items": raw}
            else:
                cls.data = raw
            cls.items = cls.data.get("items") or cls.data.get("examples", [])
        else:
            cls.data = {}
            cls.items = []

    def test_01_dataset_file_exists(self):
        """Asserts that data/golden_eval_set.json exists on disk."""
        self.assertTrue(
            os.path.exists(self.eval_path),
            f"Golden evaluation set missing at expected path: {self.eval_path}"
        )

    def test_02_total_item_count(self):
        """Asserts total items in golden evaluation set is >= 100."""
        self.assertGreaterEqual(
            len(self.items), 100,
            f"Golden evaluation set must contain >= 100 items; found {len(self.items)}."
        )

    def test_03_positive_and_negative_counts(self):
        """Asserts positive examples >= 50 and negative examples >= 50."""
        positives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "positive"]
        negatives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "negative"]

        self.assertGreaterEqual(
            len(positives), 50,
            f"Positive examples must be >= 50; found {len(positives)}."
        )
        self.assertGreaterEqual(
            len(negatives), 50,
            f"Negative examples must be >= 50; found {len(negatives)}."
        )

    def test_04_all_14_intents_represented(self):
        """Asserts that all 14 required semantic intents are present among positive items."""
        positives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "positive"]
        found_intents = set()

        for item in positives:
            raw_intent = item.get("expected_intent") or item.get("intent")
            if raw_intent:
                canon = INTENT_ALIASES.get(raw_intent.strip().lower(), raw_intent.strip().lower())
                found_intents.add(canon)

        missing = CANONICAL_14_INTENTS - found_intents
        self.assertEqual(
            len(missing), 0,
            f"Representation failure: All 14 semantic intents must be represented. Missing {len(missing)} intents: {sorted(list(missing))}"
        )

    def test_05_mandatory_negative_categories_present(self):
        """Asserts presence of MCQ noise, watermark noise, incomplete clause fragments, and OCR artifacts."""
        negatives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "negative"]
        found_noise = set()

        for item in negatives:
            raw_noise = item.get("noise_type") or item.get("rejection_category") or item.get("rejection_reason_category") or item.get("category")
            if raw_noise:
                canon = NOISE_ALIASES.get(raw_noise.strip().lower(), raw_noise.strip().lower())
                found_noise.add(canon)

        missing = MANDATORY_NEGATIVE_CATEGORIES - found_noise
        self.assertEqual(
            len(missing), 0,
            f"Negative noise failure: Mandatory noise categories missing: {sorted(list(missing))}"
        )

    def test_06_unique_identifiers(self):
        """Asserts that all item IDs are strictly unique."""
        ids = [item.get("id") for item in self.items if item.get("id")]
        self.assertEqual(
            len(ids), len(self.items),
            "Every item must have a valid 'id' property."
        )
        id_counts = Counter(ids)
        dups = [item_id for item_id, count in id_counts.items() if count > 1]
        self.assertEqual(
            len(dups), 0,
            f"Duplicate IDs detected: {dups}"
        )

    def test_07_text_deduplication(self):
        """Asserts that no two items share identical normalized text."""
        texts = [re.sub(r'\s+', ' ', item.get("text", "").strip().lower()) for item in self.items]
        text_counts = Counter(texts)
        dups = [txt[:60] + "..." for txt, count in text_counts.items() if count > 1 and txt]
        self.assertEqual(
            len(dups), 0,
            f"Duplicate text entries detected: {dups}"
        )

    def test_08_non_trivial_provenance(self):
        """Asserts that provenance fields (source.file and source.line_or_page) are non-empty and non-trivial."""
        for item in self.items:
            item_id = item.get("id", "UNKNOWN")
            source = item.get("source") or item.get("provenance")
            self.assertIsInstance(
                source, dict,
                f"Item [{item_id}]: 'source' / 'provenance' must be an object."
            )
            src_file = str(source.get("file") or source.get("source_file") or "").strip().lower()
            src_loc = str(source.get("line_or_page") or "").strip().lower()

            self.assertTrue(
                src_file and src_file not in TRIVIAL_STRINGS,
                f"Item [{item_id}]: 'source.file' is empty or trivial ('{src_file}')."
            )
            self.assertTrue(
                src_loc and src_loc not in TRIVIAL_STRINGS,
                f"Item [{item_id}]: 'source.line_or_page' is empty or trivial ('{src_loc}')."
            )

    def test_09_positive_entities_and_claims(self):
        """Asserts positive examples include extracted_entities and expected_truth_claim."""
        positives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "positive"]
        for item in positives:
            item_id = item.get("id", "UNKNOWN")
            entities = item.get("extracted_entities") or item.get("semantic_entities")
            self.assertTrue(
                entities is not None and (len(entities) > 0 if isinstance(entities, (list, dict)) else True),
                f"Positive item [{item_id}]: 'extracted_entities' / 'semantic_entities' must not be empty."
            )
            claim = item.get("expected_truth_claim") or item.get("rationale")
            self.assertTrue(
                isinstance(claim, str) and len(claim.strip()) >= 5,
                f"Positive item [{item_id}]: 'expected_truth_claim' / 'rationale' must be a non-empty descriptive string."
            )

    def test_10_negative_rejection_reasons(self):
        """Asserts negative examples include expected_rejection_reason."""
        negatives = [it for it in self.items if (it.get("expected_label") or it.get("label")) == "negative"]
        for item in negatives:
            item_id = item.get("id", "UNKNOWN")
            reason = item.get("expected_rejection_reason") or item.get("rejection_reason")
            self.assertTrue(
                isinstance(reason, str) and len(reason.strip()) >= 5,
                f"Negative item [{item_id}]: 'expected_rejection_reason' must be a non-empty string explaining rejection."
            )


if __name__ == "__main__":
    unittest.main()
