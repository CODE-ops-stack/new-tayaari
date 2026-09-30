"""
Fail-closed semantic / stem / explanation gates.

Unknown → reject. No silent category fallback. No substring ontology matching.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from v13_discovery.data_contract import VALID_TRAP_TYPES, validate_locked_question
from v13_discovery.question_synthesizer import OntologyRegistry, VALID_ROOM_TRAP_TYPES

PLACEHOLDER_RE = re.compile(
    r"\b(this entity|the described feature|TBD|TODO|placeholder|dummy option|sample option)\b",
    re.IGNORECASE,
)
OCR_JUNK_RE = re.compile(
    r"(figure\s+\d|2018-19|attrib\b|\bpheno\b|best described as|\bit it\b)",
    re.IGNORECASE,
)
CONNECTIVE_START_RE = re.compile(
    r"^(thus|hence|also|so|therefore|moreover|however|furthermore|consequently|additionally)\b",
    re.I,
)
TRUNCATED_TAIL_RE = re.compile(
    r"\b(the|a|an|of|and|to|for|with|as|by|from|that|which|called)\s*[.]*$",
    re.I,
)


def _get(q: Any, key: str, default: Any = None) -> Any:
    if isinstance(q, dict):
        return q.get(key, default)
    return getattr(q, key, default)


def _correct_text(q: Any) -> str:
    options = _get(q, "options") or []
    correct = _get(q, "correctAnswer")
    if isinstance(options, list):
        for opt in options:
            if isinstance(opt, dict) and opt.get("id") == correct:
                return str(opt.get("text", "")).strip()
    return ""


def _evidence(q: Any) -> str:
    prov = _get(q, "provenance") or {}
    if isinstance(prov, dict):
        return (
            prov.get("evidenceText")
            or prov.get("evidenceExcerpt")
            or ""
        ).strip()
    return ""


def validate_stem(q: Any) -> List[str]:
    errors: List[str] = []
    stem = (_get(q, "stem") or "").strip()
    fmt = _get(q, "format") or "Direct Fact"
    if not stem:
        return ["STEM_EMPTY"]
    if PLACEHOLDER_RE.search(stem):
        errors.append("STEM_PLACEHOLDER")
    if CONNECTIVE_START_RE.match(stem):
        errors.append("STEM_STARTS_WITH_CONNECTIVE")
    if not stem.endswith("?"):
        errors.append("STEM_NOT_A_QUESTION")
    if TRUNCATED_TAIL_RE.search(stem.rstrip("?").strip()):
        errors.append("STEM_TRUNCATED")
    if len(stem) < 24:
        errors.append("STEM_TOO_SHORT")
    limit = 420 if fmt in {"Statement-based", "Assertion-Reason", "Matching", "Application"} else 240
    if len(stem) > limit:
        errors.append("STEM_TOO_LONG")
    if stem.count("?") > 3:
        errors.append("STEM_MALFORMED_PUNCTUATION")
    if OCR_JUNK_RE.search(stem):
        errors.append("STEM_OCR_OR_TEMPLATE_JUNK")
    if re.search(r"\ban earth['’]s\b|\ba himalayan\b|\ba trans-himalayan\b", stem, re.I):
        errors.append("STEM_ARTICLE_ERROR")
    if ".." in stem:
        errors.append("STEM_DOUBLE_PERIOD")
    if re.search(r"\bdefined as [A-Z]", stem) and "Assertion" not in stem:
        errors.append("STEM_MISSING_ARTICLE")
    if re.search(r"which of the following [A-Z][a-z]+ atmospheric", stem, re.I):
        errors.append("STEM_MISSING_VERB")
    if fmt == "Assertion-Reason":
        am = re.search(r"Assertion \(A\):\s*(.+?)\.\s*Reason \(R\):\s*(.+?)\.", stem)
        if am:
            a = am.group(1).strip().lower()
            r = am.group(2).strip().lower()
            if a == r or a in r or r in a:
                errors.append("AR_TAUTOLOGY")
            r0 = am.group(2).strip().split()[0]
            if r0 not in {"It", "The", "This", "A", "An"}:
                errors.append("AR_FRAGMENT_REASON")
        else:
            errors.append("AR_MALFORMED")
    return errors


def _concept(q: Any) -> str:
    prov = _get(q, "provenance") or {}
    if isinstance(prov, dict):
        loc = prov.get("sourceLocation") or {}
        if isinstance(loc, dict) and loc.get("concept"):
            return str(loc.get("concept")).strip()
        if prov.get("entity"):
            return str(prov.get("entity")).strip()
    return _correct_text(q)


def validate_explanation(q: Any) -> List[str]:
    errors: List[str] = []
    exp = (_get(q, "explanation") or "").strip()
    ans_id = _get(q, "correctAnswer") or ""
    letter = str(ans_id).replace("opt_", "").upper()
    evidence = _evidence(q)
    if not exp:
        return ["EXPLANATION_EMPTY"]
    if PLACEHOLDER_RE.search(exp):
        errors.append("EXPLANATION_PLACEHOLDER")
    if letter and f"Option ({letter})" not in exp and f"Option {letter}" not in exp:
        errors.append("EXPLANATION_MISSING_OPTION_LETTER")
    concept = _concept(q)
    if concept and concept.lower() not in exp.lower():
        errors.append("EXPLANATION_MISSING_CORRECT_ENTITY")
    if evidence and exp.rstrip(".").lower() == evidence.rstrip(".").lower():
        errors.append("EXPLANATION_IS_RAW_SOURCE_DUMP")
    if len(exp) < 40:
        errors.append("EXPLANATION_TOO_SHORT")
    if OCR_JUNK_RE.search(exp):
        errors.append("EXPLANATION_JUNK")
    # Expert explanations must say why the key is right, not only dump a label.
    if "do not" not in exp.lower() and "unlike" not in exp.lower() and "whereas" not in exp.lower() and "not " not in exp.lower():
        errors.append("EXPLANATION_NO_DISTRACTOR_CONTRAST")
    return errors


def validate_semantic_coherence(
    q: Any, ontology: Optional[OntologyRegistry] = None
) -> List[str]:
    errors: List[str] = []
    ontology = ontology or OntologyRegistry()
    stem = (_get(q, "stem") or "").strip()
    evidence = _evidence(q)
    correct = _correct_text(q)
    concept = _concept(q)
    topic = (_get(q, "topicName") or "").strip()
    fmt = _get(q, "format") or "Direct Fact"

    if not evidence:
        errors.append("EVIDENCE_MISSING")
    if not correct:
        errors.append("CORRECT_TEXT_MISSING")
        return errors

    entity_for_evidence = concept or correct
    if evidence:
        if not re.search(
            r"\b" + re.escape(entity_for_evidence.lower()) + r"\b", evidence.lower()
        ):
            errors.append("ANSWER_NOT_IN_EVIDENCE")

    cat = ontology.find_category_for_entity(concept) if concept else None
    if cat is None:
        family = _get(q, "familyId")
        if family and family in ontology.categories:
            cat = ontology.categories[family]
    if cat is None:
        errors.append("UNKNOWN_CATEGORY_REJECTED")
    else:
        if topic and topic.lower() != cat.display_name.lower():
            errors.append(
                f"TOPIC_CATEGORY_MISMATCH topic={topic!r} category={cat.display_name!r}"
            )
        options = _get(q, "options") or []
        if fmt == "Direct Fact" and isinstance(options, list):
            members = {m.lower() for m in cat.members}
            for opt in options:
                text = str(opt.get("text", "")).strip().lower()
                if text and text not in members:
                    errors.append(f"DISTRACTOR_OUT_OF_CATEGORY:{opt.get('text')}")

    if topic.lower() == "geomorphic landforms":
        landform_hints = (
            "meander",
            "oxbow",
            "delta",
            "gorge",
            "floodplain",
            "alluvial",
            "landform",
            "river",
        )
        blob = f"{stem} {evidence} {correct} {concept}".lower()
        if not any(h in blob for h in landform_hints):
            errors.append("TOPIC_STEM_MISMATCH")

    return errors


def validate_question(
    q: Any, ontology: Optional[OntologyRegistry] = None
) -> List[str]:
    errors: List[str] = []
    errors.extend(validate_locked_question(q))
    errors.extend(validate_stem(q))
    errors.extend(validate_explanation(q))
    errors.extend(validate_semantic_coherence(q, ontology=ontology))
    return errors


def question_is_production_ready(
    q: Any, ontology: Optional[OntologyRegistry] = None
) -> bool:
    return not validate_question(q, ontology=ontology)
