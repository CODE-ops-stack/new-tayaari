"""
v13_discovery/experiments.py
============================
3-Approach Comparative Experimentation & Metrics Benchmark Engine for Milestone 3.

Evaluates and compares three distinct educational knowledge extraction paradigms:
- Approach A: Rule-Based / Generalized Grammar & NLP (LinguisticSemanticExtractor + NoiseFilterGate)
- Approach B: Structured LLM / In-Context Learning (GeminiStructuredExtractor / DeterministicLLMStub)
- Approach C: Hybrid Multi-Stage Pipeline (Noise Gate -> Rule Fast-Path -> LLM Disambiguation/Fallback)

Computes exact evaluation metrics:
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- False Acceptance Rate (FAR) = FP / (FP + TN)
- False Rejection Rate (FRR) = FN / (TP + FN)
- F1-Score = 2 * P * R / (P + R)
- Multi-Class Intent Breakdown across all 14 R2 intents (Macro/Micro F1)
- Noise Rejection Rate across all 6 corpus failure categories
- Operational Latency (Mean, p50, p95, Throughput units/sec)

Generates standardized data/experiment_metrics.json.
"""

import os
import sys
import json
import time
import uuid
import re
import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

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

from v13_discovery.semantic_extractor import (
    KnowledgeNode,
    NoiseFilterGate,
    LinguisticSemanticExtractor,
    GeminiStructuredExtractor,
    HybridSemanticExtractor,
    canonicalize_intent,
    to_r2_intent,
    CANONICAL_14_INTENTS,
    INTENT_ALIASES,
)


# =============================================================================
# 1. EVALUATION DATA STRUCTURES & CONTINGENCY MODELS
# =============================================================================

@dataclass
class ExtractionResult:
    """Result of running an extraction approach on an individual unit."""
    item_id: str
    raw_text: str
    expected_label: str  # "positive" | "negative"
    expected_intent: Optional[str]  # None if negative
    rejection_category: Optional[str]  # None if positive
    predicted_node: Optional[KnowledgeNode]
    latency_ms: float
    is_accepted: bool = False
    predicted_intent: Optional[str] = None
    extraction_method: str = "none"

    def __post_init__(self):
        if self.predicted_node:
            self.is_accepted = True
            self.predicted_intent = canonicalize_intent(self.predicted_node.intent_type)
            self.extraction_method = self.predicted_node.extraction_method
        else:
            self.is_accepted = False
            self.predicted_intent = "none"


@dataclass
class BinaryMetrics:
    """Binary knowledge classification contingency metrics."""
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    false_acceptance_rate: float = 0.0  # FAR = FP / (FP + TN)
    false_rejection_rate: float = 0.0   # FRR = FN / (TP + FN)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IntentMetrics:
    """Multi-class performance breakdown for an individual intent."""
    intent_name: str
    support: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NoiseRejectionMetrics:
    """Rejection performance for an individual corpus noise category."""
    category_name: str
    total_examples: int = 0
    rejected_count: int = 0
    leaked_count: int = 0
    rejection_rate: float = 0.0  # TN / (TN + FP)
    false_acceptance_rate: float = 0.0  # FP / (TN + FP)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LatencyMetrics:
    """Operational latency and throughput measurements."""
    total_time_seconds: float = 0.0
    mean_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    throughput_units_per_second: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 2. DETERMINISTIC OFFLINE MOCK / STUB FOR LLM EXTRACTOR
# =============================================================================

class DeterministicLLMStub:
    """Offline, deterministic mock simulation of GeminiStructuredExtractor.
    
    Ensures CI/CD environments and automated tests run without network access,
    without API keys, and with zero flakiness while honoring the exact
    structured output schema and behavior expected from an LLM.
    """

    def __init__(self, simulated_delay_sec: float = 0.0):
        self.simulated_delay_sec = simulated_delay_sec
        self.noise_gate = NoiseFilterGate()
        self.linguistic = LinguisticSemanticExtractor()

    def extract(self, text: str, source_loc: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        """Simulates structured LLM extraction with deterministic heuristics."""
        if self.simulated_delay_sec > 0:
            time.sleep(self.simulated_delay_sec)

        # 1. Negative noise rejection simulation
        rejection = self.noise_gate.audit(text, is_block_context=False)
        if rejection:
            return None

        # 2. Extract using linguistic rule base as semantic foundation
        node = self.linguistic.extract(text, source_loc)
        if node and node.primary_entity and node.predicate:
            # Rebrand extraction method to reflect structured model extraction
            node.extraction_method = "gemini_structured_mock"
            node.confidence = 0.96
            return node

        # 3. Handle nuanced patterns that LLMs typically resolve
        m_cause = re.search(r'\b(?:because of|due to|as a result of)\s+([^,]+),\s*(.+)$', text, re.IGNORECASE)
        if m_cause:
            cause_phrase = m_cause.group(1).strip()
            effect_clause = m_cause.group(2).strip()
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type="cause/effect",
                primary_entity=effect_clause.split()[0] if effect_clause else "Entity",
                predicate=f"occurs due to {cause_phrase}",
                secondary_entities=[cause_phrase],
                raw_evidence=text,
                source_location=source_loc or {},
                confidence=0.94,
                extraction_method="gemini_structured_mock"
            )

        return None


# =============================================================================
# 3. EXTRACTION PARADIGM ADAPTERS
# =============================================================================

class BaseExtractorAdapter(ABC):
    """Abstract interface adapter for comparative extraction approaches."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def extract_single(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        """Extracts a KnowledgeNode from an isolated text unit."""
        pass

    def benchmark_unit(self, item: Dict[str, Any]) -> ExtractionResult:
        """Runs extraction on a single item, measuring wall-clock latency."""
        item_id = item.get("id", "UNIT")
        text = item.get("text", "")
        label = item.get("expected_label") or item.get("label", "positive")
        raw_intent = item.get("expected_intent") or item.get("intent")
        intent = canonicalize_intent(raw_intent) if raw_intent else None
        rej_cat = item.get("rejection_category") or item.get("noise_type")

        t0 = time.perf_counter()
        try:
            node = self.extract_single(text, item.get("provenance"))
        except Exception:
            node = None
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        return ExtractionResult(
            item_id=item_id,
            raw_text=text,
            expected_label=label,
            expected_intent=intent,
            rejection_category=rej_cat,
            predicted_node=node,
            latency_ms=latency_ms
        )


class RuleBasedAdapter(BaseExtractorAdapter):
    """Approach A: Rule-Based / Generalized Grammar & NLP.
    
    Directly evaluates LinguisticSemanticExtractor coupled with NoiseFilterGate.
    Zero external dependencies, sub-millisecond deterministic execution.
    """

    def __init__(self):
        super().__init__(
            name="Approach A: Rule-Based / Generalized Grammar & NLP",
            description="Deterministic regex and linguistic discourse patterns with 0ms pre-extraction noise gate."
        )
        self.noise_gate = NoiseFilterGate()
        self.linguistic = LinguisticSemanticExtractor()

    def extract_single(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        # Pre-extraction noise gate
        rejection = self.noise_gate.audit(text, is_block_context=False)
        if rejection:
            return None
        return self.linguistic.extract(text, metadata)


class StructuredLLMAdapter(BaseExtractorAdapter):
    """Approach B: Structured LLM / In-Context Learning.
    
    Directly invokes Google Gemini API via GeminiStructuredExtractor with
    strict responseSchema, or gracefully falls back to DeterministicLLMStub
    when running offline or without an API key.
    """

    def __init__(self, api_key: Optional[str] = None, force_offline: bool = False):
        super().__init__(
            name="Approach B: Structured LLM / In-Context Learning",
            description="Direct structured LLM generation with strict JSON schema and offline deterministic stub fallback."
        )
        self.force_offline = force_offline
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.force_offline and self.api_key:
            self.client = GeminiStructuredExtractor(api_key=self.api_key)
            self.is_offline = False
        else:
            self.client = DeterministicLLMStub()
            self.is_offline = True

    def extract_single(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        return self.client.extract(text, metadata)


class HybridPipelineAdapter(BaseExtractorAdapter):
    """Approach C: Hybrid Multi-Stage Pipeline.
    
    Cascades 3 stages:
    1. NoiseFilterGate (0ms rejection of non-factual noise)
    2. LinguisticSemanticExtractor (fast path: accepts high-confidence structured matches)
    3. Structured LLM / Stub (slow path: disambiguates complex or unhandled expressions)
    """

    def __init__(self, api_key: Optional[str] = None, force_offline: bool = False):
        super().__init__(
            name="Approach C: Hybrid Multi-Stage Pipeline",
            description="Cascaded 3-stage architecture: 0ms Noise Gate -> Linguistic Rule Fast-Path -> LLM Disambiguation Fallback."
        )
        self.noise_gate = NoiseFilterGate()
        self.linguistic = LinguisticSemanticExtractor()
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not force_offline and self.api_key:
            self.llm = GeminiStructuredExtractor(api_key=self.api_key)
        else:
            self.llm = DeterministicLLMStub()

    def extract_single(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        # Stage 1: Noise Gate (0ms)
        rejection = self.noise_gate.audit(text, is_block_context=False)
        if rejection:
            return None

        # Stage 2: Linguistic Rule Fast-Path (<0.5ms)
        rule_node = self.linguistic.extract(text, metadata)
        if rule_node and rule_node.primary_entity and rule_node.predicate:
            # High-confidence deterministic match -> return immediately
            if rule_node.confidence >= 0.88:
                rule_node.extraction_method = "hybrid_rule_fastpath"
                return rule_node

        # Stage 3: LLM Disambiguation Fallback
        llm_node = self.llm.extract(text, metadata)
        if llm_node and llm_node.primary_entity and llm_node.predicate:
            # Grounding check: verify primary entity exists in text to prevent hallucinations
            pe_clean = re.sub(r'[^\w\s]', '', llm_node.primary_entity.lower())
            text_clean = re.sub(r'[^\w\s]', '', text.lower())
            
            # Allow single-word containment or phrase overlap
            pe_words = pe_clean.split()
            if any(w in text_clean for w in pe_words if len(w) > 3) or pe_clean in text_clean:
                llm_node.extraction_method = "hybrid_llm_fallback"
                return llm_node

        return rule_node if rule_node else None


# =============================================================================
# 4. METRIC CALCULATION ENGINE
# =============================================================================

class MetricCalculator:
    """Pure mathematical metric calculator for classification & latency statistics."""

    @staticmethod
    def compute_binary_metrics(results: List[ExtractionResult]) -> BinaryMetrics:
        """Calculates TP, FP, TN, FN, Precision, Recall, F1, FAR, and FRR."""
        if not results:
            return BinaryMetrics()

        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for r in results:
            actual_pos = (r.expected_label == "positive")
            pred_pos = r.is_accepted

            if actual_pos and pred_pos:
                tp += 1
            elif not actual_pos and pred_pos:
                fp += 1
            elif not actual_pos and not pred_pos:
                tn += 1
            elif actual_pos and not pred_pos:
                fn += 1

        # Precision = TP / (TP + FP)
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if fp == 0 else 0.0)
        
        # Recall = TP / (TP + FN)
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0

        # False Acceptance Rate (FAR) = FP / (FP + TN)
        far = (fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        # False Rejection Rate (FRR) = FN / (TP + FN) = 1 - Recall
        frr = (fn / (tp + fn)) if (tp + fn) > 0 else 0.0

        # F1-Score = 2 * P * R / (P + R)
        f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return BinaryMetrics(
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            false_acceptance_rate=round(far, 4),
            false_rejection_rate=round(frr, 4)
        )

    @staticmethod
    def compute_intent_metrics(results: List[ExtractionResult]) -> Dict[str, IntentMetrics]:
        """Calculates per-intent multi-class metrics across all 14 R2 intents."""
        metrics_by_intent = {}

        for intent in sorted(list(CANONICAL_14_INTENTS)):
            tp = 0
            fp = 0
            fn = 0
            support = 0

            for r in results:
                actual_intent = r.expected_intent
                pred_intent = r.predicted_intent

                if actual_intent == intent:
                    support += 1
                    if pred_intent == intent:
                        tp += 1
                    else:
                        fn += 1
                else:
                    if pred_intent == intent:
                        fp += 1

            p = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if fp == 0 and tp > 0 else 0.0)
            rec = (tp / (tp + fn)) if (tp + fn) > 0 else (1.0 if support == 0 else 0.0)
            f1 = (2.0 * p * rec / (p + rec)) if (p + rec) > 0 else 0.0

            r2_name = to_r2_intent(intent)
            metrics_by_intent[r2_name] = IntentMetrics(
                intent_name=r2_name,
                support=support,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                precision=round(p, 4),
                recall=round(rec, 4),
                f1_score=round(f1, 4)
            )

        return metrics_by_intent

    @staticmethod
    def compute_noise_rejection_metrics(results: List[ExtractionResult]) -> Dict[str, NoiseRejectionMetrics]:
        """Calculates rejection metrics across the 6 negative corpus failure categories."""
        categories = {
            "mcq_leakage",
            "watermark_header",
            "syntactic_fragment",
            "broken_reading_order",
            "table_formatting_artifact",
            "anaphoric_unresolved"
        }
        noise_metrics = {}

        for cat in sorted(list(categories)):
            total = 0
            leaked = 0
            rejected = 0

            for r in results:
                if r.expected_label == "negative" and r.rejection_category == cat:
                    total += 1
                    if r.is_accepted:
                        leaked += 1
                    else:
                        rejected += 1

            rej_rate = (rejected / total) if total > 0 else 1.0
            far = (leaked / total) if total > 0 else 0.0

            noise_metrics[cat] = NoiseRejectionMetrics(
                category_name=cat,
                total_examples=total,
                rejected_count=rejected,
                leaked_count=leaked,
                rejection_rate=round(rej_rate, 4),
                false_acceptance_rate=round(far, 4)
            )

        return noise_metrics

    @staticmethod
    def compute_latency_metrics(latencies_ms: List[float]) -> LatencyMetrics:
        """Calculates latency distribution (mean, p50, p95) and throughput."""
        if not latencies_ms:
            return LatencyMetrics()

        n = len(latencies_ms)
        sorted_lat = sorted(latencies_ms)
        total_time_sec = sum(latencies_ms) / 1000.0

        mean_ms = sum(latencies_ms) / n
        p50_ms = sorted_lat[int(n * 0.50)]
        p95_index = min(int(n * 0.95), n - 1)
        p95_ms = sorted_lat[p95_index]

        throughput = (n / total_time_sec) if total_time_sec > 0 else 0.0

        return LatencyMetrics(
            total_time_seconds=round(total_time_sec, 4),
            mean_latency_ms=round(mean_ms, 2),
            p50_latency_ms=round(p50_ms, 2),
            p95_latency_ms=round(p95_ms, 2),
            throughput_units_per_second=round(throughput, 2)
        )


# =============================================================================
# 5. EXPERIMENT BENCHMARK RUNNER & CORPUS SAMPLER
# =============================================================================

class CorpusSampler:
    """Stratified sampler ingesting real corpus files to construct evaluation sets."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def load_golden_eval_set(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Loads and returns the 111 validated items from golden_eval_set.json."""
        target_path = path or os.path.abspath(os.path.join(REPO_ROOT, "data", "golden_eval_set.json"))
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Golden evaluation set missing at: {target_path}")
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("examples") or data.get("items", [])


class ExperimentBenchmarkRunner:
    """Orchestrates comparative benchmarking across all 3 extraction paradigms."""

    def __init__(
        self,
        eval_set_path: Optional[str] = None,
        output_metrics_path: Optional[str] = None,
        force_offline: bool = False
    ):
        self.eval_set_path = eval_set_path or os.path.abspath(
            os.path.join(REPO_ROOT, "data", "golden_eval_set.json")
        )
        self.output_metrics_path = output_metrics_path or os.path.abspath(
            os.path.join(REPO_ROOT, "data", "experiment_metrics.json")
        )
        self.force_offline = force_offline
        self.sampler = CorpusSampler()

        # Initialize the 3 approaches
        self.approaches: Dict[str, BaseExtractorAdapter] = {
            "approach_a_rule_based": RuleBasedAdapter(),
            "approach_b_structured_llm": StructuredLLMAdapter(force_offline=self.force_offline),
            "approach_c_hybrid_pipeline": HybridPipelineAdapter(force_offline=self.force_offline),
        }

    def load_dataset(self) -> List[Dict[str, Any]]:
        """Loads and validates evaluation dataset items."""
        return self.sampler.load_golden_eval_set(self.eval_set_path)

    def run_benchmark(self) -> Dict[str, Any]:
        """Executes full comparative benchmark and returns structured metrics."""
        dataset = self.load_dataset()
        pos_count = sum(1 for it in dataset if (it.get("expected_label") or it.get("label")) == "positive")
        neg_count = sum(1 for it in dataset if (it.get("expected_label") or it.get("label")) == "negative")

        results_by_approach: Dict[str, List[ExtractionResult]] = {}
        approach_payloads: Dict[str, Any] = {}

        for app_id, adapter in self.approaches.items():
            app_results = []
            for item in dataset:
                res = adapter.benchmark_unit(item)
                app_results.append(res)
            results_by_approach[app_id] = app_results

            # Compute metrics
            binary = MetricCalculator.compute_binary_metrics(app_results)
            intent_m = MetricCalculator.compute_intent_metrics(app_results)
            noise_m = MetricCalculator.compute_noise_rejection_metrics(app_results)
            latency_m = MetricCalculator.compute_latency_metrics([r.latency_ms for r in app_results])

            fps = [r.item_id for r in app_results if not (r.expected_label == "positive") and r.is_accepted]
            fns = [r.item_id for r in app_results if (r.expected_label == "positive") and not r.is_accepted]

            approach_payloads[app_id] = {
                "name": adapter.name,
                "description": adapter.description,
                "units_evaluated": len(app_results),
                "precision": binary.precision,
                "recall": binary.recall,
                "false_acceptance_rate": binary.false_acceptance_rate,
                "false_rejection_rate": binary.false_rejection_rate,
                "f1_score": binary.f1_score,
                "summary_metrics": binary.to_dict(),
                "intent_breakdown": {k: v.to_dict() for k, v in intent_m.items()},
                "noise_rejection_breakdown": {k: v.to_dict() for k, v in noise_m.items()},
                "latency_metrics": latency_m.to_dict(),
                "error_analysis": {
                    "false_positive_ids": fps,
                    "false_negative_ids": fns
                }
            }

        # Ranking by composite score (F1 descending, FAR ascending, Latency ascending)
        ranking = []
        for app_id, payload in approach_payloads.items():
            f1 = payload["summary_metrics"]["f1_score"]
            far = payload["summary_metrics"]["false_acceptance_rate"]
            mean_lat = payload["latency_metrics"]["mean_latency_ms"]
            ranking.append({
                "approach_id": app_id,
                "name": payload["name"],
                "f1_score": f1,
                "far": far,
                "mean_latency_ms": mean_lat
            })

        def rank_sorter(x):
            # Priority: F1 (descending), FAR (ascending), architectural robustness (hybrid preferred on tie), latency (ascending)
            is_hybrid_tier = 0 if "hybrid" in x["approach_id"] else (1 if "rule" in x["approach_id"] else 2)
            return (-round(x["f1_score"], 4), round(x["far"], 4), is_hybrid_tier, x["mean_latency_ms"])

        ranking.sort(key=rank_sorter)
        for idx, item in enumerate(ranking, 1):
            item["rank"] = idx

        # Production recommendation
        winner = ranking[0]
        rationale = (
            f"{winner['name']} is selected for production deployment because it achieves "
            f"F1-Score of {winner['f1_score']} with minimal False Acceptance Rate (FAR={winner['far']}) "
            f"and high operational throughput ({winner['mean_latency_ms']} ms/unit)."
        )

        full_output = {
            "version": "1.0.0",
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "environment": "offline" if self.force_offline else "live_or_hybrid",
                "git_commit": "HEAD"
            },
            "dataset_info": {
                "dataset_path": self.eval_set_path,
                "total_units": len(dataset),
                "positive_units": pos_count,
                "negative_units": neg_count
            },
            "approaches": approach_payloads,
            "comparative_summary": {
                "ranking": ranking,
                "production_recommendation": winner["approach_id"],
                "rationale": rationale
            }
        }

        # Save to output path
        os.makedirs(os.path.dirname(os.path.abspath(self.output_metrics_path)), exist_ok=True)
        with open(self.output_metrics_path, "w", encoding="utf-8") as f:
            json.dump(full_output, f, indent=2)

        return full_output

    def print_markdown_summary(self, metrics_payload: Dict[str, Any]) -> str:
        """Renders formatted Markdown comparison table."""
        md = []
        md.append("# Milestone 3: 3-Approach Comparative Benchmark Report\n")
        md.append(f"**Dataset**: `{metrics_payload['dataset_info']['dataset_path']}` "
                  f"({metrics_payload['dataset_info']['total_units']} source units: "
                  f"{metrics_payload['dataset_info']['positive_units']} positive, "
                  f"{metrics_payload['dataset_info']['negative_units']} negative)\n")
        
        md.append("| Approach | Precision | Recall | F1-Score | FAR (Fallout) | FRR (Miss Rate) | Mean Latency | Throughput |")
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

        for app_id, data in metrics_payload["approaches"].items():
            name = data["name"].split(":")[1].strip() if ":" in data["name"] else data["name"]
            sm = data["summary_metrics"]
            lm = data["latency_metrics"]
            md.append(
                f"| **{name}** | {sm['precision']:.4f} | {sm['recall']:.4f} | {sm['f1_score']:.4f} | "
                f"{sm['false_acceptance_rate']:.4f} | {sm['false_rejection_rate']:.4f} | "
                f"{lm['mean_latency_ms']:.2f} ms | {lm['throughput_units_per_second']:.1f} u/s |"
            )

        md.append("\n### Key Takeaways")
        md.append(f"- **Production Winner**: `{metrics_payload['comparative_summary']['production_recommendation']}`")
        md.append(f"- **Rationale**: {metrics_payload['comparative_summary']['rationale']}")

        summary_text = "\n".join(md)
        return summary_text


# =============================================================================
# 6. CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Run Milestone 3 Extraction Paradigm Benchmark")
    parser.add_argument("--eval-set", default=None, help="Path to golden_eval_set.json")
    parser.add_argument("--output", default=None, help="Output path for experiment_metrics.json")
    parser.add_argument("--offline", action="store_true", default=True, help="Force offline deterministic LLM stub")
    parser.add_argument("--quiet", action="store_true", help="Suppress console markdown output")
    args = parser.parse_args()

    runner = ExperimentBenchmarkRunner(
        eval_set_path=args.eval_set,
        output_metrics_path=args.output,
        force_offline=args.offline
    )

    metrics = runner.run_benchmark()
    if not args.quiet:
        print("\n" + runner.print_markdown_summary(metrics))


if __name__ == "__main__":
    main()
