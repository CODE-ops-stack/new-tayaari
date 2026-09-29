#!/usr/bin/env python3
"""
tests/test_v13_semantic_extractor.py
====================================
Comprehensive Unit Test Suite for V13 Semantic Extractor & Normalizer (Milestone 2).

Target Deliverables Under Test:
- v13_discovery/semantic_extractor.py (14-Intent Semantic Knowledge Representation Engine)
- v13_discovery/normalizer.py (Table Parser, Column Stitcher, Watermark Filter)
- data/golden_eval_set.json (Canonical 111-item evaluation benchmark)

Test Coverage:
1. All 14 R2 Semantic Intents (1 test per intent, verifying intent classification & slotting):
   - definition, attribute, cause/effect, comparison, spatial, distribution, classification,
     quantity, sequence, condition, exception, process, part-of, member-of.
2. Negative Noise Rejection (6 failure categories, verifying 0 false acceptances):
   - mcq_leakage (10 items)
   - watermark_header (9 items)
   - syntactic_fragment (9 items)
   - broken_reading_order (9 items)
   - table_formatting_artifact (9 items)
   - anaphoric_unresolved (9 items)
3. Ingestion & Normalization:
   - Markdown table ingestion -> produces valid propositions.
   - Broken column stitcher -> reconstructs continuous sentences across line wraps.
   - Watermark filter -> strips headers/footers without altering prose.

Run with:
    python -m unittest tests.test_v13_semantic_extractor
    pytest tests/test_v13_semantic_extractor.py
"""

import json
import os
import re
import sys
import unittest
from typing import Dict, List, Optional, Any

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Intent canonicalization and alias dictionary
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

def canonicalize_intent(intent: str) -> str:
    """Normalize intent strings to canonical snake_case format."""
    if not intent:
        return "none"
    norm = intent.strip().lower()
    return INTENT_ALIASES.get(norm, norm)


# Graceful import / Contract definition for V13 Discovery modules
try:
    from v13_discovery.semantic_extractor import SemanticExtractor, KnowledgeNode
    from v13_discovery.normalizer import Normalizer, NormalizedBlock, BlockType
    V13_MODULES_AVAILABLE = True
except ImportError:
    # Contract Stubs for early test verification / TDD guidance
    V13_MODULES_AVAILABLE = False
    
    class KnowledgeNode:
        def __init__(
            self,
            node_id: str,
            intent_type: str,
            primary_entity: str,
            predicate: str,
            secondary_entities: Optional[List[str]] = None,
            conditions: Optional[Any] = None,
            quantitative_data: Optional[Any] = None,
            raw_evidence: str = "",
            source_location: Optional[Dict[str, Any]] = None,
        ):
            self.node_id = node_id
            self.intent_type = intent_type
            self.primary_entity = primary_entity
            self.predicate = predicate
            self.secondary_entities = secondary_entities or []
            self.conditions = conditions
            self.quantitative_data = quantitative_data
            self.raw_evidence = raw_evidence
            self.source_location = source_location or {}

    class BlockType:
        PROSE = "PROSE"
        TABLE = "TABLE"

    class NormalizedBlock:
        def __init__(
            self,
            id: str,
            text: str,
            block_type: str,
            clean_sentences: List[str],
            metadata: Optional[Dict[str, Any]] = None,
        ):
            self.id = id
            self.text = text
            self.type = block_type
            self.clean_sentences = clean_sentences
            self.metadata = metadata or {}

    class SemanticExtractor:
        """Reference stub matching PROJECT.md interface contract."""
        def extract(self, block_or_text: Any) -> List[KnowledgeNode]:
            raise NotImplementedError("v13_discovery.semantic_extractor not yet implemented by worker")

    class Normalizer:
        """Reference stub matching PROJECT.md interface contract."""
        def normalize_block(self, raw_block: Dict[str, Any]) -> NormalizedBlock:
            raise NotImplementedError("v13_discovery.normalizer not yet implemented by worker")

        def stitch_columns(self, text: str) -> str:
            raise NotImplementedError("v13_discovery.normalizer not yet implemented by worker")

        def strip_watermarks(self, text: str) -> str:
            raise NotImplementedError("v13_discovery.normalizer not yet implemented by worker")


class BaseV13TestHarness(unittest.TestCase):
    """Base test harness loading golden evaluation dataset fixtures."""

    @classmethod
    def setUpClass(cls):
        # Locate golden_eval_set.json
        candidate_paths = [
            os.environ.get("GOLDEN_EVAL_SET_PATH"),
            os.path.join(REPO_ROOT, "data", "golden_eval_set.json"),
            os.path.abspath(os.path.join(os.getcwd(), "data", "golden_eval_set.json")),
        ]
        cls.eval_path = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                cls.eval_path = p
                break

        if not cls.eval_path:
            raise FileNotFoundError(f"data/golden_eval_set.json not found in candidate paths: {candidate_paths}")

        with open(cls.eval_path, "r", encoding="utf-8") as f:
            cls.raw_data = json.load(f)

        examples = cls.raw_data.get("examples") or cls.raw_data.get("items", [])
        cls.positives_by_id = {ex["id"]: ex for ex in examples if ex.get("expected_label") == "positive"}
        cls.negatives_by_id = {ex["id"]: ex for ex in examples if ex.get("expected_label") == "negative"}

        # Group positives by canonical intent
        cls.positives_by_intent: Dict[str, List[Dict[str, Any]]] = {}
        for ex in cls.positives_by_id.values():
            canon = canonicalize_intent(ex.get("intent", ""))
            cls.positives_by_intent.setdefault(canon, []).append(ex)

        # Group negatives by rejection category
        cls.negatives_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for ex in cls.negatives_by_id.values():
            cat = ex.get("rejection_category", "unknown")
            cls.negatives_by_category.setdefault(cat, []).append(ex)


# =============================================================================
# PART 1: 14 SEMANTIC INTENTS EXTRACTION & SLOTTING TESTS
# =============================================================================

class TestV13SemanticExtractorIntents(BaseV13TestHarness):
    """
    Verifies that the V13 semantic extractor successfully identifies and slots
    each of the 14 semantic intents from data/golden_eval_set.json.
    Exactly 1 dedicated test case per intent (14 tests total).
    """

    def setUp(self):
        if not V13_MODULES_AVAILABLE:
            self.skipTest("v13_discovery.semantic_extractor not yet implemented by worker")
        self.extractor = SemanticExtractor()

    def _assert_intent_slotting(
        self,
        item_id: str,
        expected_intent: str,
        expected_entity_substr: str,
        validate_fn=None
    ):
        """Helper to run extraction on a golden item and assert semantic slotting."""
        item = self.positives_by_id.get(item_id)
        self.assertIsNotNone(item, f"Fixture item {item_id} missing from golden_eval_set.json")

        nodes = self.extractor.extract(item["text"])
        self.assertGreaterEqual(
            len(nodes), 1,
            f"Failed to extract knowledge node for item [{item_id}] text: '{item['text'][:80]}...'"
        )

        primary_node = nodes[0]
        actual_intent = canonicalize_intent(primary_node.intent_type)
        self.assertEqual(
            actual_intent, canonicalize_intent(expected_intent),
            f"Item [{item_id}] intent mismatch: expected '{expected_intent}', got '{primary_node.intent_type}'"
        )

        self.assertIn(
            expected_entity_substr.lower(),
            primary_node.primary_entity.lower(),
            f"Item [{item_id}] primary entity mismatch: expected '{expected_entity_substr}' in '{primary_node.primary_entity}'"
        )
        self.assertTrue(
            bool(primary_node.predicate and primary_node.predicate.strip()),
            f"Item [{item_id}] predicate must not be empty"
        )

        if validate_fn:
            validate_fn(primary_node, item)

    def test_01_intent_definition(self):
        """1. Intent: definition — POS-001 (Celestial bodies definition)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            # Verify defining predicate captures celestial objects shining in night sky
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["night sky", "shining", "sun", "moon", "celestial"]),
                f"Predicate should capture definition semantics: {node.predicate}"
            )
        self._assert_intent_slotting("POS-001", "definition", "celestial bodies", validate)

    def test_02_intent_attribute(self):
        """2. Intent: attribute — POS-006 (Primary waves longitudinal compressional attributes)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["longitudinal", "compressional", "vibrate", "propagation"]),
                f"Predicate should capture kinematic attributes: {node.predicate}"
            )
        self._assert_intent_slotting("POS-006", "attribute", "Primary waves", validate)

    def test_03_intent_cause_effect(self):
        """3. Intent: cause/effect — POS-009 (Solar storms disrupting magnetosphere and power grids)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["disturb", "disrupt", "currents", "grids", "gps"]),
                f"Predicate should capture causal consequence: {node.predicate}"
            )
        self._assert_intent_slotting("POS-009", "cause_effect", "solar storms", validate)

    def test_04_intent_comparison(self):
        """4. Intent: comparison — POS-013 (Primary vs Secondary waves media propagation contrast)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["solid", "liquid", "gas", "whereas", "unlike", "exclusive"]),
                f"Predicate should capture comparative contrast: {node.predicate}"
            )
        self._assert_intent_slotting("POS-013", "comparison", "Primary seismic waves", validate)

    def test_05_intent_spatial(self):
        """5. Intent: spatial — POS-018 (Narmada River rift valley between Vindhya and Satpura)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["between", "rift valley", "vindhya", "satpura", "westward"]),
                f"Predicate should capture spatial coordinates and bounds: {node.predicate}"
            )
        self._assert_intent_slotting("POS-018", "spatial", "Narmada River", validate)

    def test_06_intent_distribution(self):
        """6. Intent: distribution — POS-021 (Global water distribution across oceans and polar ice)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in str(node.predicate).lower() for w in ["ocean", "percent", "concentrated", "97", "ice"]),
                f"Predicate should capture geographic distribution: {node.predicate}"
            )
        self._assert_intent_slotting("POS-021", "distribution", "Earth's total water", validate)

    def test_07_intent_classification(self):
        """7. Intent: classification — POS-025 (Three fundamental rock classes: igneous, sedimentary, metamorphic)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            # Verify secondary entities or predicate contains classification categories
            pred_or_secs = (node.predicate + " " + " ".join(node.secondary_entities)).lower()
            self.assertTrue(
                "igneous" in pred_or_secs or "sedimentary" in pred_or_secs or "metamorphic" in pred_or_secs,
                f"Classification should enumerate categories: {pred_or_secs}"
            )
        self._assert_intent_slotting("POS-025", "classification", "rocks", validate)

    def test_08_intent_quantity(self):
        """8. Intent: quantity — POS-029 (Sun constitutes 99.86% of solar system mass)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            quant = str(node.quantitative_data) if node.quantitative_data else ""
            self.assertTrue(
                "99.86" in quant or "99.86" in node.predicate,
                f"Quantity slotting must extract numerical metric (99.86%): {quant} / {node.predicate}"
            )
        self._assert_intent_slotting("POS-029", "quantity", "Sun", validate)

    def test_09_intent_sequence(self):
        """9. Intent: sequence — POS-033 (Stellar evolutionary life cycle sequence)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            pred_or_secs = (node.predicate + " " + " ".join(node.secondary_entities)).lower()
            self.assertTrue(
                any(stage in pred_or_secs for stage in ["protostar", "main sequence", "red giant", "white dwarf"]),
                f"Sequence must capture stages in order: {pred_or_secs}"
            )
        self._assert_intent_slotting("POS-033", "sequence", "stellar evolution", validate)

    def test_10_intent_condition(self):
        """10. Intent: condition — POS-037 (Solar eclipse conditions during new moon syzygy)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            cond_str = str(node.conditions) if node.conditions else ""
            self.assertTrue(
                any(w in (cond_str + " " + node.predicate).lower() for w in ["new moon", "alignment", "between", "syzygy"]),
                f"Condition must slot conditional requirements: {cond_str} / {node.predicate}"
            )
        self._assert_intent_slotting("POS-037", "condition", "solar eclipse", validate)

    def test_11_intent_exception(self):
        """11. Intent: exception — POS-041 (Venus and Uranus retrograde clockwise rotation exception)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["clockwise", "retrograde", "exception", "unlike", "east to west"]),
                f"Exception slotting must capture anomalous behavior: {node.predicate}"
            )
        self._assert_intent_slotting("POS-041", "exception", "Venus and Uranus", validate)

    def test_12_intent_process(self):
        """12. Intent: process — POS-045 (Seafloor spreading geodynamic mechanism)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            self.assertTrue(
                any(w in node.predicate.lower() for w in ["magma", "mid-ocean", "crust", "solidif", "outward"]),
                f"Process slotting must capture dynamic steps: {node.predicate}"
            )
        self._assert_intent_slotting("POS-045", "process", "Seafloor spreading", validate)

    def test_13_intent_part_of(self):
        """13. Intent: part-of — POS-049 (Solar corona outermost atmospheric layer of Sun)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            pred_or_secs = (node.predicate + " " + " ".join(node.secondary_entities)).lower()
            self.assertTrue(
                "sun" in pred_or_secs and any(w in pred_or_secs for w in ["outer", "layer", "atmosphere", "envelope"]),
                f"Part-of slotting must capture component/whole relation: {pred_or_secs}"
            )
        self._assert_intent_slotting("POS-049", "part_of", "solar corona", validate)

    def test_14_intent_member_of(self):
        """14. Intent: member-of — POS-053 (Ursa Major member of astronomical constellations)."""
        def validate(node: KnowledgeNode, item: Dict[str, Any]):
            pred_or_secs = (node.predicate + " " + " ".join(node.secondary_entities)).lower()
            self.assertTrue(
                "constellation" in pred_or_secs,
                f"Member-of slotting must capture class membership (constellations): {pred_or_secs}"
            )
        self._assert_intent_slotting("POS-053", "member_of", "Ursa Major", validate)


# =============================================================================
# PART 2: NEGATIVE NOISE REJECTION TESTS (0 FALSE ACCEPTANCES)
# =============================================================================

class TestV13NoiseRejection(BaseV13TestHarness):
    """
    Verifies that all 6 noise categories in data/golden_eval_set.json
    are correctly rejected with 0 false acceptances (100% precision on clean knowledge).
    """

    def setUp(self):
        if not V13_MODULES_AVAILABLE:
            self.skipTest("v13_discovery.semantic_extractor not yet implemented by worker")
        self.extractor = SemanticExtractor()

    def _assert_zero_false_acceptances(self, category_key: str):
        """Asserts that all items in a negative category yield 0 extracted knowledge nodes."""
        items = self.negatives_by_category.get(category_key, [])
        self.assertGreater(len(items), 0, f"No negative items found for category '{category_key}'")

        false_acceptances = []
        for item in items:
            nodes = self.extractor.extract(item["text"])
            if len(nodes) > 0:
                false_acceptances.append({
                    "id": item["id"],
                    "text": item["text"],
                    "accepted_nodes_count": len(nodes),
                    "accepted_entities": [n.primary_entity for n in nodes],
                })

        self.assertEqual(
            len(false_acceptances), 0,
            f"Negative category '{category_key}' violation: {len(false_acceptances)} false acceptances detected: {false_acceptances}"
        )

    def test_15_noise_mcq_leakage_rejected(self):
        """Verifies rejection of MCQ options, question letters, and answer keys (NEG-001 to NEG-010)."""
        self._assert_zero_false_acceptances("mcq_leakage")

    def test_16_noise_watermark_header_rejected(self):
        """Verifies rejection of publisher branding, ISBN, figure captions, and URLs (NEG-011 to NEG-019)."""
        self._assert_zero_false_acceptances("watermark_header")

    def test_17_noise_syntactic_fragment_rejected(self):
        """Verifies rejection of sentences ending abruptly in conjunctions or prepositions (NEG-020 to NEG-028)."""
        self._assert_zero_false_acceptances("syntactic_fragment")

    def test_18_noise_broken_reading_order_rejected(self):
        """Verifies rejection of cross-column collisions and smashed headings (NEG-029 to NEG-037)."""
        self._assert_zero_false_acceptances("broken_reading_order")

    def test_19_noise_table_formatting_artifact_rejected(self):
        """Verifies rejection of raw markdown table delimiters, lab craft lists, and code fences (NEG-038 to NEG-046)."""
        self._assert_zero_false_acceptances("table_formatting_artifact")

    def test_20_noise_anaphoric_unresolved_rejected(self):
        """Verifies rejection of sentences with unresolved pronouns ('They', 'It', 'These') (NEG-047 to NEG-055)."""
        self._assert_zero_false_acceptances("anaphoric_unresolved")

    def test_21_aggregate_noise_rejection_zero_false_acceptances(self):
        """Comprehensive verification across all 55 negative items in golden_eval_set.json."""
        total_negatives = len(self.negatives_by_id)
        self.assertEqual(total_negatives, 55, f"Expected exactly 55 negative items, found {total_negatives}")

        all_false_acceptances = []
        for item in self.negatives_by_id.values():
            nodes = self.extractor.extract(item["text"])
            if len(nodes) > 0:
                all_false_acceptances.append(item["id"])

        self.assertEqual(
            len(all_false_acceptances), 0,
            f"Zero False Acceptance Rule violated: {len(all_false_acceptances)} items falsely accepted: {all_false_acceptances}"
        )


# =============================================================================
# PART 3: INGESTION & NORMALIZER TESTS
# =============================================================================

class TestV13Normalizer(BaseV13TestHarness):
    """
    Verifies normalizer operations:
    1. Markdown table ingestion -> produces valid propositions.
    2. Broken column stitcher -> reconstructs continuous sentences.
    3. Watermark filter -> strips headers without altering prose.
    """

    def setUp(self):
        if not V13_MODULES_AVAILABLE:
            self.skipTest("v13_discovery.normalizer not yet implemented by worker")
        self.normalizer = Normalizer()

    def test_22_normalizer_markdown_table_ingestion(self):
        """Verifies markdown table parser produces valid propositions without leaking formatting delimiters."""
        table_markdown = (
            "| Celestial Body | Mean Density (g/cm^3) | Orbital Period (Days) |\n"
            "|---|---|---|\n"
            "| Saturn | 0.69 | 10759 |\n"
            "| Earth | 5.51 | 365.25 |\n"
            "| Mercury | 5.43 | 88 |"
        )
        raw_block = {
            "sourceId": "test_table_src",
            "path": "test_table.md",
            "text": table_markdown,
            "page_or_line": "lines 1-5"
        }

        normalized = self.normalizer.normalize_block(raw_block)

        # 1. Block type must be TABLE
        self.assertEqual(normalized.type, BlockType.TABLE)

        # 2. Must produce synthetic clean sentences
        self.assertGreaterEqual(
            len(normalized.clean_sentences), 3,
            f"Expected at least 3 proposition sentences for 3 table rows, got {len(normalized.clean_sentences)}"
        )

        # 3. Delimiter pipes '|' must NOT leak into clean sentences
        for sentence in normalized.clean_sentences:
            self.assertNotIn("|", sentence, f"Raw table delimiter leaked into proposition: '{sentence}'")
            self.assertNotIn("---", sentence, f"Table alignment row leaked into proposition: '{sentence}'")

        # 4. Content assertions: Saturn density proposition must be present
        saturn_prop = [s for s in normalized.clean_sentences if "Saturn" in s]
        self.assertTrue(len(saturn_prop) > 0, "Missing proposition for Saturn")
        self.assertIn("0.69", saturn_prop[0], "Saturn density metric 0.69 missing from proposition")

    def test_23_normalizer_broken_column_stitching(self):
        """Verifies column stitcher reconnects lines broken across columns or ending in prepositions/conjunctions."""
        # Simulated broken OCR wrap from geography_extracted.txt (NEG-023)
        broken_text = (
            "One would first notice one or two bright dots shining in\n"
            "the sky. Soon you would see the number increasing."
        )
        stitched = self.normalizer.stitch_columns(broken_text)

        # Must stitch "shining in\nthe sky" into "shining in the sky"
        self.assertIn(
            "shining in the sky", stitched,
            f"Failed to stitch terminal preposition wrap: '{stitched}'"
        )
        self.assertNotIn("shining in\nthe sky", stitched)

        # Simulated dangling conjunction wrap from geography_extracted_2.txt
        broken_conjunction = (
            "The Nile basin is immense and\n"
            "supports diverse agricultural settlements along its delta."
        )
        stitched_conj = self.normalizer.stitch_columns(broken_conjunction)
        self.assertIn(
            "immense and supports", stitched_conj,
            f"Failed to stitch dangling conjunction: '{stitched_conj}'"
        )

    def test_24_normalizer_watermark_stripping(self):
        """Verifies watermark cleaner strips headers, footers, and ISBNs while 100% preserving prose."""
        raw_text = (
            "PARMAR SSC\n"
            "The sun, the moon and all those objects shining in the night sky are called celestial bodies.\n"
            "ISBN 81-7450-491-5\n"
            "Textbook in Geography for Class VI\n"
            "Some celestial bodies are very big and hot.\n"
            "www.ssccglpinnacle.com\n"
            "They are made up of gases."
        )

        cleaned = self.normalizer.strip_watermarks(raw_text)

        # Watermarks must be completely stripped
        forbidden_watermarks = [
            "PARMAR SSC",
            "ISBN 81-7450-491-5",
            "Textbook in Geography for Class VI",
            "www.ssccglpinnacle.com"
        ]
        for wm in forbidden_watermarks:
            self.assertNotIn(wm, cleaned, f"Watermark '{wm}' was not stripped by normalizer")

        # Substantive educational prose must remain 100% intact
        self.assertIn(
            "The sun, the moon and all those objects shining in the night sky are called celestial bodies.",
            cleaned,
            "Canonical definition prose was corrupted or stripped"
        )
        self.assertIn(
            "Some celestial bodies are very big and hot.",
            cleaned,
            "Attribute prose was corrupted or stripped"
        )

    def test_25_provenance_preservation(self):
        """Verifies normalizer preserves unbreakable source provenance metadata."""
        raw_block = {
            "sourceId": "SRC-NCERT-GEO-06",
            "path": "source-material/geography_extracted.txt",
            "text": "The sun, the moon and all those objects shining in the night sky are called celestial bodies.",
            "page_or_line": "lines 36-37"
        }
        normalized = self.normalizer.normalize_block(raw_block)

        self.assertEqual(normalized.metadata.get("sourceId"), "SRC-NCERT-GEO-06")
        self.assertEqual(normalized.metadata.get("path"), "source-material/geography_extracted.txt")
        self.assertEqual(normalized.metadata.get("page_or_line"), "lines 36-37")


if __name__ == "__main__":
    unittest.main()
