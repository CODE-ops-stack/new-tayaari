#!/usr/bin/env python3
"""
Internal self-verification script for test_v13_semantic_extractor.py logic.
Verifies that:
1. All golden evaluation set fixtures load correctly.
2. The 14 intents test assertions succeed on synthetic mock nodes matching golden expectations.
3. The 6 noise rejection test assertions correctly fail if an item is falsely accepted.
4. The normalizer test assertions validate table propositions, column stitching, and watermark stripping.
"""

import sys
import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from proposed_test_v13_semantic_extractor import (
        BaseV13TestHarness,
        KnowledgeNode,
        NormalizedBlock,
        BlockType,
        canonicalize_intent,
        CANONICAL_14_INTENTS
    )
except ImportError:
    from .proposed_test_v13_semantic_extractor import (
        BaseV13TestHarness,
        KnowledgeNode,
        NormalizedBlock,
        BlockType,
        canonicalize_intent,
        CANONICAL_14_INTENTS
    )


class MockSemanticExtractor:
    """Mock extractor that mirrors ground-truth golden evaluation fixtures."""
    def __init__(self, golden_positives, golden_negatives):
        self.golden_positives = golden_positives
        self.golden_negatives = golden_negatives

    def extract(self, text: str):
        # Check if text matches any golden positive item
        for ex in self.golden_positives.values():
            if ex["text"].strip() == text.strip():
                pe = ex.get("semantic_entities", {}).get("primary_entity", "Entity")
                pred = ex.get("semantic_entities", {}).get("predicate", "Predicate")
                secs = ex.get("semantic_entities", {}).get("secondary_entities", [])
                
                # Intent-specific slotting mock
                quant = "99.86%" if "99.86" in text else None
                cond = "new moon phase" if "solar eclipse" in text.lower() else None

                return [KnowledgeNode(
                    node_id=ex["id"],
                    intent_type=ex["intent"],
                    primary_entity=pe,
                    predicate=pred,
                    secondary_entities=secs,
                    conditions=cond,
                    quantitative_data=quant,
                    raw_evidence=text,
                    source_location=ex.get("provenance")
                )]
        
        # Check if text matches golden negative item -> reject (return empty)
        for ex in self.golden_negatives.values():
            if ex["text"].strip() == text.strip():
                return []
        
        return []


class MockNormalizer:
    """Mock normalizer validating normalizer test contracts."""
    def normalize_block(self, raw_block):
        text = raw_block.get("text", "")
        if "|" in text:
            sentences = [
                "Saturn has a mean density of 0.69 g/cm^3 and orbital period of 10759 days.",
                "Earth has a mean density of 5.51 g/cm^3 and orbital period of 365.25 days.",
                "Mercury has a mean density of 5.43 g/cm^3 and orbital period of 88 days."
            ]
            return NormalizedBlock(
                id=raw_block.get("sourceId", "mock_id"),
                text=text,
                block_type=BlockType.TABLE,
                clean_sentences=sentences,
                metadata=raw_block
            )
        return NormalizedBlock(
            id=raw_block.get("sourceId", "mock_id"),
            text=text,
            block_type=BlockType.PROSE,
            clean_sentences=[text],
            metadata=raw_block
        )

    def stitch_columns(self, text: str) -> str:
        # Simple regex stitcher for soft-wraps
        res = text.replace("shining in\nthe sky", "shining in the sky")
        res = res.replace("immense and\nsupports", "immense and supports")
        return res

    def strip_watermarks(self, text: str) -> str:
        for wm in ["PARMAR SSC", "ISBN 81-7450-491-5", "Textbook in Geography for Class VI", "www.ssccglpinnacle.com"]:
            text = text.replace(wm + "\n", "").replace(wm, "")
        return text.strip()


class TestSuiteSelfVerification(BaseV13TestHarness):
    """Executes all 25 test methods against mock reference implementations to guarantee assertion soundness."""

    def setUp(self):
        self.extractor = MockSemanticExtractor(self.positives_by_id, self.negatives_by_id)
        self.normalizer = MockNormalizer()

    def test_verify_fixture_loading(self):
        self.assertEqual(len(self.positives_by_id), 56)
        self.assertEqual(len(self.negatives_by_id), 55)
        self.assertEqual(len(self.positives_by_intent), 14)
        self.assertEqual(len(self.negatives_by_category), 6)

    def test_verify_mock_passes_all_14_intents(self):
        for intent in CANONICAL_14_INTENTS:
            items = self.positives_by_intent.get(intent)
            self.assertIsNotNone(items, f"Missing items for intent {intent}")
            self.assertEqual(len(items), 4)

            # Test first item for each intent
            first_item = items[0]
            nodes = self.extractor.extract(first_item["text"])
            self.assertEqual(len(nodes), 1)
            self.assertEqual(canonicalize_intent(nodes[0].intent_type), intent)

    def test_verify_mock_rejects_all_55_negatives(self):
        for neg in self.negatives_by_id.values():
            nodes = self.extractor.extract(neg["text"])
            self.assertEqual(len(nodes), 0, f"Failed rejection on {neg['id']}")

    def test_verify_normalizer_table(self):
        table_markdown = "| Celestial Body | Mean Density |\n|---|---|\n| Saturn | 0.69 |"
        norm = self.normalizer.normalize_block({"sourceId": "tbl", "text": table_markdown})
        self.assertEqual(norm.type, BlockType.TABLE)
        self.assertTrue(any("0.69" in s for s in norm.clean_sentences))

    def test_verify_normalizer_stitching(self):
        text = "shining in\nthe sky"
        stitched = self.normalizer.stitch_columns(text)
        self.assertEqual(stitched, "shining in the sky")

    def test_verify_normalizer_watermark(self):
        text = "PARMAR SSC\nValid sentence."
        cleaned = self.normalizer.strip_watermarks(text)
        self.assertNotIn("PARMAR SSC", cleaned)
        self.assertIn("Valid sentence.", cleaned)


if __name__ == "__main__":
    unittest.main()
