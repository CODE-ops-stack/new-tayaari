"""
Locked Android data contract for Tayaari Pakki questions.

Android (TestModels / QuestionSelectionEngine / PracticeScreen) is the source of truth:

    options                 = [{"id": "opt_a", "text": "..."}, ...]
    correctAnswer           = "opt_a"   # MUST be one of options[].id
    distractorDissections   = [{"optionId": "opt_b", "trapType": "...", "dissection": "..."}]

No silent dual-format. Bare-letter dicts are a contract violation.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence, Tuple

OPTION_ID_PREFIX = "opt_"
OPTION_ID_RE = re.compile(r"^opt_[a-e]$")
SUPPORTED_LETTERS = ("a", "b", "c", "d", "e")
MIN_OPTIONS = 4
MAX_OPTIONS = 5
DISSECTION_KEYS = frozenset({"optionId", "trapType", "dissection"})
VALID_TRAP_TYPES = frozenset(
    {
        "ABSOLUTE_WORDING",
        "FACT_DISTORTION",
        "FAMILIARITY_TRAP",
        "CONCEPT_MIX",
        "FALSE_CORRELATION",
        "PARTIAL_TRUTH",
        "TIMELINE_MISMATCH",
        "UNCLASSIFIED_TRAP",
    }
)
VALID_FORMATS = frozenset(
    {
        "Statement-based",
        "Direct Fact",
        "Matching",
        "Assertion-Reason",
        "Application",
    }
)
VALID_TIERS = frozenset({"Basic", "Medium", "Advanced", "Elite"})


def option_ids(options: Sequence[Dict[str, str]]) -> List[str]:
    return [str(opt.get("id", "")) for opt in options]


def validate_locked_question(q: Any) -> List[str]:
    """Return a list of contract violations. Empty list means PASS.

    Accepts a dict or an object with the locked fields. Fail-closed: unknown
    option shapes are errors, never repaired here.
    """
    errors: List[str] = []
    getter = q.get if isinstance(q, dict) else lambda k, d=None: getattr(q, k, d)

    options = getter("options")
    correct = getter("correctAnswer")
    dissections = getter("distractorDissections")
    stem = getter("stem") or getter("questionText") or ""

    if not isinstance(options, list):
        errors.append(
            f"options must be a list of {{id,text}} dicts; got {type(options).__name__}"
        )
        return errors

    if len(options) < MIN_OPTIONS or len(options) > MAX_OPTIONS:
        errors.append(
            f"options count {len(options)} not in [{MIN_OPTIONS},{MAX_OPTIONS}]"
        )

    ids: List[str] = []
    texts: List[str] = []
    for i, opt in enumerate(options):
        if not isinstance(opt, dict):
            errors.append(f"options[{i}] is not a dict")
            continue
        if "id" not in opt or "text" not in opt:
            errors.append(f"options[{i}] missing id/text keys: {sorted(opt.keys())}")
            continue
        oid = str(opt["id"])
        text = opt["text"]
        if not OPTION_ID_RE.match(oid):
            errors.append(f"options[{i}].id {oid!r} is not opt_[a-e]")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"options[{i}].text is empty or non-string")
        ids.append(oid)
        texts.append(str(text).strip())

    expected = [f"{OPTION_ID_PREFIX}{c}" for c in SUPPORTED_LETTERS[: len(options)]]
    if ids and ids != expected:
        errors.append(f"options ids must be exactly {expected} in order; got {ids}")

    lowered = [t.lower() for t in texts if t]
    if len(lowered) != len(set(lowered)):
        errors.append(f"duplicate option texts: {texts}")

    if not isinstance(correct, str) or not OPTION_ID_RE.match(correct):
        errors.append(f"correctAnswer {correct!r} is not an opt_[a-e] id")
    elif correct not in ids:
        errors.append(f"correctAnswer {correct!r} is not in option ids {ids}")

    if not isinstance(dissections, list):
        errors.append(
            f"distractorDissections must be a list; got {type(dissections).__name__}"
        )
    else:
        dissected: List[str] = []
        for i, d in enumerate(dissections):
            if not isinstance(d, dict):
                errors.append(f"distractorDissections[{i}] is not a dict")
                continue
            missing = DISSECTION_KEYS - set(d.keys())
            extra_legacy = {"option", "rationale", "optionText"} & set(d.keys())
            if missing:
                errors.append(
                    f"distractorDissections[{i}] missing {sorted(missing)}; keys={sorted(d.keys())}"
                )
            if extra_legacy and missing:
                errors.append(
                    f"distractorDissections[{i}] uses legacy keys {sorted(extra_legacy)}"
                )
            oid = str(d.get("optionId", ""))
            if oid == correct:
                errors.append("dissection tagged the correct answer")
            if oid and oid not in ids:
                errors.append(f"dissection optionId {oid!r} not in option ids")
            trap = str(d.get("trapType", ""))
            if trap and trap not in VALID_TRAP_TYPES:
                errors.append(f"unknown trapType {trap!r}")
            if not str(d.get("dissection", "")).strip():
                errors.append(f"distractorDissections[{i}].dissection is empty")
            dissected.append(oid)
        distractor_ids = [oid for oid in ids if oid != correct]
        if dissected and sorted(dissected) != sorted(distractor_ids):
            errors.append(
                f"dissections must cover every distractor exactly once; "
                f"got {sorted(dissected)} expected {sorted(distractor_ids)}"
            )

    if not isinstance(stem, str) or not stem.strip():
        errors.append("stem is empty")

    fmt = getter("format")
    if fmt is not None and fmt not in VALID_FORMATS:
        errors.append(f"format {fmt!r} is not a recognised exam format")

    tier = getter("tier")
    if tier is not None and tier not in VALID_TIERS:
        errors.append(f"tier {tier!r} is not in {sorted(VALID_TIERS)}")

    return errors


def assert_locked_contract(q: Any) -> None:
    errors = validate_locked_question(q)
    if errors:
        raise ValueError("LOCKED CONTRACT VIOLATION: " + "; ".join(errors))


def is_legacy_bare_letter_options(options: Any) -> bool:
    return isinstance(options, dict) and options and all(
        str(k).lower() in SUPPORTED_LETTERS for k in options.keys()
    )


def reject_legacy_mismatch(options: Any, correct_answer: Any) -> List[str]:
    """Regression helper: the historical 1200-question defect."""
    errors: List[str] = []
    if is_legacy_bare_letter_options(options) and str(correct_answer).startswith(
        OPTION_ID_PREFIX
    ):
        errors.append(
            "answer-key mismatch: options keyed a/b/c/d but correctAnswer is opt_*"
        )
    if isinstance(options, dict):
        errors.append("options is a dict; locked contract requires a list")
    return errors
