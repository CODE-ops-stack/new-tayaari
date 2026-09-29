#!/usr/bin/env python3
"""
test_harness_self_verification.py
=================================
Self-verification script to test proposed_validate_eval_set.py and proposed_metrics_evaluator.py.
"""

import os
import sys
import json
from proposed_validate_eval_set import validate_golden_eval_data, CANONICAL_14_INTENTS, MANDATORY_NEGATIVE_CATEGORIES
from proposed_metrics_evaluator import evaluate_extractor, verify_unbreakable_provenance

def build_mock_dataset(include_all_intents=True, include_all_noise=True, count_pos=52, count_neg=52, duplicate_id=False, missing_provenance=False):
    intents = sorted(list(CANONICAL_14_INTENTS))
    items = []
    
    # Generate Positives
    for i in range(count_pos):
        intent = intents[i % len(intents)] if include_all_intents else "definition"
        item_id = "pos_001" if (duplicate_id and i > 0) else f"pos_{i+1:03d}"
        source_file = "source-material/geography_extracted.txt" if not missing_provenance else ""
        items.append({
            "id": item_id,
            "expected_label": "positive",
            "text": f"Geographical entity #{i+1} is defined by characteristics and processes in physical geography.",
            "source": {
                "file": source_file,
                "line_or_page": f"line {100 + i}",
                "context": f"Section on Physical Geography {i}"
            },
            "expected_intent": intent,
            "extracted_entities": [f"Entity_{i+1}", "Physical Geography"],
            "expected_truth_claim": f"Entity_{i+1} undergoes physical processes."
        })
        
    # Generate Negatives
    noise_types = sorted(list(MANDATORY_NEGATIVE_CATEGORIES))
    for i in range(count_neg):
        noise = noise_types[i % len(noise_types)] if include_all_noise else "mcq_noise"
        item_id = f"neg_{i+1:03d}"
        items.append({
            "id": item_id,
            "expected_label": "negative",
            "text": f"(c) Option fragment {i+1} with watermark www.ssccglpinnacle.com and trailing...",
            "source": {
                "file": "source-material/question_extracted.txt",
                "line_or_page": f"page {10 + i}",
                "context": f"Question paper fragment {i}"
            },
            "noise_type": noise,
            "expected_rejection_reason": f"Contains {noise} and cannot form a valid question stem."
        })
        
    return {"version": "1.0", "items": items}

def run_self_verification():
    print("=== TEST 1: Valid Dataset (104 items, all 14 intents, all 4 noise types) ===")
    valid_data = build_mock_dataset(count_pos=52, count_neg=52)
    report = validate_golden_eval_data(valid_data)
    assert report.passed, f"Expected valid dataset to pass, but failed with: {report.errors}"
    assert report.stats["positive_count"] == 52
    assert report.stats["negative_count"] == 52
    assert len(report.stats["intent_distribution"]) == 14
    print("  -> Passed perfectly!")

    print("=== TEST 2: Under-count Dataset (40 pos, 40 neg = 80 total) ===")
    small_data = build_mock_dataset(count_pos=40, count_neg=40)
    report = validate_golden_eval_data(small_data)
    assert not report.passed
    assert any("Count constraint failed: Total items = 80" in e for e in report.errors)
    print("  -> Correctly flagged count constraint failures!")

    print("=== TEST 3: Missing Intents Dataset (only 'definition') ===")
    no_intents_data = build_mock_dataset(include_all_intents=False, count_pos=50, count_neg=50)
    report = validate_golden_eval_data(no_intents_data)
    assert not report.passed
    assert any("Missing 13 semantic intents" in e for e in report.errors)
    print("  -> Correctly flagged missing semantic intents!")

    print("=== TEST 4: Missing Mandatory Noise Dataset ===")
    no_noise_data = build_mock_dataset(include_all_noise=False, count_pos=50, count_neg=50)
    report = validate_golden_eval_data(no_noise_data)
    assert not report.passed
    assert any("Missing mandatory noise categories" in e for e in report.errors)
    print("  -> Correctly flagged missing mandatory noise categories!")

    print("=== TEST 5: Duplicate IDs Dataset ===")
    dup_id_data = build_mock_dataset(duplicate_id=True, count_pos=50, count_neg=50)
    report = validate_golden_eval_data(dup_id_data)
    assert not report.passed
    assert any("Duplicate IDs detected" in e for e in report.errors)
    print("  -> Correctly flagged duplicate IDs!")

    print("=== TEST 6: Missing Provenance Dataset ===")
    miss_prov_data = build_mock_dataset(missing_provenance=True, count_pos=50, count_neg=50)
    report = validate_golden_eval_data(miss_prov_data)
    assert not report.passed
    assert any("'source.file' is trivial or empty" in e for e in report.errors)
    print("  -> Correctly flagged missing provenance!")

    print("=== TEST 7: Metrics Evaluator (P/R/FAR/FRR) on Mock Extractor ===")
    def mock_v12_extractor(text):
        # Brittle extractor: accepts only if text contains "is defined by"
        if "is defined by" in text:
            return {"verdict": "ACCEPT", "predicted_intent": "definition"}
        return {"verdict": "REJECT", "rejection_reason": "No regex match"}

    res = evaluate_extractor(valid_data["items"], mock_v12_extractor)
    metrics = res.to_dict()
    print(f"  Mock Extractor Precision: {metrics['summary']['precision']}")
    print(f"  Mock Extractor Recall:    {metrics['summary']['recall']}")
    print(f"  Mock Extractor FAR:       {metrics['summary']['false_acceptance_rate_far']}")
    print(f"  Mock Extractor FRR:       {metrics['summary']['false_rejection_rate_frr']}")
    assert metrics["summary"]["precision"] == 1.0  # zero noise accepted
    assert metrics["summary"]["false_acceptance_rate_far"] == 0.0
    print("  -> Metrics computed successfully!")

    print("=== TEST 8: 6-Link Provenance Verification ===")
    valid_q = {
        "provenance": {
            "intent": "definition",
            "knowledge_unit_id": "ku_101",
            "evidence": "The Chota Nagpur plateau comprises immense reserves.",
            "source_file": "source-material/consolidated_grounding.md",
            "location": "line 15"
        }
    }
    repo_root = "c:/Users/harsh/Downloads/tayaari/tayaariapp"
    ok, errs = verify_unbreakable_provenance(valid_q, workspace_root=repo_root)
    assert ok, f"Expected valid question provenance to pass: {errs}"
    print("  -> Provenance verified successfully!")

    print("\nALL 8 SELF-VERIFICATION CHECKS PASSED [OK]")

if __name__ == "__main__":
    run_self_verification()
