#!/usr/bin/env python3
"""
Forensic Audit Verification Script for Milestone 4 Iteration 2
Authored by: auditor_m4_it2_1
Working directory: c:/Users/harsh/Downloads/tayaari/tayaariapp/.agents/auditor_m4_it2_1/
"""

import sys
import os
import re
import hashlib
import json
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    DistractorVerificationGate,
    NaturalStemSynthesizer,
    DistractorDissector,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    ProvenanceTracker,
    verify_provenance_chain,
    audit_provenance_integrity,
    canonicalize_intent,
    _canonical_json,
    _sha256,
)
from v13_discovery.semantic_extractor import KnowledgeNode, SemanticExtractor
from v13_discovery.normalizer import DocumentNormalizer


def check_1_static_analysis():
    print("=== CHECK 1: STATIC ANALYSIS FOR BYPASS FLAGS & SYNTHETIC SHORTCUTS ===")
    target_files = [
        os.path.join(REPO_ROOT, "v13_discovery", "question_synthesizer.py"),
        os.path.join(REPO_ROOT, "tests", "test_v13_distractor_engine.py"),
    ]
    banned_tokens = ["skip_gate", "bypass", "mock", "fake"]
    violations = []
    
    for tf in target_files:
        with open(tf, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            for token in banned_tokens:
                if re.search(r'\b' + re.escape(token) + r'\b', line, re.IGNORECASE):
                    violations.append(f"{os.path.basename(tf)}:{idx} contains '{token}': {line.strip()}")
            # Also check 'dummy' specifically
            if re.search(r'\bdummy\b', line, re.IGNORECASE):
                # Is it part of placeholder detection regex?
                if "placeholder_regex" in line or "Dummy" in line:
                    pass  # Allowed: rejecting dummy values
                else:
                    violations.append(f"{os.path.basename(tf)}:{idx} contains 'dummy': {line.strip()}")

    print(f"Static Analysis Violations Found: {len(violations)}")
    for v in violations:
        print(f"  VIOLATION: {v}")
    return len(violations) == 0


def check_2_genuine_logic_adversarial_fixes():
    print("\n=== CHECK 2: GENUINE LOGIC VERIFICATION (5 ADVERSARIAL FIXES) ===")
    ontology = OntologyRegistry()
    synth = QuestionSynthesizer(ontology)
    results = {}

    # Fix 1: Targeted de-identification & valid attribute
    node_leaking = KnowledgeNode(
        node_id="adv_test_leak_01",
        intent_type="definition",
        primary_entity="Saptarishi",
        predicate="is defined as",
        secondary_entities=[],
        conditions=[],
        quantitative_data=None,
        raw_evidence="Saptarishi is defined as a group of seven sages forming Ursa Major.",
        source_location={"sourceId": "test.txt", "line": 10, "offset": 0},
        confidence=1.0
    )
    cq_leaking = synth.synthesize(node_leaking)
    leak_check, leak_errs = DistractorVerificationGate.check_absence_of_clueing(
        cq_leaking.options, cq_leaking.correctAnswer, cq_leaking.stem
    )
    fix1_pass = cq_leaking.valid and leak_check and ("saptarishi" not in cq_leaking.stem.lower())
    results["fix_1_targeted_deid"] = {
        "pass": fix1_pass,
        "stem": cq_leaking.stem,
        "correct": cq_leaking.options[cq_leaking.correctAnswer.replace("opt_", "")],
        "cq_valid": cq_leaking.valid,
        "leak_check": leak_check
    }
    print(f"Fix 1 (De-identification & cq.valid): {'PASS' if fix1_pass else 'FAIL'}")
    print(f"  Stem: {cq_leaking.stem}")

    # Fix 2: Stem-terminal indefinite article detection
    options = {"a": "Oxbow lake", "b": "Cirque", "c": "Moraine", "d": "Delta"}
    failing_stems = [
        "Which fluvial process creates an?",
        "Which geological feature represents a?",
        "In Earth science, this structure forms an:",
        "Which natural formation constitutes a?",
        "Which of the following is an?",
        "Which feature is called a?",
    ]
    passing_stems = [
        "Which feature is prominent in this area?",
        "Which of the following describes the phenomena?",
        "In Earth science, what is this landform called?",
    ]
    fix2_caught_all = True
    for s in failing_stems:
        v, err = DistractorVerificationGate.check_grammatical_fit(options, s)
        if v:
            fix2_caught_all = False
            print(f"  Fix 2 FAILED to catch: {s}")
    fix2_passed_clean = True
    for s in passing_stems:
        v, err = DistractorVerificationGate.check_grammatical_fit(options, s)
        if not v:
            fix2_passed_clean = False
            print(f"  Fix 2 FALSE POSITIVE on: {s} -> {err}")
    fix2_pass = fix2_caught_all and fix2_passed_clean
    results["fix_2_stem_terminal_article"] = {"pass": fix2_pass, "caught_all": fix2_caught_all, "clean_pass": fix2_passed_clean}
    print(f"Fix 2 (Stem-terminal article cluing): {'PASS' if fix2_pass else 'FAIL'}")

    # Fix 3: Short 3-letter entity leakage
    short_entities = ["Fog", "Ice", "Sun", "Ore", "Mud", "Ash"]
    fix3_caught_all = True
    for se in short_entities:
        stem = f"Which natural phenomenon known as {se.lower()} occurs here?"
        opts = {"a": se, "b": "Granite", "c": "Basalt", "d": "Shale"}
        v, err = DistractorVerificationGate.check_absence_of_clueing(opts, "opt_a", stem)
        if v:
            fix3_caught_all = False
            print(f"  Fix 3 FAILED to catch 3-letter entity '{se}' in: {stem}")
    # Substring false positive test
    safe_stem = "Which surface feature formed before the ice age represents this rock?"
    opts_no_ice = {"a": "Ore", "b": "Granite", "c": "Basalt", "d": "Shale"}
    v_no_ice, err_no_ice = DistractorVerificationGate.check_absence_of_clueing(opts_no_ice, "opt_a", safe_stem)
    fix3_no_false_positive = v_no_ice
    fix3_pass = fix3_caught_all and fix3_no_false_positive
    results["fix_3_short_entity_leakage"] = {"pass": fix3_pass, "caught_all": fix3_caught_all, "no_false_positives": fix3_no_false_positive}
    print(f"Fix 3 (Short-entity stem leakage): {'PASS' if fix3_pass else 'FAIL'}")

    # Fix 4: Synthetic placeholder detection
    placeholders = [
        "Option 1", "Option 2", "Option A", "Option B",
        "Alternative 1", "Alternative A",
        "Choice A", "Choice 1",
        "All of the above", "None of the above", "None",
        "N/A", "NA", "TBD", "Placeholder", "Unknown",
        "Dummy", "Sample", "Test Option"
    ]
    fix4_caught_all = True
    for ph in placeholders:
        opts = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": ph}
        v, err = DistractorVerificationGate.check_semantic_plausibility(opts)
        if v:
            fix4_caught_all = False
            print(f"  Fix 4 FAILED to catch placeholder '{ph}'")
    results["fix_4_placeholder_detection"] = {"pass": fix4_caught_all}
    print(f"Fix 4 (Placeholder detection): {'PASS' if fix4_caught_all else 'FAIL'}")

    # Fix 5: Ontology multi-category collision resolution
    hadley_cat = ontology.find_category_for_entity("Hadley cell")
    hadley_id = hadley_cat.category_id if hadley_cat else None
    clim_cat = ontology.get_category("climatic_phenomena")
    clim_has_hadley = "hadley cell" in [m.lower() for m in clim_cat.members] if clim_cat else True
    fluvial_cat = ontology.get_category("fluvial_landforms")
    fluvial_members = [m.lower() for m in fluvial_cat.members] if fluvial_cat else []
    fluvial_clean = ("cirque" not in fluvial_members) and ("moraine" not in fluvial_members) and ("mushroom rock" not in fluvial_members)
    cirque_cat = ontology.find_category_for_entity("Cirque")
    moraine_cat = ontology.find_category_for_entity("Moraine")
    mushroom_cat = ontology.find_category_for_entity("Mushroom rock")
    fix5_pass = (
        hadley_id == "circulation_cells" and
        not clim_has_hadley and
        fluvial_clean and
        cirque_cat.category_id == "glacial_landforms" and
        moraine_cat.category_id == "glacial_landforms" and
        mushroom_cat.category_id == "aeolian_landforms"
    )
    results["fix_5_ontology_purity"] = {
        "pass": fix5_pass,
        "hadley_id": hadley_id,
        "clim_has_hadley": clim_has_hadley,
        "fluvial_clean": fluvial_clean
    }
    print(f"Fix 5 (Ontology category purity): {'PASS' if fix5_pass else 'FAIL'}")

    all_fixes_pass = all(r["pass"] for r in results.values())
    return all_fixes_pass, results


def check_3_filtering_cq_valid():
    print("\n=== CHECK 3: FILTERING VERIFICATION OF cq.valid IN synthesize_from_corpus() ===")
    corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
    normalizer = DocumentNormalizer()
    extractor = SemanticExtractor()
    with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    blocks = normalizer.normalize(corpus_path, text)
    raw_nodes = []
    for b in blocks:
        raw_nodes.extend(extractor.extract(b))
    
    print(f"Total raw KnowledgeNodes extracted: {len(raw_nodes)}")
    
    synth = QuestionSynthesizer()
    valid_count = 0
    invalid_count = 0
    stem_leak_count = 0
    gate_fail_count = 0

    for node in raw_nodes[:200]:
        ent = (getattr(node, "primary_entity", "") or "").strip()
        ev = (getattr(node, "raw_evidence", "") or "").strip()
        if len(ent) < 3 or len(ev) < 20:
            continue
        try:
            cq = synth.synthesize(node, shuffle=True)
            if not cq.valid:
                invalid_count += 1
            else:
                valid_count += 1
            g_pass, _ = DistractorVerificationGate.verify_all(cq.options, cq.correctAnswer, cq.stem, None)
            if not g_pass:
                gate_fail_count += 1
            l_pass, _ = DistractorVerificationGate.check_absence_of_clueing(cq.options, cq.correctAnswer, cq.stem)
            if not l_pass:
                stem_leak_count += 1
        except Exception:
            pass

    print(f"Unfiltered Sample (first 200 nodes):")
    print(f"  Valid: {valid_count}, Invalid: {invalid_count}")
    print(f"  Gate failures: {gate_fail_count}, Stem leakage failures: {stem_leak_count}")

    # Now verify synthesize_from_corpus filtering
    synthesized_100 = synth.synthesize_from_corpus(corpus_path, min_questions=100)
    print(f"Synthesized from corpus with filtering: {len(synthesized_100)} questions")
    
    corpus_invalid = [q for q in synthesized_100 if not q.valid]
    corpus_gate_fails = [q for q in synthesized_100 if not DistractorVerificationGate.verify_all(q.options, q.correctAnswer, q.stem, None)[0]]
    corpus_stem_leaks = [q for q in synthesized_100 if not DistractorVerificationGate.check_absence_of_clueing(q.options, q.correctAnswer, q.stem)[0]]

    print(f"Corpus Batch Audit Results:")
    print(f"  Invalid questions emitted: {len(corpus_invalid)} / {len(synthesized_100)}")
    print(f"  Gate failures emitted: {len(corpus_gate_fails)} / {len(synthesized_100)}")
    print(f"  Stem leakages emitted: {len(corpus_stem_leaks)} / {len(synthesized_100)}")

    pass_check = (len(corpus_invalid) == 0 and len(corpus_gate_fails) == 0 and len(corpus_stem_leaks) == 0 and len(synthesized_100) >= 100)
    return pass_check, len(synthesized_100), len(corpus_invalid), len(corpus_stem_leaks)


def check_4_cryptographic_integrity():
    print("\n=== CHECK 4: CRYPTOGRAPHIC INTEGRITY OF 6-LINK MERKLIZED SHA-256 DIGESTS ===")
    corpus_path = os.path.abspath(os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt"))
    with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()
    normalizer = DocumentNormalizer()
    blocks = normalizer.normalize(corpus_path, raw_text)
    normalized_text = blocks[0].text if blocks else raw_text

    synth = QuestionSynthesizer()
    questions = synth.synthesize_from_corpus(corpus_path, min_questions=50)

    # 1. Verify batch integrity via audit_provenance_integrity with normalized text
    batch_records = [q.provenance for q in questions]
    corpus_dict = {
        corpus_path: normalized_text,
        "geography_extracted.txt": normalized_text
    }
    audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)
    print(f"Audit Provenance Integrity Result:")
    print(f"  Total records: {audit_res['total_records']}")
    print(f"  Valid records: {audit_res['valid_records']}")
    print(f"  Invalid records: {audit_res['invalid_records']}")
    print(f"  Tampered records: {audit_res['tampered_records']}")
    print(f"  Integrity rate: {audit_res['integrity_rate'] * 100:.2f}%")
    print(f"  Audit verdict: {audit_res['audit_verdict']}")

    # 2. Independently verify all 6 Merklized links on all questions
    link_names = ["location_hash", "source_hash", "evidence_hash", "unit_hash", "intent_hash", "question_hash"]
    all_chains_valid = True
    for q in questions:
        p = q.provenance
        lh = p.get("linkHashes", {})
        
        can_loc = _canonical_json(p.get("sourceLocation", {}))
        clean_src = (p.get("sourceFile") or "").strip()
        clean_ev = (p.get("evidenceText") or "").strip()
        clean_knid = (p.get("knowledgeNodeId") or "").strip()
        can_intent = canonicalize_intent(p.get("intentType") or "")
        clean_qid = (p.get("questionId") or "").strip()
        clean_stem = (p.get("questionStem") or "").strip()
        
        h_loc = _sha256(f"LINK6_LOC:{can_loc}")
        h_src = _sha256(f"LINK5_SRC:{clean_src}:{h_loc}")
        h_ev = _sha256(f"LINK4_EV:{clean_ev}:{h_src}")
        h_unit = _sha256(f"LINK3_UNIT:{clean_knid}:{h_ev}")
        h_intent = _sha256(f"LINK2_INTENT:{can_intent}:{h_unit}")
        h_quest = _sha256(f"LINK1_QUEST:{clean_qid}:{clean_stem}:{h_intent}")
        
        if (h_loc != lh.get("location_hash") or
            h_src != lh.get("source_hash") or
            h_ev != lh.get("evidence_hash") or
            h_unit != lh.get("unit_hash") or
            h_intent != lh.get("intent_hash") or
            h_quest != lh.get("question_hash")):
            all_chains_valid = False
            break

    print(f"Independent 6-Link Merklized SHA-256 verification across 50 questions: {'PASS' if all_chains_valid else 'FAIL'}")
    
    # Display sample record links
    sample_lh = questions[0].provenance.get("linkHashes", {})
    for ln in link_names:
        print(f"  {ln}: {sample_lh.get(ln)}")

    # 3. Adversarial Tamper Detection Verification
    sample_prov = questions[0].provenance
    
    # Tamper with questionStem
    tampered_q_stem = dict(sample_prov)
    tampered_q_stem["questionStem"] = tampered_q_stem.get("questionStem", "") + " TAMPERED"
    v_stem = verify_provenance_chain(tampered_q_stem)
    print(f"Tamper test (mutated questionStem): Caught={not v_stem.is_valid}, Reason: {v_stem.errors}")

    # Tamper with evidenceText
    tampered_q_ev = dict(sample_prov)
    tampered_q_ev["evidenceText"] = tampered_q_ev.get("evidenceText", "") + " TAMPERED"
    v_ev = verify_provenance_chain(tampered_q_ev)
    print(f"Tamper test (mutated evidenceText): Caught={not v_ev.is_valid}, Reason: {v_ev.errors}")

    # Tamper with knowledgeNodeId
    tampered_q_node = dict(sample_prov)
    tampered_q_node["knowledgeNodeId"] = "TAMPERED_NODE_ID"
    v_node = verify_provenance_chain(tampered_q_node)
    print(f"Tamper test (mutated knowledgeNodeId): Caught={not v_node.is_valid}, Reason: {v_node.errors}")

    # Tamper with provenanceHash
    tampered_q_hash = dict(sample_prov)
    tampered_q_hash["provenanceHash"] = "0" * 64
    v_hash = verify_provenance_chain(tampered_q_hash)
    print(f"Tamper test (mutated provenanceHash): Caught={not v_hash.is_valid}, Reason: {v_hash.errors}")

    tamper_caught = (not v_stem.is_valid) and (not v_ev.is_valid) and (not v_node.is_valid) and (not v_hash.is_valid)
    crypto_pass = (audit_res["audit_verdict"] == "PASS" and all_chains_valid and tamper_caught)
    return crypto_pass, audit_res


def check_5_scale_synthesis_integrity():
    print("\n=== CHECK 5: SCALE SYNTHESIS INTEGRITY & 0% STEM LEAKAGE ===")
    corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
    synth = QuestionSynthesizer()
    questions = synth.synthesize_from_corpus(corpus_path, min_questions=100)
    print(f"Total questions synthesized: {len(questions)}")

    # 1. Stem uniqueness
    stems = [q.stem.strip().lower() for q in questions]
    unique_stems = set(stems)
    stem_uniqueness = len(unique_stems) / len(stems)
    print(f"Stem uniqueness: {len(unique_stems)} / {len(stems)} ({stem_uniqueness * 100:.1f}%)")

    # 2. Stem leakage check
    leaking_questions = []
    for idx, q in enumerate(questions, 1):
        is_valid, errs = DistractorVerificationGate.check_absence_of_clueing(
            options=q.options,
            correct_key=q.correctAnswer,
            stem=q.stem
        )
        if not is_valid:
            leaking_questions.append((idx, q.id, q.stem, q.correctAnswer, q.options[q.correctAnswer.replace("opt_", "")], errs))

    print(f"Stem leakage count: {len(leaking_questions)} / {len(questions)}")
    for lq in leaking_questions[:5]:
        print(f"  Leakage in Q#{lq[0]} ({lq[1]}): {lq[5]}")

    # 3. Anti-quotation check (NQ1-NQ5)
    lazy_pattern = re.compile(r'(?i)what is a direct consequence of|according to the passage|as stated in the text')
    quotation_pattern = re.compile(r'["\'“”]')
    lazy_matches = []
    quotation_matches = []
    for idx, q in enumerate(questions, 1):
        if lazy_pattern.search(q.stem):
            lazy_matches.append((idx, q.stem))
        if quotation_pattern.search(q.stem):
            quotation_matches.append((idx, q.stem))

    print(f"Lazy template matches: {len(lazy_matches)}")
    print(f"Quotation fragment matches: {len(quotation_matches)}")

    # 4. Distractor dissections check
    dissection_errors = []
    for idx, q in enumerate(questions, 1):
        correct_letter = q.correctAnswer.replace("opt_", "")
        if len(q.distractorDissections) != len(q.options) - 1:
            dissection_errors.append(f"Q#{idx} has {len(q.distractorDissections)} dissections, expected {len(q.options) - 1}")
        for d in q.distractorDissections:
            opt_id = d.get("optionId", "").replace("opt_", "")
            if opt_id == correct_letter:
                dissection_errors.append(f"Q#{idx} distractor dissection assigned to correct answer '{correct_letter}'")
            if d.get("trapType") not in VALID_ROOM_TRAP_TYPES:
                dissection_errors.append(f"Q#{idx} invalid trap type: {d.get('trapType')}")

    print(f"Dissection errors: {len(dissection_errors)}")

    scale_pass = (
        len(questions) >= 100 and
        len(unique_stems) >= 100 and
        len(leaking_questions) == 0 and
        len(lazy_matches) == 0 and
        len(quotation_matches) == 0 and
        len(dissection_errors) == 0
    )
    return scale_pass, len(questions), len(leaking_questions), stem_uniqueness


def check_6_room_db_serialization():
    print("\n=== CHECK 6: ROOM DB MARKDOWN SERIALIZATION INTEGRITY ===")
    synth = QuestionSynthesizer()
    corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")
    questions = synth.synthesize_from_corpus(corpus_path, min_questions=10)
    
    serialization_results = []
    for idx, q in enumerate(questions, 1):
        md = q.to_room_markdown()
        
        # 1. Explanation precedes Correct Answer inside code fence
        code_fence_match = re.search(r'```(.*?)```', md, re.DOTALL)
        if not code_fence_match:
            serialization_results.append(f"Q#{idx}: Missing code fence")
            continue
        fence_content = code_fence_match.group(1)
        
        exp_pos = fence_content.find("Explanation:")
        ans_pos = fence_content.find("Correct Answer:")
        if exp_pos == -1 or ans_pos == -1:
            serialization_results.append(f"Q#{idx}: Missing Explanation or Correct Answer inside fence")
            continue
        if exp_pos >= ans_pos:
            serialization_results.append(f"Q#{idx}: 'Correct Answer:' precedes 'Explanation:' (exp_pos={exp_pos}, ans_pos={ans_pos})")
            continue

        # 2. Explanation format: 'Option (X) is correct.'
        correct_letter = q.correctAnswer.replace("opt_", "").upper()
        expected_prefix = f"Option ({correct_letter}) is correct."
        if not q.explanation.startswith(expected_prefix):
            serialization_results.append(f"Q#{idx}: Explanation does not start with '{expected_prefix}': '{q.explanation[:40]}'")
            continue

        # 3. Simulate DataImporter.kt parsing logic verbatim
        # Regex from DataImporter.kt line 109
        ans_pattern = re.compile(r'(?i)Correct [Aa]nswer:\s*(?:Option\s*)?([a-eA-E])')
        raw_q_text = fence_content.strip()
        ans_m = ans_pattern.search(raw_q_text)
        if not ans_m:
            serialization_results.append(f"Q#{idx}: DataImporter ansMatcher failed")
            continue
        parsed_ans_letter = ans_m.group(1).lower().strip()
        raw_q_text_sliced = raw_q_text[:ans_m.start()].strip()

        # Regex from DataImporter.kt line 121
        exp_pattern = re.compile(r'(?i)Explanation:\s*(.*)', re.DOTALL)
        exp_m = exp_pattern.search(raw_q_text_sliced)
        if not exp_m:
            serialization_results.append(f"Q#{idx}: DataImporter expMatcher failed")
            continue
        parsed_explanation = exp_m.group(1).strip()
        raw_q_text_options = raw_q_text_sliced[:exp_m.start()].strip()

        # Regex from DataImporter.kt line 129
        options_pattern = re.compile(r'(?s)\s*\(?([a-eA-E])\)\s+(.*?)(?=\s*\(?[a-eA-E]\)\s+|$)')
        option_matches = options_pattern.findall(raw_q_text_options)

        if parsed_ans_letter != correct_letter.lower():
            serialization_results.append(f"Q#{idx}: Parsed answer letter '{parsed_ans_letter}' != expected '{correct_letter.lower()}'")
            continue
        if not parsed_explanation.startswith(expected_prefix):
            serialization_results.append(f"Q#{idx}: Parsed explanation truncated or corrupted: '{parsed_explanation[:40]}'")
            continue
        if len(option_matches) < 4:
            serialization_results.append(f"Q#{idx}: Parsed options count < 4: {len(option_matches)}")
            continue

    print(f"Serialization Errors: {len(serialization_results)}")
    for err in serialization_results:
        print(f"  {err}")

    # Show verbatim markdown of sample question
    sample_md = questions[0].to_room_markdown()
    print("\n--- Verbatim Room DB Markdown Output Sample ---")
    print(sample_md)
    print("------------------------------------------------")

    room_db_pass = (len(serialization_results) == 0)
    return room_db_pass, sample_md


if __name__ == "__main__":
    print("================================================================================")
    print("FORENSIC AUDIT: MILESTONE 4 ITERATION 2 DELIVERABLES")
    print("================================================================================")
    
    c1 = check_1_static_analysis()
    c2, r2 = check_2_genuine_logic_adversarial_fixes()
    c3, n_q, n_inv, n_leak = check_3_filtering_cq_valid()
    c4, audit_res = check_4_cryptographic_integrity()
    c5, n_scale, n_scale_leak, stem_uniq = check_5_scale_synthesis_integrity()
    c6, sample_md = check_6_room_db_serialization()

    print("\n================================================================================")
    print("AUDIT SUMMARY:")
    print(f"  Check 1 (Static Analysis / Zero Shortcuts): {'PASS' if c1 else 'FAIL'}")
    print(f"  Check 2 (Genuine Logic in 5 Fixes):         {'PASS' if c2 else 'FAIL'}")
    print(f"  Check 3 (Filtering cq.valid in Corpus):      {'PASS' if c3 else 'FAIL'}")
    print(f"  Check 4 (6-Link Merklized SHA-256 Crypto):  {'PASS' if c4 else 'FAIL'}")
    print(f"  Check 5 (Scale Synthesis & 0% Leakage):     {'PASS' if c5 else 'FAIL'}")
    print(f"  Check 6 (Room DB Markdown Serialization):   {'PASS' if c6 else 'FAIL'}")
    print("================================================================================")
    
    all_clean = c1 and c2 and c3 and c4 and c5 and c6
    print(f"OVERALL VERDICT: {'CLEAN' if all_clean else 'INTEGRITY VIOLATION'}")
    print("================================================================================")
    sys.exit(0 if all_clean else 1)
