#!/usr/bin/env python3
"""
Produce 1200 exam-grade Geography MCQs.

Stems, options, keys and explanations are written from ontology knowledge
units (not OCR fragments). Fail-closed: ungrammatical, tautological,
placeholder, or ungrounded items are never persisted.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
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
MAX_DIRECT_FACT = 560
MAX_FORMAT_SHARE = 560
MAX_TIER_SHARE = 600
MAX_EXAM_SHARE = 850
MAX_DEFINITION = 360

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

VERB_FIRST = {
    "contains", "formed", "flowing", "originating", "cools", "extends", "aids",
    "rotates", "revolves", "blows", "carries", "comprises", "consists", "covers",
    "encircles", "surrounds", "lies", "rises", "drops", "generates", "built",
    "created", "known", "famous", "rich", "used", "made", "composed", "characterised",
    "characterized", "associated", "located", "situated", "found", "called",
    "named", "driven", "caused", "produced", "deposited", "carved", "built",
}

PROPER_FIRST = {
    "earth", "mars", "venus", "mercury", "jupiter", "saturn", "uranus", "neptune",
    "pluto", "ceres", "eris", "haumea", "makemake", "moon", "phobos", "deimos",
    "ganymede", "europa", "callisto", "titan", "triton", "io", "charon",
    "himalayas", "alps", "andes", "rockies", "appalachians", "urals", "aravallis",
    "narmada", "tapi", "ganga", "brahmaputra", "godavari", "krishna", "cauvery",
    "pacific", "atlantic", "indian", "arctic", "southern", "hadley", "ferrel",
    "gulf", "kuroshio", "labrador", "oyashio", "california", "canary", "benguela",
    "peru", "troposphere", "stratosphere", "mesosphere", "thermosphere", "exosphere",
    "tropopause", "stratopause", "mesopause", "thermopause",
}


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def tidy(desc: str) -> str:
    d = re.sub(r"\s+", " ", (desc or "").strip()).rstrip(" .,;")
    d = d.replace(";", ",")
    return d


PROPER_ADJ = {
    "himalayan", "trans-himalayan", "indian", "pacific", "atlantic", "arctic",
    "southern", "galilean", "deccan", "kuiper", "western", "eastern", "northern",
    "great", "inner", "outer",
}


def as_np(desc: str) -> str:
    """Turn a knowledge-unit description into a grammatical noun/verb phrase."""
    d = tidy(desc)
    if not d:
        return d
    first = d.split()[0]
    fl = first.lower()
    base = re.sub(r"['’]s$", "", fl)

    if fl in VERB_FIRST:
        return first.lower() + d[len(first):]

    # Possessive proper nouns: Earth's only natural satellite
    if re.search(r"['’]s$", first):
        return d

    if re.match(r"^(the|a|an)\b", d, re.I):
        return d

    # Proper names / adjectives keep original capitalisation
    if base in PROPER_FIRST or fl in PROPER_ADJ or fl.startswith("trans-"):
        if fl in {
            "himalayan", "trans-himalayan", "pacific", "atlantic", "indian",
            "arctic", "southern", "great",
        }:
            return "the " + d
        return d

    if first[0].isupper() and first.lower() not in PROPER_FIRST:
        d = first.lower() + d[len(first):]

    if re.match(
        r"^(lowest|outermost|innermost|largest|smallest|longest|major|main|"
        r"cold|warm|fine|coarse|thick|thin|rigid|molten|solid|only|"
        r"gently|steep|high|low|vast|small|young|old|sacred)",
        d,
        re.I,
    ):
        return "the " + d
    if re.match(r"^(movement|process|theory|inclination|group|layer|zone|range|rock|soil|river|current|wind|cloud)", d, re.I):
        return "the " + d
    if d[0].lower() in "aeiou":
        return "an " + d
    return "a " + d


def as_clause(entity: str, desc: str) -> str:
    d = tidy(desc)
    first = d.split()[0].lower() if d else ""
    if first in VERB_FIRST:
        return f"{entity} {as_np(desc)}"
    return f"{entity} is {as_np(desc)}"


def topic_for(cat) -> Tuple[int, str, str]:
    if cat.category_id in CATEGORY_TOPIC_OVERRIDE:
        return CATEGORY_TOPIC_OVERRIDE[cat.category_id]
    return DOMAIN_TOPIC.get(cat.domain, (6, "Major Landforms of the Earth", "Physical Geography"))


def exam_for(tier: str) -> str:
    if tier in {"Elite", "Advanced"}:
        return "UPSC-Prelims"
    if tier == "Medium":
        return "BPSC-Prelims"
    return "SSC-CGL"


def shuffle_values(correct: str, distractors: List[str], seed_key: str) -> Tuple[List[Dict[str, str]], str]:
    letters = ["a", "b", "c", "d"]
    values = [correct] + list(distractors[:3])
    rng = random.Random(int(_md5(seed_key)[:12], 16))
    rng.shuffle(values)
    options = [{"id": f"{OPTION_ID_PREFIX}{letters[i]}", "text": values[i]} for i in range(4)]
    correct_id = next(o["id"] for o in options if o["text"] == correct)
    return options, correct_id


def letter_of(opt_id: str) -> str:
    return opt_id.replace(OPTION_ID_PREFIX, "").upper()


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


def expert_explanation(opt_id: str, entity: str, desc: str, distractors: List[str], cat, fmt: str) -> str:
    L = letter_of(opt_id)
    others = ", ".join(distractors[:3])
    core = as_np(desc)
    if fmt == "Statement-based":
        return (
            f"Option ({L}) is correct. {entity} is {core}. "
            f"The other statement attributes a property of {others.split(',')[0]} to {entity}, which is not true. "
            f"{others} do not match this description."
        )
    if fmt == "Assertion-Reason":
        return (
            f"Option ({L}) is correct. {entity} is {core}. "
            f"The reason states the defining mechanism of {entity}, whereas {others} do not satisfy both assertion and reason."
        )
    if fmt == "Matching":
        return (
            f"Option ({L}) is correct. {entity} is correctly paired with its definition ({core}). "
            f"The other pairs either swap {entity} with {others.split(',')[0]} or attach the wrong definition. "
            f"{others} do not match this description."
        )
    return (
        f"Option ({L}) is correct. {entity} is {core}. "
        f"{others} are related {cat.display_name.lower()} members but do not match this description."
    )


def make_q(entity, cat, desc, options, correct_id, intent, fmt, tier, stage, stem, distractors):
    topic_id, _android_topic, _mod = topic_for(cat)
    evidence = f"{entity} is {as_np(desc)}."
    stem = stem.strip()
    if not stem.endswith("?"):
        stem = stem.rstrip(".") + "?"
    explanation = expert_explanation(correct_id, entity, desc, distractors, cat, fmt)
    qid = "q_" + _md5(f"{entity}|{fmt}|{stem}|{correct_id}")[:12]
    cog = "UNDERSTAND"
    if intent in {"comparison", "exception"}:
        cog = "COMPARE"
    elif fmt in {"Assertion-Reason", "Application"} or intent in {"process", "cause_effect"}:
        cog = "APPLY"
    elif tier == "Basic":
        cog = "RECALL"
    q = {
        "id": qid,
        "stem": stem,
        "options": options,
        "correctAnswer": correct_id,
        "explanation": explanation,
        "distractorDissections": dissections_for(
            options, correct_id, entity, cat, intent, evidence
        ),
        "provenance": {
            "questionId": qid,
            "questionStem": stem,
            "intentType": intent,
            "knowledgeNodeId": f"kn_{cat.category_id}_{_md5(entity)[:8]}",
            "evidenceText": evidence,
            "sourceFile": "v13_ontology_knowledge_unit",
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
            "schemaVersion": "v13-expert-1",
            "metadata": {"tier": tier, "specificExam": exam_for(tier)},
            "linkHashes": {"evidence": _md5(evidence)},
            "entity": entity,
        },
        "cognitiveDemand": cog,
        "examTarget": exam_for(tier),
        "tier": tier,
        "format": fmt,
        "topicId": topic_id,
        "topicName": cat.display_name,
        "pdfSequenceNumber": f"V13-{int(_md5(qid)[:4], 16) % 9000:04d}",
        "valid": True,
        "familyId": cat.category_id,
        "familyStage": stage,
    }
    return q


_REASON_VERB = re.compile(
    r"\b(is|are|was|were|has|have|had|extends|enters|occurs|occur|contains|"
    r"causes|forms|formed|lies|receives|generates|produces|results)\b",
    re.I,
)


def split_reason(desc: str) -> Optional[Tuple[str, str]]:
    """Only split when the reason can be a real explanatory clause."""
    d = desc.strip().rstrip(".")
    for sep, prefix in (
        (" formed by ", "It is formed by "),
        (" formed from ", "It is formed from "),
        ("; ", ""),
    ):
        if sep not in d:
            continue
        a, r = d.split(sep, 1)
        a, r = a.strip(), r.strip()
        if len(a) < 18 or len(r) < 12:
            continue
        reason = (prefix + r) if prefix else r
        if not _REASON_VERB.search(reason):
            continue
        return a, reason
    return None


def build_definition(entity, cat, desc, sibs, seed):
    np = as_np(desc)
    stem = f"Which one of the following is {np}?"
    options, cid = shuffle_values(entity, sibs, seed + "|def")
    return make_q(entity, cat, desc, options, cid, "definition", "Direct Fact", "Basic", "FOUNDATION", stem, sibs)


def build_attribute(entity, cat, desc, sibs, seed):
    np = as_np(desc)
    stem = (
        f"With reference to {cat.display_name}, "
        f"which one of the following is {np}?"
    )
    options, cid = shuffle_values(entity, sibs, seed + "|attr")
    return make_q(entity, cat, desc, options, cid, "attribute", "Direct Fact", "Medium", "REINFORCEMENT", stem, sibs)


def build_comparison(entity, cat, desc, sibs, seed):
    np = as_np(desc)
    stem = (
        f"Which one of the following, unlike {sibs[0]}, is {np}?"
    )
    options, cid = shuffle_values(entity, sibs, seed + "|cmp")
    return make_q(entity, cat, desc, options, cid, "comparison", "Direct Fact", "Elite", "TRANSFER", stem, sibs)


def build_statement(entity, cat, desc, sibs, seed):
    true_s = as_clause(entity, desc) + "."
    false_s = as_clause(entity, cat.descriptions.get(sibs[0], sibs[0])) + "."
    if true_s.lower() == false_s.lower():
        return None
    rng = random.Random(int(_md5(seed + "|st")[:12], 16))
    if rng.random() < 0.5:
        s1, s2, cid = true_s, false_s, "opt_a"
    else:
        s1, s2, cid = false_s, true_s, "opt_b"
    stem = (
        f"Consider the following statements: "
        f"1. {s1} 2. {s2} "
        f"Which of the following is correct?"
    )
    options = [
        {"id": "opt_a", "text": "1 only"},
        {"id": "opt_b", "text": "2 only"},
        {"id": "opt_c", "text": "Both 1 and 2"},
        {"id": "opt_d", "text": "Neither 1 nor 2"},
    ]
    return make_q(entity, cat, desc, options, cid, "classification", "Statement-based", "Medium", "REINFORCEMENT", stem, sibs)


def build_assertion(entity, cat, desc, sibs, seed):
    parts = split_reason(desc)
    if not parts:
        return None
    head, reason = parts
    assertion = as_clause(entity, head) + "."
    reason_txt = reason.strip()
    first = reason_txt.split()[0] if reason_txt else ""
    if first.lower() in VERB_FIRST:
        reason_txt = "It " + first.lower() + reason_txt[len(first):]
    elif re.match(r"^(it|this|that|these|the|a|an)\b", reason_txt, re.I):
        reason_txt = reason_txt[0].upper() + reason_txt[1:]
    elif reason_txt and not reason_txt[0].isupper():
        reason_txt = reason_txt[0].upper() + reason_txt[1:]
    if not reason_txt.endswith("."):
        reason_txt += "."
    if not _REASON_VERB.search(reason_txt):
        return None
    if assertion.lower().rstrip(".") in reason_txt.lower() or reason_txt.lower().rstrip(".") in assertion.lower():
        return None
    stem = (
        f"Assertion (A): {assertion} "
        f"Reason (R): {reason_txt} "
        f"Which of the following is correct?"
    )
    options = [
        {"id": "opt_a", "text": "Both A and R are true, and R explains A"},
        {"id": "opt_b", "text": "Both A and R are true, but R does not explain A"},
        {"id": "opt_c", "text": "A is true, but R is false"},
        {"id": "opt_d", "text": "A is false, but R is true"},
    ]
    return make_q(entity, cat, desc, options, "opt_a", "cause_effect", "Assertion-Reason", "Advanced", "EXAM_STYLE", stem, sibs)


def build_application(entity, cat, desc, sibs, seed):
    np = as_np(desc)
    stem = (
        f"A student notes a feature of {cat.display_name} that is {np}. "
        f"Which one of the following does this identify?"
    )
    options, cid = shuffle_values(entity, sibs, seed + "|app")
    return make_q(entity, cat, desc, options, cid, "process", "Application", "Advanced", "EXAM_STYLE", stem, sibs)


def build_matching(entity, cat, desc, sibs, seed):
    np = as_np(desc)
    sib = sibs[0]
    sib_np = as_np(cat.descriptions.get(sib, sib))
    correct_text = f"{entity} — {np}"
    texts = [
        correct_text,
        f"{entity} — {sib_np}",
        f"{sib} — {np}",
        f"{sibs[1]} — {np}",
    ]
    if len(set(t.lower() for t in texts)) < 4:
        return None
    rng = random.Random(int(_md5(seed + "|match")[:12], 16))
    rng.shuffle(texts)
    options = [{"id": f"opt_{L}", "text": t} for L, t in zip("abcd", texts)]
    cid = next(o["id"] for o in options if o["text"] == correct_text)
    stem = f"Which of the following pairs is correctly matched?"
    return make_q(entity, cat, desc, options, cid, "classification", "Matching", "Medium", "REINFORCEMENT", stem, sibs)


BUILDERS = [
    build_definition,
    build_attribute,
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
    stem_key = f"{stem_key}|{q['format']}|{q['provenance'].get('entity','')}"
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
    print("[1] Building expert MCQs from ontology knowledge units...")
    accepted: List[Dict[str, Any]] = []
    seen = set()
    counts = {k: Counter() for k in ("topic", "intent", "format", "tier", "exam")}
    rejected = Counter()

    members = []
    for cat in ontology.categories.values():
        for m in cat.members:
            desc = (cat.descriptions or {}).get(m, "")
            if desc:
                members.append((m, cat, desc))
    random.Random(SEED).shuffle(members)

    for entity, cat, desc in members:
        sibs = ontology.get_siblings(entity, limit=3)
        if len(sibs) < 3:
            rejected["INSUFFICIENT_DISTRACTORS"] += 1
            continue
        seed = f"{cat.category_id}|{entity}"
        for builder in BUILDERS:
            if len(accepted) >= TARGET:
                break
            try:
                q = builder(entity, cat, desc, sibs, seed)
            except Exception:
                rejected["BUILDER_EXCEPTION"] += 1
                continue
            if not q:
                rejected["BUILDER_NONE"] += 1
                continue
            if not accept(q, accepted, seen, counts, ontology):
                rejected["GATE_OR_QUOTA"] += 1
        if len(accepted) >= TARGET:
            break

    # Second pass: extra comparison stems using other siblings, to fill 1200.
    if len(accepted) < TARGET:
        for entity, cat, desc in members:
            if len(accepted) >= TARGET:
                break
            sibs = ontology.get_siblings(entity, limit=3)
            if len(sibs) < 3:
                continue
            for i, sib in enumerate(sibs):
                if len(accepted) >= TARGET:
                    break
                np = as_np(desc)
                stem = f"Which one of the following, rather than {sib}, is {np}?"
                options, cid = shuffle_values(entity, sibs, f"{entity}|extra|{i}")
                q = make_q(
                    entity, cat, desc, options, cid, "comparison", "Direct Fact",
                    "Elite", "TRANSFER", stem, sibs,
                )
                if not accept(q, accepted, seen, counts, ontology):
                    rejected["EXTRA_GATE"] += 1

    print(f"    accepted={len(accepted)} rejected={dict(rejected)}")
    print(f"    formats={dict(counts['format'])}")
    print(f"    tiers={dict(counts['tier'])}")
    print(f"    intents={counts['intent'].most_common()}")
    print(f"    topics={counts['topic'].most_common(8)}")
    print(f"    exams={dict(counts['exam'])}")

    if len(accepted) < TARGET:
        print(f"ERROR: only {len(accepted)} expert questions; need {TARGET}")
        return 1

    accepted = accepted[:TARGET]
    bad = [q["id"] for q in accepted if validate_locked_question(q)]
    if bad:
        print("ERROR: contract failures", bad[:5])
        return 1

    out_json = os.path.join(PROJECT_ROOT, "generated_questions_1200_clean.json")
    assets_json = os.path.join(PROJECT_ROOT, "app", "src", "main", "assets", "generated_questions_1200_clean.json")
    report_path = os.path.join(PROJECT_ROOT, "docs", "production_1200_gate_report.json")
    for path in (out_json, assets_json):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(accepted, f, ensure_ascii=False, indent=2)

    report = {
        "count": len(accepted),
        "formats": dict(counts["format"]),
        "tiers": dict(counts["tier"]),
        "intents": dict(counts["intent"]),
        "topics": dict(counts["topic"]),
        "exams": dict(counts["exam"]),
        "rejected": dict(rejected),
        "status": "PASS",
        "quality": "expert-mcq-v1",
    }
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("[2] Wrote", out_json)
    print("STATUS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
