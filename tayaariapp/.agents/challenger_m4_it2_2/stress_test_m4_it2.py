#!/usr/bin/env python3
"""
.agents/challenger_m4_it2_2/stress_test_m4_it2.py
=================================================
Empirical Stress-Test Harness for Milestone 4 Iteration 2 Challenger:
1. Synthesize 100 questions from source-material/geography_extracted.txt:
   - 100% unique stems
   - 0% stem leakage
   - balanced option distribution
   - 0 quotation marks
   - 4 options per question
2. Provenance audit:
   - run audit_provenance_integrity on the 100 questions
   - verify 100% integrity rate (both structural/crypto and verbatim grounding)
3. Cryptographic tamper test:
   - verify 1-token mutation is caught across all 6 links
4. Room DB markdown parsing:
   - verify Explanation: precedes Correct Answer:
   - verify 'Option (X) is correct.' format
   - verify zero character truncation with DataImporter parsing rules.
"""

import os
import sys
import re
import json
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    DistractorVerificationGate,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    audit_provenance_integrity,
    verify_provenance_chain,
)
from tests.e2e.test_helpers import DataImporterSimulator

def run_empirical_stress_test():
    print("=" * 80)
    print("STARTING EMPIRICAL CHALLENGER M4 ITERATION 2 STRESS TEST")
    print("=" * 80)

    corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_corpus_text = f.read()

    normalizer = DocumentNormalizer()
    blocks = normalizer.normalize(corpus_path, raw_corpus_text)
    combined_normalized_text = "\n\n".join(b.text for b in blocks)

    # =========================================================================
    # 1. Scale Synthesis: Harvest 100 questions from real corpus
    # =========================================================================
    print("\n[STEP 1] Synthesizing 100 questions from real corpus...")
    synthesizer = QuestionSynthesizer()
    questions = synthesizer.synthesize_from_corpus(corpus_path, min_questions=100)
    total_q = len(questions)
    print(f"Synthesized {total_q} questions (Target >= 100).")
    assert total_q >= 100, f"Expected >= 100 questions, got {total_q}"

    # 1.1 Verify 100% Unique Stems
    print("\n[STEP 1.1] Verifying 100% unique stems...")
    stems_seen = set()
    duplicate_stems = []
    for idx, q in enumerate(questions):
        norm_stem = re.sub(r'\s+', ' ', q.stem.strip().lower())
        if norm_stem in stems_seen:
            duplicate_stems.append((idx, q.id, q.stem))
        stems_seen.add(norm_stem)

    unique_stems_count = len(stems_seen)
    stem_uniqueness_rate = unique_stems_count / total_q
    print(f"Unique stems: {unique_stems_count}/{total_q} ({stem_uniqueness_rate:.1%})")
    assert len(duplicate_stems) == 0, f"Found duplicate stems: {duplicate_stems}"

    # 1.2 Verify 0% Stem Leakage
    print("\n[STEP 1.2] Verifying 0% stem leakage...")
    leakage_failures = []
    gate_failures = []
    for idx, q in enumerate(questions):
        gate_ok, gate_errs = DistractorVerificationGate.verify_all(
            options=q.options,
            correct_key=q.correctAnswer,
            stem=q.stem,
            category=None
        )
        if not gate_ok:
            gate_failures.append((idx, q.id, gate_errs))

        clue_ok, clue_errs = DistractorVerificationGate.check_absence_of_clueing(
            options=q.options,
            correct_key=q.correctAnswer,
            stem=q.stem
        )
        if not clue_ok:
            leakage_failures.append((idx, q.id, clue_errs))

    print(f"Gate failures: {len(gate_failures)}/{total_q}")
    print(f"Stem leakage failures: {len(leakage_failures)}/{total_q}")
    assert len(leakage_failures) == 0, f"Stem leakage detected in: {leakage_failures}"
    assert len(gate_failures) == 0, f"Verification gate violations in: {gate_failures}"

    # 1.3 Verify Balanced Option Distribution
    print("\n[STEP 1.3] Verifying balanced option distribution...")
    ans_dist = Counter()
    for q in questions:
        letter = q.correctAnswer.replace("opt_", "").lower()
        ans_dist[letter] += 1

    print("Answer distribution across 100 questions:")
    for l in sorted(['a', 'b', 'c', 'd']):
        cnt = ans_dist[l]
        pct = cnt / total_q
        print(f"  Option ({l.upper()}): {cnt} ({pct:.1%})")
        assert cnt > 0, f"Option {l} was never assigned as correct answer"
        assert pct < 0.50, f"Option {l} dominates with {pct:.1%} (> 50%)"

    # 1.4 Verify 0 Quotation Marks
    print("\n[STEP 1.4] Verifying 0 quotation marks...")
    quote_chars = ['"', "'", '“', '”', '`', '‘', '’']
    banned_patterns = [
        re.compile(r'(?i)what is a direct consequence of\s*["\']'),
        re.compile(r'(?i)which of the following is true regarding\s*["\']'),
        re.compile(r'(?i)consider the following statement\s*["\']'),
        re.compile(r'(?i)according to the passage'),
        re.compile(r'(?i)as stated in the text'),
        re.compile(r'(?i)based on the quote'),
        re.compile(r'(?i)from the provided paragraph'),
        re.compile(r'(?i)refer to the excerpt'),
    ]
    quote_violations = []
    banned_violations = []

    for idx, q in enumerate(questions):
        for qc in quote_chars:
            if qc in q.stem:
                quote_violations.append((idx, q.id, "stem", qc, q.stem))
            for opt_k, opt_v in q.options.items():
                if qc in opt_v:
                    quote_violations.append((idx, q.id, f"option_{opt_k}", qc, opt_v))

        for bp in banned_patterns:
            if bp.search(q.stem):
                banned_violations.append((idx, q.id, bp.pattern, q.stem))

    print(f"Quotation mark violations: {len(quote_violations)}")
    print(f"Banned lazy template violations: {len(banned_violations)}")
    assert len(quote_violations) == 0, f"Quote violations found: {quote_violations[:5]}"
    assert len(banned_violations) == 0, f"Banned template violations found: {banned_violations[:5]}"

    # 1.5 Verify 4 Options per Question
    print("\n[STEP 1.5] Verifying 4 options per question...")
    option_count_violations = []
    placeholder_violations = []
    for idx, q in enumerate(questions):
        if set(q.options.keys()) != {'a', 'b', 'c', 'd'}:
            option_count_violations.append((idx, q.id, set(q.options.keys())))
        for opt_k, opt_v in q.options.items():
            if len(opt_v.strip()) < 2:
                placeholder_violations.append((idx, q.id, opt_k, opt_v))

    print(f"Option count violations: {len(option_count_violations)}")
    print(f"Placeholder option violations: {len(placeholder_violations)}")
    assert len(option_count_violations) == 0, f"Option count violations: {option_count_violations}"
    assert len(placeholder_violations) == 0, f"Placeholder violations: {placeholder_violations}"

    # =========================================================================
    # 2. Provenance Audit
    # =========================================================================
    print("\n[STEP 2] Running audit_provenance_integrity on all 100 questions...")
    records = [q.provenance for q in questions]

    # 2.1 Audit Schema & Cryptographic Integrity
    audit_res_crypto = audit_provenance_integrity(records)
    print(f"Crypto Audit Total Records: {audit_res_crypto['total_records']}")
    print(f"Crypto Audit Valid Records: {audit_res_crypto['valid_records']}")
    print(f"Crypto Audit Invalid Records: {audit_res_crypto['invalid_records']}")
    print(f"Crypto Audit Tampered Records: {audit_res_crypto['tampered_records']}")
    print(f"Crypto Audit Integrity Rate: {audit_res_crypto['integrity_rate']:.1%}")
    print(f"Crypto Audit Verdict: {audit_res_crypto['audit_verdict']}")

    assert audit_res_crypto["total_records"] == total_q
    assert audit_res_crypto["valid_records"] == total_q
    assert audit_res_crypto["invalid_records"] == 0
    assert audit_res_crypto["tampered_records"] == 0
    assert audit_res_crypto["integrity_rate"] == 1.0
    assert audit_res_crypto["audit_verdict"] == "PASS"

    # 2.2 Audit Verbatim Grounding Against Corpus
    corpus_dict = {
        corpus_path: combined_normalized_text,
        "geography_extracted.txt": combined_normalized_text
    }
    audit_res_grounding = audit_provenance_integrity(records, source_corpus=corpus_dict)
    print(f"Grounding Audit Total Records: {audit_res_grounding['total_records']}")
    print(f"Grounding Audit Valid Records: {audit_res_grounding['valid_records']}")
    print(f"Grounding Audit Invalid Records: {audit_res_grounding['invalid_records']}")
    print(f"Grounding Audit Grounding Failures: {audit_res_grounding['grounding_failures']}")
    print(f"Grounding Audit Integrity Rate: {audit_res_grounding['integrity_rate']:.1%}")
    print(f"Grounding Audit Verdict: {audit_res_grounding['audit_verdict']}")

    assert audit_res_grounding["total_records"] == total_q
    assert audit_res_grounding["valid_records"] == total_q
    assert audit_res_grounding["invalid_records"] == 0
    assert audit_res_grounding["grounding_failures"] == 0
    assert audit_res_grounding["integrity_rate"] == 1.0
    assert audit_res_grounding["audit_verdict"] == "PASS"

    # =========================================================================
    # 3. Cryptographic Tamper Test: 1-Token Mutation across all 6 Links
    # =========================================================================
    print("\n[STEP 3] Cryptographic Tamper Test across all 6 Merklized links...")
    links_to_test = [
        ("Link 1: questionStem", "questionStem", lambda val: val[:-1] + ("!" if not val.endswith("!") else "?")),
        ("Link 1: questionId", "questionId", lambda val: val + "_mutated"),
        ("Link 2: intentType", "intentType", lambda val: "process" if val != "process" else "definition"),
        ("Link 3: knowledgeNodeId", "knowledgeNodeId", lambda val: val + "_mutated"),
        ("Link 4: evidenceText", "evidenceText", lambda val: val + " [TAMPER]"),
        ("Link 5: sourceFile", "sourceFile", lambda val: "tampered_source.txt"),
        ("Link 6: sourceLocation", "sourceLocation", lambda val: {**val, "offset": val.get("offset", 0) + 5}),
    ]

    for link_desc, link_key, mutate_fn in links_to_test:
        tampered_records = []
        for r in records:
            t = json.loads(json.dumps(r))
            orig_val = t.get(link_key, {})
            t[link_key] = mutate_fn(orig_val)
            tampered_records.append(t)

        audit_tamper = audit_provenance_integrity(tampered_records)
        tampered_cnt = audit_tamper["tampered_records"]
        invalid_cnt = audit_tamper["invalid_records"]
        valid_cnt = audit_tamper["valid_records"]
        print(f"  Tamper Test [{link_desc}]: {tampered_cnt}/{total_q} flagged tampered, {invalid_cnt}/{total_q} invalid, {valid_cnt} evaded.")
        assert valid_cnt == 0, f"Tamper evasion detected on {link_desc}: {valid_cnt} passed!"
        assert tampered_cnt == total_q, f"Not all records flagged as tampered on {link_desc}: {tampered_cnt}/{total_q}"
        assert audit_tamper["audit_verdict"] == "REJECT"

    # =========================================================================
    # 4. Room DB Markdown Parsing: DataImporter.kt parsing rules
    # =========================================================================
    print("\n[STEP 4] Room DB Markdown Parsing and DataImporter.kt verification...")
    order_violations = []
    format_violations = []
    truncation_failures = []

    for idx, q in enumerate(questions):
        md = q.to_room_markdown()
        exp_pos = md.find("Explanation:")
        ans_pos = md.find("Correct Answer:")

        # 4.1 Explanation: precedes Correct Answer:
        if exp_pos == -1 or ans_pos == -1 or exp_pos > ans_pos:
            order_violations.append((idx, q.id, exp_pos, ans_pos))

        # 4.2 'Option (X) is correct.' format
        correct_letter = q.correctAnswer.replace("opt_", "").upper()
        expected_prefix = f"Option ({correct_letter}) is correct."
        if not q.explanation.strip().startswith(expected_prefix):
            format_violations.append((idx, q.id, q.explanation[:40], expected_prefix))

        # 4.3 Sequential regex parsing simulation
        q_fence_match = re.search(r'- \*\*Question\*\*:\s*```\s*(.*?)\s*```', md, re.DOTALL)
        assert q_fence_match is not None, f"Failed to match code fence in Q {q.id}"
        raw_q_text = q_fence_match.group(1).strip()

        # Step A: DataImporter.kt Correct Answer regex
        ans_match = re.search(r'(?i)Correct [Aa]nswer:\s*(?:Option\s*)?([a-eA-E])', raw_q_text)
        assert ans_match is not None, f"Correct Answer match failed for Q {q.id}"
        parsed_ans = f"opt_{ans_match.group(1).lower().strip()}"
        assert parsed_ans == q.correctAnswer

        # Step B: DataImporter.kt slice before Correct Answer
        raw_q_text = raw_q_text[:ans_match.start()].strip()

        # Step C: DataImporter.kt Explanation regex
        exp_match = re.search(r'(?i)Explanation:\s*(.*)', raw_q_text, re.DOTALL)
        assert exp_match is not None, f"Explanation match failed for Q {q.id}"
        extracted_exp = exp_match.group(1).strip()

        # Step D: Verify zero character truncation
        if extracted_exp != q.explanation.strip():
            truncation_failures.append({
                "id": q.id,
                "expected": q.explanation.strip(),
                "extracted": extracted_exp,
                "expected_len": len(q.explanation.strip()),
                "extracted_len": len(extracted_exp)
            })

    print(f"Explanation-before-Answer order violations: {len(order_violations)}")
    print(f"'Option (X) is correct.' format violations: {len(format_violations)}")
    print(f"DataImporter explanation truncation failures: {len(truncation_failures)}")

    assert len(order_violations) == 0, f"Order violations: {order_violations}"
    assert len(format_violations) == 0, f"Format violations: {format_violations}"
    assert len(truncation_failures) == 0, f"Truncation failures: {truncation_failures}"

    # 4.4 Full DataImporterSimulator multi-question parsing test
    print("\n[STEP 4.4] Full DataImporterSimulator multi-question parsing test...")
    full_md = "## 1. Physical Geography\n" + "\n".join(q.to_room_markdown() for q in questions)
    parse_result = DataImporterSimulator.parse_markdown(full_md)

    print(f"DataImporterSimulator Found: {parse_result['totalFound']}")
    print(f"DataImporterSimulator Accepted: {parse_result['totalAccepted']}")
    print(f"DataImporterSimulator Rejected: {parse_result['totalRejected']}")

    assert parse_result["totalFound"] == total_q
    assert parse_result["totalAccepted"] == total_q
    assert parse_result["totalRejected"] == 0
    assert len(parse_result["rejections"]) == 0

    print("\n" + "=" * 80)
    print("ALL EMPIRICAL ADVERSARIAL STRESS TESTS PASSED WITH 100% INTEGRITY!")
    print("=" * 80)

if __name__ == "__main__":
    run_empirical_stress_test()
