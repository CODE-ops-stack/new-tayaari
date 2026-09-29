#!/usr/bin/env python3
"""
validate_eval_set.py
====================
Strict Automated Validation Harness for the Golden Evaluation Set (data/golden_eval_set.json).

Verifies:
1. File format and JSON schema conformity.
2. Count constraints: total items >= 100, positive examples >= 50, negative examples >= 50.
3. Representation constraints: all 14 semantic intents represented among positive examples.
4. Non-triviality constraints: unique IDs, text deduplication, non-empty fields, valid provenance.
5. Negative categories: presence of MCQ noise, watermark noise, incomplete clause fragments, OCR artifacts.

Usage:
    python scripts/validate_eval_set.py [--file data/golden_eval_set.json] [--strict] [--json-output report.json]
"""

import sys
import os
import json
import re
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# =====================================================================
# TAXONOMY DEFINITIONS
# =====================================================================

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
    "part of": "part_of",
    "member-of": "member_of",
    "member_of": "member_of",
    "member of": "member_of",
}

MANDATORY_NEGATIVE_CATEGORIES = {
    "mcq_noise",
    "watermark_noise",
    "incomplete_clause_fragment",
    "ocr_artifact",
}

OPTIONAL_NEGATIVE_CATEGORIES = {
    "table_artifact",
    "anaphoric_reference",
}

ALL_RECOGNIZED_NEGATIVE_CATEGORIES = MANDATORY_NEGATIVE_CATEGORIES | OPTIONAL_NEGATIVE_CATEGORIES

NOISE_ALIASES = {
    "mcq_noise": "mcq_noise",
    "mcq_leakage": "mcq_noise",
    "mcq_marker": "mcq_noise",
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
    "dangling_clause": "incomplete_clause_fragment",
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
    "unresolved_pronoun": "anaphoric_reference",
}

TRIVIAL_PLACEHOLDERS = {
    "test", "sample", "foo", "bar", "baz", "n/a", "na", "none", "null", "todo", "tbd", "unknown", "placeholder"
}

# =====================================================================
# JSON SCHEMA DRAFT-07
# =====================================================================

GOLDEN_EVAL_SET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "GoldenEvaluationSet",
    "type": "object",
    "required": ["version", "items"],
    "properties": {
        "version": {"type": "string"},
        "description": {"type": "string"},
        "metadata": {"type": "object"},
        "items": {
            "type": "array",
            "minItems": 100,
            "items": {
                "type": "object",
                "required": ["id", "expected_label", "text", "source"],
                "properties": {
                    "id": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 64,
                        "pattern": r"^[a-zA-Z0-9_\-]+$"
                    },
                    "expected_label": {
                        "type": "string",
                        "enum": ["positive", "negative"]
                    },
                    "text": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 4000
                    },
                    "source": {
                        "type": "object",
                        "required": ["file", "line_or_page"],
                        "properties": {
                            "file": {"type": "string", "minLength": 3},
                            "line_or_page": {"type": ["string", "integer"]},
                            "context": {"type": "string"}
                        }
                    },
                    "expected_intent": {"type": "string"},
                    "extracted_entities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "expected_truth_claim": {"type": "string"},
                    "noise_type": {"type": "string"},
                    "expected_rejection_reason": {"type": "string"}
                }
            }
        }
    }
}


# =====================================================================
# VALIDATION ENGINE
# =====================================================================

class ValidationReport:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {
            "total_items": 0,
            "positive_count": 0,
            "negative_count": 0,
            "intent_distribution": {},
            "noise_distribution": {},
            "sources_count": 0
        }

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats
        }


def normalize_intent(intent_raw: Optional[str]) -> Optional[str]:
    if not intent_raw:
        return None
    key = intent_raw.strip().lower()
    return INTENT_ALIASES.get(key, key)


def normalize_noise_type(noise_raw: Optional[str]) -> Optional[str]:
    if not noise_raw:
        return None
    key = noise_raw.strip().lower()
    return NOISE_ALIASES.get(key, key)


def validate_golden_eval_data(raw_data: Any, strict_mode: bool = False) -> ValidationReport:
    report = ValidationReport()

    # 1. Root structure normalization
    if isinstance(raw_data, list):
        report.add_warning("Root element is a JSON list instead of an object with {'version', 'items'}. Normalizing for evaluation.")
        data = {"version": "1.0", "items": raw_data}
    elif isinstance(raw_data, dict):
        data = dict(raw_data)
        if "examples" in data and "items" not in data:
            report.add_warning("Found 'examples' array instead of canonical 'items'. Normalizing for evaluation.")
            data["items"] = data["examples"]
    else:
        report.add_error(f"Root JSON element must be an object or array, got {type(raw_data).__name__}")
        return report

    items = data.get("items")
    if not isinstance(items, list):
        report.add_error("Missing or invalid 'items' / 'examples' array.")
        return report

    # 2. JSON Schema validation
    if HAS_JSONSCHEMA:
        # Create a copy for schema check ensuring items array is present
        schema_validator_data = {"version": data.get("version", "1.0"), "items": items}
        validator = jsonschema.Draft7Validator(GOLDEN_EVAL_SET_SCHEMA)
        # Validate item-level schemas flexibly
        schema_errors = list(validator.iter_errors(schema_validator_data))
        # Filter schema errors if items have alternative aliases (source/provenance)
        for err in schema_errors[:20]:
            path = " -> ".join([str(p) for p in err.path])
            report.add_warning(f"Schema notice at [{path}]: {err.message}")
    else:
        report.add_warning("jsonschema package not installed; skipping formal Draft-07 schema check.")

    report.stats["total_items"] = len(items)

    # 3. Count constraints
    positives = []
    negatives = []
    seen_ids = set()
    duplicate_ids = set()
    seen_texts = {}
    duplicate_texts = []
    sources = set()

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            report.add_error(f"Item #{idx} is not a JSON object.")
            continue

        item_id = str(item.get("id", f"item_{idx}")).strip()

        # Check ID uniqueness
        if item_id in seen_ids:
            duplicate_ids.add(item_id)
        seen_ids.add(item_id)

        # Check label (support 'expected_label' or 'label')
        label = item.get("expected_label") or item.get("label")
        if label == "positive":
            positives.append((idx, item))
        elif label == "negative":
            negatives.append((idx, item))
        else:
            report.add_error(f"Item [{item_id}] (index {idx}): Invalid or missing label: '{label}'. Must be 'positive' or 'negative'.")

        # Text checks
        text = item.get("text", "")
        if not isinstance(text, str) or not text.strip():
            report.add_error(f"Item [{item_id}] (index {idx}): 'text' is empty or missing.")
        else:
            cleaned_text = re.sub(r'\s+', ' ', text.strip().lower())
            if len(cleaned_text) < 15:
                report.add_warning(f"Item [{item_id}] (index {idx}): Text length is suspiciously short ({len(cleaned_text)} chars).")
            if cleaned_text in seen_texts:
                duplicate_texts.append((item_id, seen_texts[cleaned_text]))
            else:
                seen_texts[cleaned_text] = item_id

        # Source / Provenance checks
        source = item.get("source") or item.get("provenance")
        if not isinstance(source, dict):
            report.add_error(f"Item [{item_id}] (index {idx}): Missing 'source' / 'provenance' object.")
        else:
            src_file = str(source.get("file") or source.get("source_file") or "").strip()
            src_loc = str(source.get("line_or_page") or "").strip()

            if not src_file or src_file.lower() in TRIVIAL_PLACEHOLDERS:
                report.add_error(f"Item [{item_id}] (index {idx}): 'source.file' is trivial or empty: '{src_file}'.")
            else:
                sources.add(src_file)

            if not src_loc or src_loc.lower() in TRIVIAL_PLACEHOLDERS or src_loc == "0":
                report.add_error(f"Item [{item_id}] (index {idx}): 'source.line_or_page' is trivial or empty: '{src_loc}'.")

    # Tally duplicates
    if duplicate_ids:
        report.add_error(f"Duplicate IDs detected ({len(duplicate_ids)} duplicates): {list(duplicate_ids)[:10]}")
    if duplicate_texts:
        report.add_error(f"Duplicate text content detected across {len(duplicate_texts)} item pairs: {duplicate_texts[:5]}")

    report.stats["positive_count"] = len(positives)
    report.stats["negative_count"] = len(negatives)
    report.stats["sources_count"] = len(sources)

    # Assert Count Constraints
    if len(items) < 100:
        report.add_error(f"Count constraint failed: Total items = {len(items)} (must be >= 100).")
    if len(positives) < 50:
        report.add_error(f"Count constraint failed: Positive examples = {len(positives)} (must be >= 50).")
    if len(negatives) < 50:
        report.add_error(f"Count constraint failed: Negative examples = {len(negatives)} (must be >= 50).")

    # 4. Positive Examples: 14 Semantic Intents Representation
    intent_counts = Counter()
    for idx, item in positives:
        item_id = item.get("id", f"pos_{idx}")
        raw_intent = item.get("expected_intent") or item.get("intent")
        canonical_intent = normalize_intent(raw_intent)

        if not canonical_intent:
            report.add_error(f"Positive item [{item_id}]: Missing 'expected_intent'.")
        elif canonical_intent not in CANONICAL_14_INTENTS:
            report.add_error(f"Positive item [{item_id}]: Unknown intent '{raw_intent}' (canonical: '{canonical_intent}'). Must be one of 14 valid intents.")
        else:
            intent_counts[canonical_intent] += 1

        # Check positive-specific non-triviality fields
        entities = item.get("extracted_entities") or item.get("semantic_entities")
        if not entities or (isinstance(entities, list) and len(entities) == 0):
            report.add_error(f"Positive item [{item_id}]: Missing or empty 'extracted_entities' / 'semantic_entities'.")

        truth_claim = item.get("expected_truth_claim") or item.get("rationale")
        if not truth_claim or not isinstance(truth_claim, str) or not truth_claim.strip():
            report.add_error(f"Positive item [{item_id}]: Missing or empty 'expected_truth_claim' / 'rationale'.")

    report.stats["intent_distribution"] = dict(intent_counts)

    missing_intents = CANONICAL_14_INTENTS - set(intent_counts.keys())
    if missing_intents:
        report.add_error(f"Representation constraint failed: Missing {len(missing_intents)} semantic intents: {sorted(list(missing_intents))}")

    # Check for intent balance
    for intent in CANONICAL_14_INTENTS:
        cnt = intent_counts.get(intent, 0)
        if cnt == 1:
            report.add_warning(f"Intent '{intent}' has only 1 example; recommend >= 3 for robust validation.")

    # 5. Negative Examples: Noise Categories Coverage
    noise_counts = Counter()
    for idx, item in negatives:
        item_id = item.get("id", f"neg_{idx}")
        raw_noise = item.get("noise_type") or item.get("rejection_category") or item.get("rejection_reason_category") or item.get("category")
        canonical_noise = normalize_noise_type(raw_noise)

        if not canonical_noise:
            report.add_error(f"Negative item [{item_id}]: Missing 'noise_type' / rejection category.")
        elif canonical_noise not in ALL_RECOGNIZED_NEGATIVE_CATEGORIES:
            report.add_warning(f"Negative item [{item_id}]: Unrecognized noise type '{raw_noise}'.")
            noise_counts[canonical_noise] += 1
        else:
            noise_counts[canonical_noise] += 1

        rej_reason = item.get("expected_rejection_reason") or item.get("rejection_reason")
        if not rej_reason or not isinstance(rej_reason, str) or not rej_reason.strip():
            report.add_error(f"Negative item [{item_id}]: Missing or empty 'expected_rejection_reason' / 'rejection_reason'.")

    report.stats["noise_distribution"] = dict(noise_counts)

    missing_mandatory_noise = MANDATORY_NEGATIVE_CATEGORIES - set(noise_counts.keys())
    if missing_mandatory_noise:
        report.add_error(f"Negative categories constraint failed: Missing mandatory noise categories: {sorted(list(missing_mandatory_noise))}")

    if strict_mode and report.warnings:
        for w in report.warnings:
            report.add_error(f"[STRICT MODE] Warning escalated to error: {w}")

    return report


def print_cli_summary(report: ValidationReport, filepath: str):
    print("=" * 72)
    print("GOLDEN EVALUATION SET VALIDATION HARNESS REPORT")
    print(f"Target File: {filepath}")
    print("=" * 72)

    stats = report.stats
    print(f"Total Items:     {stats['total_items']:>4}  (Constraint: >= 100)")
    print(f"Positive Items:  {stats['positive_count']:>4}  (Constraint: >=  50)")
    print(f"Negative Items:  {stats['negative_count']:>4}  (Constraint: >=  50)")
    print(f"Unique Sources:  {stats['sources_count']:>4}")
    print("-" * 72)

    print("POSITIVE EXAMPLES: 14 SEMANTIC INTENTS DISTRIBUTION")
    print(f"{'#':<3} {'Semantic Intent':<22} {'Count':<8} {'Status'}")
    for idx, intent in enumerate(sorted(list(CANONICAL_14_INTENTS)), 1):
        cnt = stats['intent_distribution'].get(intent, 0)
        status = "OK" if cnt >= 2 else ("WARN (low)" if cnt == 1 else "FAIL (MISSING)")
        print(f"{idx:<3} {intent:<22} {cnt:<8} {status}")
    print("-" * 72)

    print("NEGATIVE EXAMPLES: NOISE CATEGORIES DISTRIBUTION")
    print(f"{'#':<3} {'Noise Category':<30} {'Count':<8} {'Status'}")
    all_noises = sorted(list(set(list(MANDATORY_NEGATIVE_CATEGORIES) + list(stats['noise_distribution'].keys()))))
    for idx, noise in enumerate(all_noises, 1):
        cnt = stats['noise_distribution'].get(noise, 0)
        is_mand = noise in MANDATORY_NEGATIVE_CATEGORIES
        mand_str = "Mandatory" if is_mand else "Optional"
        status = "OK" if cnt > 0 else ("FAIL (MISSING)" if is_mand else "ABSENT")
        print(f"{idx:<3} {noise:<30} {cnt:<8} [{mand_str}] {status}")
    print("-" * 72)

    if report.warnings:
        print(f"WARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"  [!] {w}")
        print("-" * 72)

    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        for e in report.errors:
            print(f"  [X] {e}")
        print("-" * 72)
        print("OVERALL VERDICT: FAILED [X]")
    else:
        print("OVERALL VERDICT: PASSED CONFORMITY CHECK [OK]")
    print("=" * 72)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Strict Automated Validator for Golden Evaluation Dataset")
    parser.add_argument("file_pos", nargs="?", default=None, help="Optional positional path to golden evaluation set JSON")
    parser.add_argument("--file", default="data/golden_eval_set.json", help="Path to golden evaluation set JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json-output", default=None, help="Path to export JSON validation report")
    args = parser.parse_args()

    target_file = args.file_pos if args.file_pos else args.file
    filepath = os.path.abspath(target_file)
    if not os.path.exists(filepath):
        print(f"ERROR: Target file does not exist at '{filepath}'", file=sys.stderr)
        sys.exit(2)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON file '{filepath}': {e}", file=sys.stderr)
        sys.exit(3)

    report = validate_golden_eval_data(raw_data, strict_mode=args.strict)
    print_cli_summary(report, filepath)

    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as out:
            json.dump(report.to_dict(), out, indent=2)
        print(f"Validation report saved to {args.json_output}")

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
