#!/usr/bin/env python3
"""
proposed_metrics_evaluator.py
=============================
Metrics Evaluation Engine for Milestones M2 and M3.

Consumes the Golden Evaluation Set (data/golden_eval_set.json) and extractor predictions
to compute:
- Precision
- Recall
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- F1-Score & Balanced Accuracy
- 14-Intent Multi-Class Accuracy & Confusion Breakdown
- Category-Specific FAR (Noise Leakage Breakdown)
- 6-Link Unbreakable Provenance Verification
"""

import os
import math
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import Counter, defaultdict

CANONICAL_14_INTENTS = [
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
]


class BenchmarkMetricsResult:
    def __init__(self):
        # Binary Discovery Confusion Matrix
        self.tp: int = 0  # Ground Truth Pos, System Accepted
        self.fn: int = 0  # Ground Truth Pos, System Rejected (Lost Knowledge)
        self.fp: int = 0  # Ground Truth Neg, System Accepted (Noise Leakage)
        self.tn: int = 0  # Ground Truth Neg, System Rejected (Noise Filtered)

        # Intent Classification on TP
        self.intent_correct: int = 0
        self.intent_total_evaluated: int = 0
        self.per_intent_tp: Counter = Counter()
        self.per_intent_actual: Counter = Counter()
        self.per_intent_predicted: Counter = Counter()

        # Noise Category Leakage (FP breakdown)
        self.noise_category_totals: Counter = Counter()
        self.noise_category_leaked_fp: Counter = Counter()

        # Item-level breakdown logs
        self.false_acceptance_items: List[Dict[str, Any]] = []
        self.false_rejection_items: List[Dict[str, Any]] = []

    @property
    def total_positives(self) -> int:
        return self.tp + self.fn

    @property
    def total_negatives(self) -> int:
        return self.fp + self.tn

    @property
    def total_items(self) -> int:
        return self.total_positives + self.total_negatives

    @property
    def precision(self) -> float:
        total_accepted = self.tp + self.fp
        return (self.tp / total_accepted) if total_accepted > 0 else 1.0

    @property
    def recall(self) -> float:
        return (self.tp / self.total_positives) if self.total_positives > 0 else 0.0

    @property
    def false_acceptance_rate(self) -> float:
        """FAR = FP / (FP + TN) = FP / total_negatives"""
        return (self.fp / self.total_negatives) if self.total_negatives > 0 else 0.0

    @property
    def false_rejection_rate(self) -> float:
        """FRR = FN / (TP + FN) = FN / total_positives = 1 - Recall"""
        return (self.fn / self.total_positives) if self.total_positives > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p = self.precision
        r = self.recall
        return (2 * p * r / (p + r)) if (p + r) > 0 else 0.0

    @property
    def balanced_accuracy(self) -> float:
        tpr = self.recall
        tnr = 1.0 - self.false_acceptance_rate
        return (tpr + tnr) / 2.0

    @property
    def intent_accuracy(self) -> float:
        return (self.intent_correct / self.intent_total_evaluated) if self.intent_total_evaluated > 0 else 0.0

    def get_category_far(self, category: str) -> float:
        tot = self.noise_category_totals.get(category, 0)
        leaked = self.noise_category_leaked_fp.get(category, 0)
        return (leaked / tot) if tot > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        per_intent_metrics = {}
        for intent in CANONICAL_14_INTENTS:
            actual = self.per_intent_actual.get(intent, 0)
            pred = self.per_intent_predicted.get(intent, 0)
            tp_int = self.per_intent_tp.get(intent, 0)
            p_int = (tp_int / pred) if pred > 0 else 0.0
            r_int = (tp_int / actual) if actual > 0 else 0.0
            f1_int = (2 * p_int * r_int / (p_int + r_int)) if (p_int + r_int) > 0 else 0.0
            per_intent_metrics[intent] = {
                "ground_truth_count": actual,
                "predicted_count": pred,
                "true_positives": tp_int,
                "precision": round(p_int, 4),
                "recall": round(r_int, 4),
                "f1_score": round(f1_int, 4)
            }

        category_far_breakdown = {}
        for cat, tot in self.noise_category_totals.items():
            leaked = self.noise_category_leaked_fp.get(cat, 0)
            category_far_breakdown[cat] = {
                "total_negative_samples": tot,
                "false_accepted_leaks": leaked,
                "category_far": round((leaked / tot) if tot > 0 else 0.0, 4)
            }

        return {
            "summary": {
                "total_items_evaluated": self.total_items,
                "true_positives": self.tp,
                "false_negatives": self.fn,
                "false_positives": self.fp,
                "true_negatives": self.tn,
                "precision": round(self.precision, 4),
                "recall": round(self.recall, 4),
                "false_acceptance_rate_far": round(self.false_acceptance_rate, 4),
                "false_rejection_rate_frr": round(self.false_rejection_rate, 4),
                "f1_score": round(self.f1_score, 4),
                "balanced_accuracy": round(self.balanced_accuracy, 4),
                "intent_accuracy": round(self.intent_accuracy, 4)
            },
            "per_intent_metrics": per_intent_metrics,
            "category_far_breakdown": category_far_breakdown,
            "false_acceptances_sample": self.false_acceptance_items[:10],
            "false_rejections_sample": self.false_rejection_items[:10]
        }


def evaluate_extractor(
    golden_eval_items: List[Dict[str, Any]],
    extractor_func
) -> BenchmarkMetricsResult:
    """
    Evaluates an extractor function on golden evaluation items.
    
    extractor_func(item_text) must return a dict:
    {
        "verdict": "ACCEPT" | "REJECT",
        "predicted_intent": str | None,
        "extracted_nodes": list | None,
        "rejection_reason": str | None
    }
    """
    res = BenchmarkMetricsResult()

    for item in golden_eval_items:
        label = item.get("expected_label") or item.get("label")
        text = item.get("text", "")
        item_id = item.get("id", "UNKNOWN")

        pred = extractor_func(text)
        verdict = pred.get("verdict", "REJECT").upper()
        pred_intent = pred.get("predicted_intent")

        if label == "positive":
            exp_intent = item.get("expected_intent", "").strip().lower().replace("/", "_").replace("-", "_")
            res.per_intent_actual[exp_intent] += 1

            if verdict == "ACCEPT":
                res.tp += 1
                if pred_intent:
                    norm_pred = pred_intent.strip().lower().replace("/", "_").replace("-", "_")
                    res.per_intent_predicted[norm_pred] += 1
                    res.intent_total_evaluated += 1
                    if norm_pred == exp_intent:
                        res.intent_correct += 1
                        res.per_intent_tp[exp_intent] += 1
            else:
                res.fn += 1
                res.false_rejection_items.append({
                    "id": item_id,
                    "text": text[:80],
                    "expected_intent": exp_intent,
                    "rejection_reason": pred.get("rejection_reason")
                })

        elif label == "negative":
            noise_type = item.get("noise_type") or item.get("category", "unknown")
            res.noise_category_totals[noise_type] += 1

            if verdict == "ACCEPT":
                res.fp += 1
                res.noise_category_leaked_fp[noise_type] += 1
                res.false_acceptance_items.append({
                    "id": item_id,
                    "text": text[:80],
                    "noise_type": noise_type,
                    "extracted_nodes": pred.get("extracted_nodes")
                })
            else:
                res.tn += 1

    return res


def verify_unbreakable_provenance(
    question_obj: Dict[str, Any],
    workspace_root: str = "."
) -> Tuple[bool, List[str]]:
    """
    Verifies the 6-link unbreakable provenance chain required by R5:
    Question -> Intent -> Knowledge Unit -> Evidence -> Source -> Location
    """
    errors = []
    prov = question_obj.get("provenance", {})

    # Link 1: Question -> Intent
    intent = prov.get("intent") or question_obj.get("intentType")
    if not intent:
        errors.append("Provenance Link 1 Broken: Missing 'intent' in question metadata.")

    # Link 2: Intent -> Knowledge Unit
    node_id = prov.get("knowledge_unit_id") or prov.get("nodeId")
    if not node_id:
        errors.append("Provenance Link 2 Broken: Missing 'knowledge_unit_id'.")

    # Link 3: Knowledge Unit -> Evidence
    evidence = prov.get("evidence") or prov.get("rawEvidence")
    if not evidence or not isinstance(evidence, str) or len(evidence.strip()) < 10:
        errors.append("Provenance Link 3 Broken: Missing or trivial 'evidence' excerpt.")

    # Link 4: Evidence -> Source File
    source_file = prov.get("source_file") or prov.get("sourceId")
    if not source_file:
        errors.append("Provenance Link 4 Broken: Missing 'source_file'.")

    # Link 5: Source File -> Location
    location = prov.get("location") or prov.get("line_or_page")
    if not location:
        errors.append("Provenance Link 5 Broken: Missing 'location' (page/line).")

    # Link 6: Location Verification (Existence on disk)
    if source_file and workspace_root:
        full_path = source_file if os.path.isabs(source_file) else os.path.join(workspace_root, source_file)
        if not os.path.exists(full_path):
            errors.append(f"Provenance Link 6 Broken: Source file does not exist at '{full_path}'.")

    return (len(errors) == 0), errors
