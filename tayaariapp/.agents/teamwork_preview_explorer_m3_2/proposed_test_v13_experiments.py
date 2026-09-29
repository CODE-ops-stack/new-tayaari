#!/usr/bin/env python3
"""
tests/test_v13_experiments.py
=============================
Unit Test Suite for Milestone 3 Comparative Architecture & Metrics Engine.

Verifies:
1. MetricCalculator mathematical correctness (Precision, Recall, FAR, FRR, F1, Latency, Throughput).
2. Zero division safeguards across edge cases (all TP, all FP, all FN, all TN, empty results).
3. DeterministicLLMStub schema conformance, deterministic behavior, and offline safety.
4. BaseExtractorAdapter implementations for Approach A, B, and C.
5. ExperimentBenchmarkRunner full end-to-end execution on data/golden_eval_set.json.
6. experiment_metrics.json schema validation and production threshold compliance.
"""

import os
import sys
import json
import unittest
from typing import Dict, List, Any

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

# Try importing from v13_discovery.experiments or fallback to proposed_experiments for explorer tests
try:
    from v13_discovery.experiments import (
        ExtractionResult,
        BinaryMetrics,
        IntentMetrics,
        NoiseRejectionMetrics,
        LatencyMetrics,
        DeterministicLLMStub,
        BaseExtractorAdapter,
        RuleBasedAdapter,
        StructuredLLMAdapter,
        HybridPipelineAdapter,
        MetricCalculator,
        ExperimentBenchmarkRunner,
    )
except ImportError:
    # Explorer local test fallback
    AGENT_DIR = os.path.abspath(os.path.join(REPO_ROOT, ".agents", "teamwork_preview_explorer_m3_2"))
    if AGENT_DIR not in sys.path:
        sys.path.insert(0, AGENT_DIR)
    from proposed_experiments import (
        ExtractionResult,
        BinaryMetrics,
        IntentMetrics,
        NoiseRejectionMetrics,
        LatencyMetrics,
        DeterministicLLMStub,
        BaseExtractorAdapter,
        RuleBasedAdapter,
        StructuredLLMAdapter,
        HybridPipelineAdapter,
        MetricCalculator,
        ExperimentBenchmarkRunner,
    )

from v13_discovery.semantic_extractor import KnowledgeNode


class TestMetricCalculatorMath(unittest.TestCase):
    """Verifies mathematical accuracy and boundary condition handling of MetricCalculator."""

    def test_01_perfect_classification(self):
        """TP=50, TN=50, FP=0, FN=0 -> Precision=1.0, Recall=1.0, F1=1.0, FAR=0.0, FRR=0.0."""
        results = []
        for i in range(50):
            node = KnowledgeNode(node_id=f"pos_{i}", intent_type="definition", primary_entity="Sun", predicate="is star")
            results.append(ExtractionResult(
                item_id=f"pos_{i}",
                raw_text="The Sun is a star.",
                expected_label="positive",
                expected_intent="definition",
                rejection_category=None,
                predicted_node=node,
                latency_ms=1.0
            ))
        for j in range(50):
            results.append(ExtractionResult(
                item_id=f"neg_{j}",
                raw_text="(a) Mars (b) Venus",
                expected_label="negative",
                expected_intent=None,
                rejection_category="mcq_leakage",
                predicted_node=None,
                latency_ms=1.0
            ))

        bm = MetricCalculator.compute_binary_metrics(results)
        self.assertEqual(bm.true_positives, 50)
        self.assertEqual(bm.false_positives, 0)
        self.assertEqual(bm.true_negatives, 50)
        self.assertEqual(bm.false_negatives, 0)
        self.assertAlmostEqual(bm.precision, 1.0)
        self.assertAlmostEqual(bm.recall, 1.0)
        self.assertAlmostEqual(bm.f1_score, 1.0)
        self.assertAlmostEqual(bm.false_acceptance_rate, 0.0)
        self.assertAlmostEqual(bm.false_rejection_rate, 0.0)

    def test_02_total_false_rejection_v12_baseline(self):
        """Simulates V12 baseline where all positive items are rejected (FN=50, TP=0)."""
        results = []
        for i in range(50):
            results.append(ExtractionResult(
                item_id=f"pos_{i}",
                raw_text="Valid educational fact.",
                expected_label="positive",
                expected_intent="definition",
                rejection_category=None,
                predicted_node=None,  # Falsely rejected!
                latency_ms=0.5
            ))
        for j in range(50):
            results.append(ExtractionResult(
                item_id=f"neg_{j}",
                raw_text="Noise header.",
                expected_label="negative",
                expected_intent=None,
                rejection_category="watermark_header",
                predicted_node=None,
                latency_ms=0.5
            ))

        bm = MetricCalculator.compute_binary_metrics(results)
        self.assertEqual(bm.true_positives, 0)
        self.assertEqual(bm.false_negatives, 50)
        self.assertEqual(bm.true_negatives, 50)
        self.assertEqual(bm.false_positives, 0)
        self.assertAlmostEqual(bm.recall, 0.0)
        self.assertAlmostEqual(bm.false_rejection_rate, 1.0)
        self.assertAlmostEqual(bm.f1_score, 0.0)

    def test_03_total_false_acceptance_catastrophe(self):
        """Simulates catastrophic extractor that accepts all negative noise (FP=50, TN=0)."""
        results = []
        for i in range(50):
            node = KnowledgeNode(node_id=f"pos_{i}", intent_type="definition", primary_entity="Earth", predicate="is planet")
            results.append(ExtractionResult(
                item_id=f"pos_{i}",
                raw_text="Earth is a planet.",
                expected_label="positive",
                expected_intent="definition",
                rejection_category=None,
                predicted_node=node,
                latency_ms=1.0
            ))
        for j in range(50):
            bad_node = KnowledgeNode(node_id=f"bad_{j}", intent_type="definition", primary_entity="Noise", predicate="leaked")
            results.append(ExtractionResult(
                item_id=f"neg_{j}",
                raw_text="Page 12 of 100",
                expected_label="negative",
                expected_intent=None,
                rejection_category="watermark_header",
                predicted_node=bad_node,  # Falsely accepted!
                latency_ms=1.0
            ))

        bm = MetricCalculator.compute_binary_metrics(results)
        self.assertEqual(bm.true_positives, 50)
        self.assertEqual(bm.false_positives, 50)
        self.assertEqual(bm.true_negatives, 0)
        self.assertEqual(bm.false_negatives, 0)
        self.assertAlmostEqual(bm.precision, 0.5)
        self.assertAlmostEqual(bm.recall, 1.0)
        self.assertAlmostEqual(bm.false_acceptance_rate, 1.0)
        self.assertAlmostEqual(bm.f1_score, 2 * 0.5 * 1.0 / (0.5 + 1.0), places=3)

    def test_04_zero_division_safety(self):
        """Verifies no ZeroDivisionError occurs on empty results list."""
        bm = MetricCalculator.compute_binary_metrics([])
        self.assertEqual(bm.precision, 0.0)
        self.assertEqual(bm.recall, 0.0)
        self.assertEqual(bm.f1_score, 0.0)
        self.assertEqual(bm.false_acceptance_rate, 0.0)

    def test_05_latency_percentiles(self):
        """Verifies latency p50, p95, and throughput calculation."""
        latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        lm = MetricCalculator.compute_latency_metrics(latencies)
        self.assertAlmostEqual(lm.mean_latency_ms, 5.5)
        self.assertEqual(lm.p50_latency_ms, 6.0)
        self.assertEqual(lm.p95_latency_ms, 10.0)
        self.assertGreater(lm.throughput_units_per_second, 0)


class TestDeterministicLLMStub(unittest.TestCase):
    """Verifies that DeterministicLLMStub provides safe, reproducible mock behavior."""

    def setUp(self):
        self.stub = DeterministicLLMStub(simulated_delay_sec=0.0)

    def test_01_rejects_negative_noise(self):
        """Verifies stub correctly rejects MCQ and watermark noise."""
        mcq_noise = "(a) 24 hours (b) 48 hours"
        node = self.stub.extract(mcq_noise)
        self.assertIsNone(node, "LLM stub must reject MCQ leakage noise")

        wm_noise = "PARMAR SSC 2023"
        node_wm = self.stub.extract(wm_noise)
        self.assertIsNone(node_wm, "LLM stub must reject watermark noise")

    def test_02_extracts_canonical_definition(self):
        """Verifies stub extracts valid KnowledgeNode for standard educational sentence."""
        sentence = "The sun, the moon and all those objects shining in the night sky are called celestial bodies."
        node = self.stub.extract(sentence)
        self.assertIsNotNone(node, "LLM stub should successfully extract celestial bodies definition")
        self.assertEqual(node.intent_type, "definition")
        self.assertEqual(node.extraction_method, "gemini_structured_mock")


class TestExtractionAdapters(unittest.TestCase):
    """Verifies interface contract conformance across Approach A, B, and C."""

    def test_01_rule_based_adapter(self):
        adapter = RuleBasedAdapter()
        node = adapter.extract_single("The sun, the moon and all those objects shining in the night sky are called celestial bodies.")
        self.assertIsNotNone(node)
        self.assertEqual(node.intent_type, "definition")

    def test_02_structured_llm_adapter_offline(self):
        adapter = StructuredLLMAdapter(force_offline=True)
        node = adapter.extract_single("The sun, the moon and all those objects shining in the night sky are called celestial bodies.")
        self.assertIsNotNone(node)
        self.assertTrue(adapter.is_offline)

    def test_03_hybrid_pipeline_adapter(self):
        adapter = HybridPipelineAdapter(force_offline=True)
        # Fast path
        node_fast = adapter.extract_single("The sun, the moon and all those objects shining in the night sky are called celestial bodies.")
        self.assertIsNotNone(node_fast)
        self.assertIn("hybrid", node_fast.extraction_method)
        # Noise rejection
        node_noise = adapter.extract_single("Ans. (b) 5.51 g/cm^3")
        self.assertIsNone(node_noise)


class TestBenchmarkRunner(unittest.TestCase):
    """Verifies end-to-end benchmark execution on data/golden_eval_set.json."""

    def setUp(self):
        self.eval_path = os.path.abspath(os.path.join(REPO_ROOT, "data", "golden_eval_set.json"))
        self.test_output = os.path.abspath(os.path.join(REPO_ROOT, "data", "test_experiment_metrics.json"))
        self.runner = ExperimentBenchmarkRunner(
            eval_set_path=self.eval_path,
            output_metrics_path=self.test_output,
            force_offline=True
        )

    def tearDown(self):
        if os.path.exists(self.test_output):
            try:
                os.remove(self.test_output)
            except OSError:
                pass

    def test_01_full_benchmark_run(self):
        """Executes full benchmark and verifies output JSON structure and schema."""
        metrics = self.runner.run_benchmark()
        self.assertIn("metadata", metrics)
        self.assertIn("dataset_info", metrics)
        self.assertIn("approaches", metrics)
        self.assertIn("comparative_summary", metrics)

        # Check all 3 approaches present
        approaches = metrics["approaches"]
        self.assertIn("approach_a_rule_based", approaches)
        self.assertIn("approach_b_structured_llm", approaches)
        self.assertIn("approach_c_hybrid_pipeline", approaches)

        # Check production acceptance criteria for Approach C
        hybrid_summary = approaches["approach_c_hybrid_pipeline"]["summary_metrics"]
        self.assertGreaterEqual(hybrid_summary["precision"], 0.95, "Approach C precision must be >= 0.95")
        self.assertLessEqual(hybrid_summary["false_acceptance_rate"], 0.02, "Approach C FAR must be <= 0.02")
        self.assertGreaterEqual(hybrid_summary["recall"], 0.85, "Approach C recall must be >= 0.85")

        # Check ranking
        ranking = metrics["comparative_summary"]["ranking"]
        self.assertEqual(len(ranking), 3)
        self.assertEqual(ranking[0]["rank"], 1)


if __name__ == "__main__":
    unittest.main()
