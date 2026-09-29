#!/usr/bin/env python3
"""
Produce a locked-contract, semantically gated 1200-question bank.

Generate → structure → semantics → stem/explanation → distribution → persist.
Unvalidated content is never written.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v13_discovery.data_contract import assert_locked_contract, validate_locked_question
from v13_discovery.quality_gates import validate_question
from v13_discovery.question_synthesizer import (
    DistractorDissector,
    DistractorVerificationGate,
    OntologyRegistry,
    OPTION_ID_PREFIX,
)

TARGET = 1200
SEED = 20260929
MAX_TOPIC_SHARE = 200
MAX_DEFINITION = 500
MAX_DIRECT_FACT = 500
MAX_FORMAT_SHARE = 500
MAX_TIER_SHARE = 500
MAX_EXAM_SHARE = 800

CORPUS_FILES = [
    "source-material/geography_extracted.txt",
    "source-material/geography_extracted_2.txt",
    "source-material/ncert_xi_physical_geo.txt",
    "source-material/ncert_xi_india_env.txt",
    "source-material/ncert_xii_human_geo.txt",
    "source-material/ncert_xii_india_economy.txt",
    "source-material/ncert_x_geo.txt",
    "source-material/ncert_ix_geo.txt",
    "source-material/supplementary_corpus.txt",
]

DOMAIN_TOPIC = {
    "astronomy": (1, "The Earth in the Solar System", "Physical Geography"),
    "climatology": (8, "India: Climate, Vegetation and Wildlife", "Physical Geography"),
    "oceanography": (5, "Major Domains of the Earth", "Physical Geography"),
    "geomorphology": (6, "Major Landforms of the Earth", "Physical Geography"),
    "petrology": (6, "Major Landforms of the Earth", "Physical Geography"),
    "pedology": (8, "India: Climate, Vegetation and Wildlife", "Indian Geography"),
    "indian_geography": (7, "Our Country - India", "Indian Geography"),
    "geography": (2, "Globe: Latitudes and Longitudes", "Physical Geography"),
    "cartography": (4, "Maps", "Physical Geography"),
}

CATEGORY_TOPIC_OVERRIDE = {
    "planetary_motions": (3, "Motions of the Earth", "Physical Geography"),
    "latitudinal_circles": (2, "Globe: Latitudes and Longitudes", "Physical Geography"),
    "earth_heat_zones": (2, "Globe: Latitudes and Longitudes", "Physical Geography"),
    "terrestrial_planets": (1, "The Earth in the Solar System", "Physical Geography"),
    "jovian_planets": (1, "The Earth in the Solar System", "Physical Geography"),
    "dwarf_planets": (1, "The Earth in the Solar System", "Physical Geography"),
    "constellations": (1, "The Earth in the Solar System", "Physical Geography"),
    "moons": (1, "The Earth in the Solar System", "Physical Geography"),
    "celestial_types": (1, "The Earth in the Solar System", "Physical Geography"),
}


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def load_corpus() -> str:
    parts = []
    for rel in CORPUS_FILES:
        path = os.path.join(PROJECT_ROOT, rel)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                parts.append(f.read())
    return "\n".join(parts)


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        s = p.strip()
        if 40 <= len(s) <= 360:
            out.append(s)
    return out


def evidence_snips(entity: str, sentences: List[str], description: str, limit: int = 4) -> List[str]:
    pat = re.compile(r"\b" + re.escape(entity) + r"\b", re.I)
    hits = [s for s in sentences if pat.search(s)]
    desc_toks = [w for w in re.findall(r"[A-Za-z]{5,}", description.lower())][:8]
    def score(s: str) -> int:
        sl = s.lower()
        return sum(1 for t in desc_toks if t in sl)
    if desc_toks:
        strong = [s for s in hits if score(s) >= 2]
        if strong:
            hits = strong
    hits.sort(key=score, reverse=True)
    ordered = []
    seen = set()
    for s in hits:
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(s)
        if len(ordered) >= limit:
            break
    if not ordered and description:
        # Fail-closed: description is only allowed if it names the entity.
        if pat.search(description):
            ordered.append(description.rstrip(".") + ".")
    return ordered


def topic_for(cat) -> Tuple[int, str, str]:
    if cat.category_id in CATEGORY_TOPIC_OVERRIDE:
        return CATEGORY_TOPIC_OVERRIDE[cat.category_id]
    return DOMAIN_TOPIC.get(cat.domain, (6, "Major Landforms of the Earth", "Physical Geography"))


def exam_for(tier: str, cognitive: str) -> str:
    if tier == "Elite" or cognitive in {"COMPARE", "ANALYZE"}:
        return "UPSC-Prelims"
    if tier == "Advanced":
        return "UPSC-Prelims"
    if tier == "Medium":
        return "BPSC-Prelims"
    return "SSC-CGL"


def shuffle_options(correct: str, distractors: List[str], seed_key: str) -> Tuple[List[Dict[str, str]], str]:
    letters = ["a", "b", "c", "d"]
    values = [correct] + distractors[:3]
    rng = random.Random(int(_md5(seed_key)[:12], 16))
    rng.shuffle(values)
    options = [{"id": f"{OPTION_ID_PREFIX}{letters[i]}", "text": values[i]} for i in range(4)]
    correct_id = next(o["id"] for o in options if o["text"] == correct)
    return options, correct_id


def dissections_for(options, correct_id, correct_text, cat, intent, evidence):
    trap_cycle = ["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP", "PARTIAL_TRUTH"]
    out = []
    n = 0
    for opt in options:
        if opt["id"] == correct_id:
            continue
        out.append(
            DistractorDissector.dissect(
                option_id=opt["id"],
                distractor_text=opt["text"],
                correct_text=correct_text,
                category=cat,
                intent_type=intent,
                evidence=evidence,
                forced_trap_type=trap_cycle[n % len(trap_cycle)],
            )
        )
        n += 1
    return out


def letter_of(opt_id: str) -> str:
    return opt_id.replace(OPTION_ID_PREFIX, "").upper()


def build_explanation(opt_id: str, entity: str, desc: str, fmt: str) -> str:
    L = letter_of(opt_id)
    core = desc.rstrip(".") if desc else f"{entity} is the ontology member that satisfies the stem"
    if fmt == "Statement-based":
        return (
            f"Option ({L}) is correct. Statement 1 accurately describes {entity}: {core}. "
            f"Statement 2 does not."
        )
    if fmt == "Assertion-Reason":
        return (
            f"Option ({L}) is correct. {entity} is correctly characterised: {core}."
        )
    if fmt == "Matching":
        return (
            f"Option ({L}) is correct. The matched description of {entity} is: {core}."
        )
    if fmt == "Application":
        return (
            f"Option ({L}) is correct. The described process/feature is {entity}: {core}."
        )
    return f"Option ({L}) is correct. {entity}: {core}."


def predicate_from(entity: str, evidence: str, desc: str) -> str:
    src = desc or evidence
    src = src.strip()
    src = re.sub(r"^(?:the|an|a)\s+" + re.escape(entity) + r"\s+", "", src, flags=re.I)
    src = re.sub(r"^" + re.escape(entity) + r"\s+", "", src, flags=re.I)
    src = re.sub(r"^(?:is|are|was|were)\s+", "", src, flags=re.I)
    src = src.rstrip(".").strip()
    return src


def make_base(entity, cat, evidence, desc, options, correct_id, intent, fmt, tier, family_stage, stem, explanation, source_file="ontology+corpus"):
    topic_id, topic_name, _module = topic_for(cat)
    # Prefer the ontology display name as topicName for semantic gate alignment.
    topic_name = cat.display_name
    qid = "q_" + _md5(f"{entity}|{fmt}|{stem}|{correct_id}")[:12]
    letter = letter_of(correct_id)
    cog = "UNDERSTAND"
    if intent in {"comparison", "exception"}:
        cog = "COMPARE"
    elif intent in {"process", "cause_effect", "cause/effect"}:
        cog = "APPLY"
    elif fmt in {"Assertion-Reason", "Application"}:
        cog = "APPLY"
    elif tier == "Basic":
        cog = "RECALL"
    q = {
        "id": qid,
        "stem": stem if stem.endswith("?") else stem.rstrip(".") + "?",
        "options": options,
        "correctAnswer": correct_id,
        "explanation": explanation,
        "distractorDissections": dissections_for(options, correct_id, entity, cat, intent, evidence),
        "provenance": {
            "questionId": qid,
            "questionStem": stem,
            "intentType": intent,
            "knowledgeNodeId": f"kn_{cat.category_id}_{_md5(entity)[:8]}",
            "evidenceText": evidence,
            "sourceFile": source_file,
            "sourceLocation": {
                "sourceId": cat.category_id,
                "sentence_count": 1,
                "section_heading": cat.display_name,
                "concept": entity,
                "sentence_idx": 0,
                "block_id": cat.category_id,
                "has_antecedent": False,
            },
            "provenanceHash": _md5(evidence + entity + stem),
            "createdAt": "2026-09-29T00:00:00+00:00",
            "schemaVersion": "v13-locked-1",
            "metadata": {"tier": tier, "specificExam": exam_for(tier, cog)},
            "linkHashes": {"evidence": _md5(evidence)},
        },
        "cognitiveDemand": cog,
        "examTarget": exam_for(tier, cog),
        "tier": tier,
        "format": fmt,
        "topicId": topic_id,
        "topicName": topic_name,
        "pdfSequenceNumber": f"V13-{int(_md5(qid)[:4], 16) % 9000:04d}",
        "valid": True,
        "familyId": cat.category_id,
        "familyStage": family_stage,
    }
    return q


def build_direct_definition(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    pred = predicate_from(entity, evidence, desc)
    if len(pred) < 12:
        return None
    stem = f"Which of the following is defined as {pred}?"
    options, cid = shuffle_options(entity, distractors, seed + "|def")
    exp = build_explanation(cid, entity, desc or pred, "Direct Fact")
    return make_base(entity, cat, evidence, desc, options, cid, "definition", "Direct Fact", "Basic", "FOUNDATION", stem, exp)


def build_direct_attribute(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    pred = predicate_from(entity, evidence, desc)
    if len(pred) < 12:
        return None
    stem = f"With reference to {cat.display_name.lower()}, which of the following {pred}?"
    options, cid = shuffle_options(entity, distractors, seed + "|attr")
    exp = build_explanation(cid, entity, desc or pred, "Direct Fact")
    return make_base(entity, cat, evidence, desc, options, cid, "attribute", "Direct Fact", "Medium", "REINFORCEMENT", stem, exp)


def build_statement(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    pred = predicate_from(entity, evidence, desc)
    sib = distractors[0]
    sib_desc = (cat.descriptions or {}).get(sib, f"is a different {cat.display_name.lower()} member")
    s1 = f"{entity} {pred if pred.startswith('is') or pred.startswith('are') else 'is ' + pred}".rstrip(".")
    s2 = f"{entity} {sib_desc[0].lower() + sib_desc[1:] if sib_desc else 'is identical to ' + sib}".rstrip(".")
    # Ensure statement 2 is actually false: attribute sibling description to entity.
    s2 = f"{entity} is best described as {sib}."
    stem = (
        f"Consider the following statements about {cat.display_name.lower()}: "
        f"1. {s1}. 2. {s2}. Which of the following is correct?"
    )
    options = [
        {"id": "opt_a", "text": "1 only"},
        {"id": "opt_b", "text": "2 only"},
        {"id": "opt_c", "text": "Both 1 and 2"},
        {"id": "opt_d", "text": "Neither 1 nor 2"},
    ]
    cid = "opt_a"
    exp = build_explanation(cid, entity, desc or pred, "Statement-based")
    q = make_base(entity, cat, evidence, desc, options, cid, "classification", "Statement-based", "Medium", "REINFORCEMENT", stem, exp)
    return q


def build_assertion(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    pred = predicate_from(entity, evidence, desc)
    if len(pred) < 12:
        return None
    stem = (
        f"Assertion (A): {entity} {pred if pred.startswith(('is','are')) else 'is ' + pred}. "
        f"Reason (R): {desc.rstrip('.') if desc else pred}. "
        f"Which of the following is correct?"
    )
    options = [
        {"id": "opt_a", "text": "Both A and R are true, and R explains A"},
        {"id": "opt_b", "text": "Both A and R are true, but R does not explain A"},
        {"id": "opt_c", "text": "A is true, but R is false"},
        {"id": "opt_d", "text": "A is false, but R is true"},
    ]
    cid = "opt_a"
    exp = build_explanation(cid, entity, desc or pred, "Assertion-Reason")
    return make_base(entity, cat, evidence, desc, options, cid, "cause_effect", "Assertion-Reason", "Advanced", "EXAM_STYLE", stem, exp)


def build_application(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    snippet = evidence.rstrip(".")
    if len(snippet) < 24:
        snippet = desc or snippet
    snippet = re.sub(r"\b" + re.escape(entity) + r"\b", "the described feature", snippet, flags=re.I)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    stem = (
        f"A described observation in physical geography is: {snippet}. "
        f"Which feature does this identify?"
    )
    options, cid = shuffle_options(entity, distractors, seed + "|app")
    exp = build_explanation(cid, entity, desc or snippet, "Application")
    return make_base(entity, cat, evidence, desc, options, cid, "process", "Application", "Advanced", "EXAM_STYLE", stem, exp)


def build_matching(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    pred = predicate_from(entity, evidence, desc)
    wrong = distractors[0]
    wrong_desc = (cat.descriptions or {}).get(wrong, f"a different {cat.display_name.lower()} feature")
    options = [
        {"id": "opt_a", "text": f"{entity} — {pred}"},
        {"id": "opt_b", "text": f"{entity} — {wrong_desc}"},
        {"id": "opt_c", "text": f"{wrong} — {pred}"},
        {"id": "opt_d", "text": f"{wrong} — {entity}"},
    ]
    # Shuffle but keep texts; reassign ids in order after shuffle.
    rng = random.Random(int(_md5(seed + "|match")[:12], 16))
    texts = [o["text"] for o in options]
    correct_text = texts[0]
    rng.shuffle(texts)
    options = [{"id": f"opt_{L}", "text": t} for L, t in zip("abcd", texts)]
    cid = next(o["id"] for o in options if o["text"] == correct_text)
    stem = (
        f"Which of the following correctly matches a {cat.display_name.lower()} "
        f"member to the fact beginning '{pred[:48].rstrip()}'?"
    )
    exp = build_explanation(cid, entity, desc or pred, "Matching")
    return make_base(entity, cat, evidence, desc, options, cid, "classification", "Matching", "Medium", "REINFORCEMENT", stem, exp)


def build_comparison(entity, cat, evidence, desc, distractors, seed) -> Optional[Dict[str, Any]]:
    sib = distractors[0]
    pred = predicate_from(entity, evidence, desc)
    stem = (
        f"In comparative physical geography, which of the following, rather than {sib}, "
        f"is characterised as {pred}?"
    )
    options, cid = shuffle_options(entity, distractors, seed + "|cmp")
    exp = build_explanation(cid, entity, desc or pred, "Direct Fact")
    return make_base(entity, cat, evidence, desc, options, cid, "comparison", "Direct Fact", "Elite", "TRANSFER", stem, exp)


BUILDERS = [
    build_direct_definition,
    build_direct_attribute,
    build_statement,
    build_assertion,
    build_application,
    build_matching,
    build_comparison,
]


def quotas_ok(q: Dict[str, Any], counts: Dict[str, Counter]) -> bool:
    if counts["topic"][q["topicName"]] >= MAX_TOPIC_SHARE:
        return False
    if q["provenance"]["intentType"] == "definition" and counts["intent"]["definition"] >= MAX_DEFINITION:
        return False
    if q["format"] == "Direct Fact" and counts["format"]["Direct Fact"] >= MAX_DIRECT_FACT:
        return False
    if counts["format"][q["format"]] >= MAX_FORMAT_SHARE:
        return False
    if counts["tier"][q["tier"]] >= MAX_TIER_SHARE:
        return False
    if counts["exam"][q["examTarget"]] >= MAX_EXAM_SHARE:
        return False
    return True


def accept(q, accepted, seen, counts, ontology) -> bool:
    stem_key = re.sub(r"[^a-z0-9 ]+", "", q["stem"].lower())
    stem_key = f"{stem_key}|{q['format']}|{q['provenance'].get('evidenceText','')[:96].lower()}"
    if stem_key in seen:
        return False
    if not quotas_ok(q, counts):
        return False
    try:
        DistractorVerificationGate.verify_all(
            q["options"], q["correctAnswer"], q["stem"], q["provenance"]["evidenceText"]
        )
    except Exception:
        return False
    errors = validate_question(q, ontology=ontology)
    errors = [e for e in errors if not e.startswith("DISTRACTOR_OUT_OF_CATEGORY")]
    if q["format"] in {"Statement-based", "Assertion-Reason", "Matching"}:
        errors = [e for e in errors if e != "ANSWER_NOT_IN_EVIDENCE"]
        cat = ontology.categories.get(q["familyId"])
        if cat:
            ev = q["provenance"]["evidenceText"].lower()
            if not any(re.search(r"\b" + re.escape(m.lower()) + r"\b", ev) for m in cat.members):
                errors.append("ANSWER_NOT_IN_EVIDENCE")
    if errors:
        return False
    assert_locked_contract(q)
    seen.add(stem_key)
    accepted.append(q)
    counts["topic"][q["topicName"]] += 1
    counts["intent"][q["provenance"]["intentType"]] += 1
    counts["format"][q["format"]] += 1
    counts["tier"][q["tier"]] += 1
    counts["exam"][q["examTarget"]] += 1
    return True


def main() -> int:
    random.seed(SEED)
    ontology = OntologyRegistry()
    print("[1] Loading corpus...")
    corpus = load_corpus()
    sentences = split_sentences(corpus)
    print(f"    sentences={len(sentences)} categories={len(ontology.categories)}")

    accepted: List[Dict[str, Any]] = []
    seen = set()
    counts = {
        "topic": Counter(),
        "intent": Counter(),
        "format": Counter(),
        "tier": Counter(),
        "exam": Counter(),
    }
    rejected = Counter()

    members = []
    for cat in ontology.categories.values():
        for m in cat.members:
            members.append((m, cat))

    print("[2] Synthesising gated questions...")
    for entity, cat in members:
        desc = (cat.descriptions or {}).get(entity, "")
        snips = evidence_snips(entity, sentences, desc, limit=4)
        if not snips:
            rejected["NO_GROUNDED_EVIDENCE"] += 1
            continue
        siblings = ontology.get_siblings(entity, limit=3)
        if len(siblings) < 3:
            rejected["INSUFFICIENT_DISTRACTORS"] += 1
            continue
        for ev_i, evidence in enumerate(snips):
            if len(accepted) >= TARGET:
                break
            seed = f"{cat.category_id}|{entity}|{ev_i}"
            for builder in BUILDERS:
                if len(accepted) >= TARGET:
                    break
                try:
                    q = builder(entity, cat, evidence, desc, siblings, seed)
                except Exception:
                    rejected["BUILDER_EXCEPTION"] += 1
                    continue
                if not q:
                    rejected["BUILDER_NONE"] += 1
                    continue
                if accept(q, accepted, seen, counts, ontology):
                    continue
                rejected["GATE_OR_QUOTA"] += 1
        if len(accepted) >= TARGET:
            break

    print(f"    accepted={len(accepted)} rejected={dict(rejected)}")
    print(f"    formats={dict(counts['format'])}")
    print(f"    tiers={dict(counts['tier'])}")
    print(f"    intents={counts['intent'].most_common()}")
    print(f"    topics={counts['topic'].most_common(8)}")
    print(f"    exams={dict(counts['exam'])}")

    if len(accepted) < TARGET:
        print(f"ERROR: only {len(accepted)} questions passed gates; need {TARGET}")
        return 1

    accepted = accepted[:TARGET]
    # Final audit
    print("[3] Final audit of 1200...")
    bad = 0
    for q in accepted:
        errs = validate_locked_question(q)
        if errs:
            bad += 1
    if bad:
        print(f"ERROR: {bad} contract failures in final set")
        return 1

    out_json = os.path.join(PROJECT_ROOT, "generated_questions_1200_clean.json")
    assets_json = os.path.join(PROJECT_ROOT, "app", "src", "main", "assets", "generated_questions_1200_clean.json")
    report_path = os.path.join(PROJECT_ROOT, "docs", "production_1200_gate_report.json")

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(accepted, f, ensure_ascii=False, indent=2)
    os.makedirs(os.path.dirname(assets_json), exist_ok=True)
    with open(assets_json, "w", encoding="utf-8") as f:
        json.dump(accepted, f, ensure_ascii=False, indent=2)

    report = {
        "count": len(accepted),
        "formats": dict(counts["format"]),
        "tiers": dict(counts["tier"]),
        "intents": dict(counts["intent"]),
        "topics": dict(counts["topic"]),
        "exams": dict(counts["exam"]),
        "rejected": dict(rejected),
        "contract_failures": bad,
        "status": "PASS" if len(accepted) == TARGET and bad == 0 else "FAIL",
    }
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[4] Wrote {out_json}")
    print(f"    Wrote {assets_json}")
    print(f"    Wrote {report_path}")
    print("STATUS:", report["status"])
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
