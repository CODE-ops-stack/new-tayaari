# Adversarial Challenge & Stress-Test Handoff Report: Milestone 4 Distractor Engine

**Date**: 2026-09-06T17:15:00Z  
**Agent**: challenger_m4_1 (Empirical Challenger: critic, specialist)  
**Parent Orchestrator**: teamwork_preview_orchestrator_5 (`d497dcb5-7f26-4e7c-bd7e-8bd149a1669d`)  
**Verdict**: `REQUEST_CHANGES`

---

## 1. Observation

### 1.1 Baseline Test Suite Execution (Worker Claims Verification)

Independent execution of standard project test suites verified that all baseline tests currently pass:

#### Command 1: Milestone 4 Distractor Engine Unit Test Suite
```powershell
python -m unittest tests/test_v13_distractor_engine.py
```
**Output**:
```text
........................
----------------------------------------------------------------------
Ran 24 tests in 0.802s

OK
```

#### Command 2: End-to-End Test Suite
```powershell
python run_e2e_tests.py
```
**Output**:
```text
----------------------------------------------------------------------
Ran 202 tests in 1.359s

OK

==============================================================================
  E2E TEST EXECUTION SUMMARY
------------------------------------------------------------------------------
  Tier 1: Feature Coverage (16 Features)    : 91 tests (Goal >=80) -> PASSED
  Tier 2: Boundary & Corner Cases          : 85 tests (Goal >=80) -> PASSED
  Tier 3: Pairwise Integration Interactions : 16 tests (Goal >=16) -> PASSED
  Tier 4: Real-World Workload Scenarios     : 10 tests (Goal >=10) -> PASSED
------------------------------------------------------------------------------
  TOTAL EXECUTED: 202 | PASSED: 202 | FAILED: 0 | ERRORS: 0
  DURATION: 1.381s | STATUS: ALL SUITES PASSED (EXIT CODE 0)
==============================================================================
```

---

### 1.2 Empirical Adversarial Stress Test Suite Execution

To stress-test the six core pillars defined in the charter, an automated 28-test adversarial test suite was authored and executed:
```powershell
python .agents/challenger_m4_1/test_adversarial_m4.py
```
**Output**:
```text
Ran 28 tests in 0.715s

OK

[EMPIRICAL FINDING] Real corpus batch has 14 / 100 questions failing stem leakage gate.
```

---

### 1.3 Verbatim Code Defects and Empirical Vulnerabilities Identified

#### Defect 1 (CRITICAL): Generator Bypasses Verification Gate Failure and Emits Leaking Questions
- **File**: `v13_discovery/question_synthesizer.py`, lines 1416–1428
- **Direct Code Observation**:
```python
1416:         # 7. Execute 5-Point Verification Gate
1417:         is_valid, violations = DistractorVerificationGate.verify_all(
1418:             options=options_dict,
1419:             correct_key=correct_answer_str,
1420:             stem=stem,
1421:             category=cat
1422:         )
1423:         if not is_valid:
1424:             # Automatic repair: normalize casing and ensure unique non-placeholder options
1425:             repaired: Dict[str, str] = {}
1426:             for k, val in options_dict.items():
1427:                 v_clean = val.strip()
1428:                 repaired[k] = v_clean[0].upper() + v_clean[1:] if v_clean else "Basalt"
1429:             options_dict = repaired
```
- **Empirical Proof**:
When `verify_all()` flags violations (such as stem leakage or cross-category distractors), `synthesize()` merely capitalizes the options at lines 1425–1428 and **still returns the invalid `CandidateQuestion`**. It does not reject, regenerate, or strip the leaking tokens.
In `synthesize_from_corpus("source-material/geography_extracted.txt", min_questions=100)`, **14 out of 100 generated questions (14%) contain blatant stem leakage of the correct answer**:
  - **Question #17** (`q_1115efdc-d361-439c-bc4d-db90bb553394`):  
    *Stem*: `"Which of the following geographical features is defined as: Saptarishi (Saptaseven, rishi-sages)?"`  
    *Correct Answer*: `Option (C): Saptarishi`  
    *Error*: `["Stem leakage detected: correct answer 'saptarishi' found verbatim in stem"]`
  - **Question #18** (`q_227160a8-db08-4581-bafb-4d2a25ea586d`):  
    *Stem*: `"Which of the following geographical features is defined as: group of seven stars (Figure 1.1) that forms a part of Ursa Major Constellation?"`  
    *Correct Answer*: `Option (D): Ursa Major`  
    *Error*: `["Stem leakage detected: correct answer 'ursa major' found verbatim in stem"]`
  - **Question #52** (`q_77454985-7a39-4e9a-9b4f-cedd62cdf42b`):  
    *Stem*: `"Which of the following geographical features is defined as: this entity was taken that Pluto like other celestial objects (Ceres, 2003?"`  
    *Correct Answer*: `Option (D): Pluto`  
    *Error*: `["Stem leakage detected: correct answer 'pluto' found verbatim in stem"]`
  - **Question #88** (`q_58f28ccc-64c8-4d27-bb0a-084337bf48e6`):  
    *Stem*: `"Which of the following geographical features is defined as: found between the orbits of Mars and Jupiter (Figure 1.2)?"`  
    *Correct Answer*: `Option (D): Mars`  
    *Error*: `["Stem leakage detected: correct answer keyword 'mars' found in stem"]`
  - **Questions #27, #45, #59, #60, #65, #72, #75, #76, #84, #91**:  
    *Stem*: Each stem includes `'earth'` while `Earth` is the correct answer.

---

#### Defect 2 (MEDIUM): Stem-Terminal Indefinite Article Clueing Regex Loophole
- **File**: `v13_discovery/question_synthesizer.py`, line 984
- **Direct Code Observation**:
```python
983:         stem_trimmed = stem.strip().rstrip("?:").strip()
984:         if re.search(r'\b(?:is|as|called|termed)\s+(?:a|an)$', stem_trimmed, re.IGNORECASE):
985:             errors.append("Stem ends with indefinite article ('a' or 'an') leaking phonetic onset of options")
```
- **Empirical Proof**:
The regex enforces that the indefinite article must be preceded strictly by `is`, `as`, `called`, or `termed`. When tested with stems ending in other common interrogative verb frames, the gate completely misses the article clueing:
  - `"Which fluvial process creates an?"` -> `is_valid: True, errors: []`
  - `"Which geological feature represents a?"` -> `is_valid: True, errors: []`
  - `"In Earth science, this structure forms an:"` -> `is_valid: True, errors: []`
  - `"Which natural formation constitutes a?"` -> `is_valid: True, errors: []`
In all these cases, a stem ending with `"an"` unambiguously clues options starting with vowels (e.g. Oxbow lake, Arete, Esker), bypassing the gate.

---

#### Defect 3 (MEDIUM): Short Entity Stem Leakage Blind Spot
- **File**: `v13_discovery/question_synthesizer.py`, line 1054
- **Direct Code Observation**:
```python
1053:         correct_text = options.get(correct_letter, "").strip().lower()
1054:         if correct_text and len(correct_text) > 3:
1055:             stem_lower = stem.lower()
1056:             if len(correct_text) > 4 and correct_text in stem_lower:
...
```
- **Empirical Proof**:
Because line 1054 requires `len(correct_text) > 3`, any 3-letter educational concept (such as `Fog`, `Ice`, `Sun`, `Ore`, `Ash`, `Mud`) can appear verbatim in the stem without triggering the leakage gate:
  - Stem: `"Which atmospheric condensation phenomenon known as fog reduces visibility below 1 km?"`
  - Correct Answer: `Option A: Fog`
  - Output: `is_valid: True, errors: []` (Bypassed!)

---

#### Defect 4 (MEDIUM): Synthetic Placeholder Text Regex Incompleteness
- **File**: `v13_discovery/question_synthesizer.py`, lines 1000–1003
- **Direct Code Observation**:
```python
1000:         placeholder_regex = re.compile(
1001:             r'^(?:Alternative\s+\d+|Option\s+[A-Z]|None\b|TBD|Placeholder|Unknown)\b',
1002:             re.IGNORECASE
1003:         )
```
- **Empirical Proof**:
The regex strictly checks `Alternative\s+\d+` and `Option\s+[A-Z]`. Common synthetic placeholder patterns easily bypass this check:
  - `"Option 1"`, `"Option 2"` -> `is_valid: True` (Missed because `Option` expects `[A-Z]`)
  - `"Alternative A"`, `"Alternative B"` -> `is_valid: True` (Missed because `Alternative` expects `\d+`)
  - `"Choice A"`, `"Choice 1"` -> `is_valid: True`
  - `"All of the above"` -> `is_valid: True`
  - `"N/A"`, `"NA"` -> `is_valid: True`

---

#### Defect 5 (MEDIUM): Ontology Multi-Category Collision & Domain Hijacking
- **File**: `v13_discovery/question_synthesizer.py`, lines 260–274, 922–940
- **Direct Code Observation**:
`OntologyRegistry.register_category` overwrites `self.entity_to_category[member.lower()]`. Across the 38 registered categories, 17 entities are registered under multiple categories:
  - `Hadley cell` is registered under both `circulation_cells` (line 266) and `climatic_phenomena` (line 929).
  - Because `climatic_phenomena` is registered last, `Hadley cell` is resolved to `climatic_phenomena`.
- **Empirical Proof**:
When synthesizing a question about `Hadley cell`:
  - Expected Distractors: Circulation cells (`Ferrel cell`, `Polar cell`, `Walker circulation`)
  - Generated Distractors: `Coriolis force`, `Monsoon trough`, `Rossby waves`
When tested against `circulation_cells`, the verification gate flags:
`["Option 'b' ('Coriolis force') violates category compatibility for 'Atmospheric Circulation Cells'", "Option 'c' ('Monsoon trough') violates category compatibility for 'Atmospheric Circulation Cells'", "Option 'd' ('Rossby waves') violates category compatibility for 'Atmospheric Circulation Cells'"]`
Forces, planetary waves, and weather troughs are mixed with a circulation cell, degrading distractors from clean taxonomic siblings to heterogeneous concepts.

---

### 1.4 Pillars Verified as Robust

1. **Trap Dissections (Pillar 3 & 6)**:
   - All 8 authorized Room DB trap types (`ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`, `UNCLASSIFIED_TRAP`) produce valid pedagogical rationales (102–156 chars).
   - Invariants strictly maintained: Dissections are **strictly assigned to distractors** and **never to the correct answer**. Exactly 3 dissections exist per 4-choice question.
2. **Length Parity (Pillar 4)**:
   - Options >= 3.0x average length are reliably rejected.
   - Options < 0.25x average length (when avg >= 15) are reliably rejected.
3. **Merklized Provenance (Pillar 5)**:
   - 6-link SHA-256 Merklized provenance binding verified with 100% audit pass across 100 synthesized questions.

---

## 2. Logic Chain

1. **Observation 1.3 (Defect 1)** shows that `QuestionSynthesizer.synthesize` captures `is_valid, violations = DistractorVerificationGate.verify_all(...)` but takes no corrective or filtering action when `is_valid` is `False`. It only capitalizes the options and returns the flawed question.
2. Because `synthesize_from_corpus` blindly collects returned questions without filtering by `is_valid`, 14% of the real NCERT corpus output contains verbatim stem leakage (e.g. Q#17 gives away "Saptarishi", Q#18 gives away "Ursa Major", Q#52 gives away "Pluto", Q#88 gives away "Mars").
3. This directly violates **ORIGINAL_REQUEST.md §R3** ("Distractors must be independently verified for category compatibility, grammatical fit... and absence of clueing/contradiction") and **§R4** ("The final quality gate must be capable of rejecting a question that the generator itself considers valid").
4. **Observation 1.3 (Defects 2, 3, 4)** demonstrates that even when called directly, the verification gate regexes are under-specified:
   - Grammatical fit only detects 4 specific verbs before articles.
   - Stem leakage ignores words with <= 3 characters.
   - Semantic plausibility ignores `Option \d+`, `Choice [A-Z]`, `N/A`.
5. **Observation 1.3 (Defect 5)** demonstrates that domain overlap in `OntologyRegistry` causes `Hadley cell` to draw distractors from planetary waves and forces rather than atmospheric circulation cells.
6. Therefore, while Milestone 4 has strong architectural foundations (provenance, 38 categories, trap dissections), the generator-to-gate binding and regex filters contain material gaps that permit defective questions into the pipeline.

---

## 3. Caveats

1. **Baseline Suite Blind Spots**: The baseline test suites (`test_v13_distractor_engine.py` and `run_e2e_tests.py`) passed 100% because their fixtures used pre-cleaned nodes that avoided these specific edge cases (e.g. they tested "Venus" or "Troposphere" where entity de-identification succeeded).
2. **Downstream Auditing**: Milestone 5 introduces independent LLM Auditors (Cognitive, Exam-Fit, Adversarial) which may catch some of these defects downstream. However, the charter explicitly mandates that the Milestone 4 Synthesizer and Distractor Verification Gate must themselves enforce these quality contracts.
3. **No Implementation Changes Made**: In accordance with challenger role constraints, no production files were modified. All tests and evidence scripts reside within `.agents/challenger_m4_1/`.

---

## 4. Conclusion

**Verdict**: `REQUEST_CHANGES`

The distractor engine and verification gate require targeted hardening before sign-off. The following five concrete changes are requested for `worker_m4_1`:

1. **Enforce Gate Rejection in `synthesize()` and `synthesize_from_corpus()`**:
   - In `synthesize()`: If `verify_all()` returns `is_valid=False`, attempt targeted entity de-identification from the stem; if violations persist, either raise `ValueError(f"Question failed distractor verification: {violations}")` or flag `cq.valid = False`.
   - In `synthesize_from_corpus()`: Ensure questions failing the 5-point verification gate are discarded and skipped from the final output batch.
2. **Harden Stem-Terminal Indefinite Article Detection**:
   - In `check_grammatical_fit()`: Replace `r'\b(?:is|as|called|termed)\s+(?:a|an)$'` with `r'\b(?:a|an)$'` (matching any stem-terminal indefinite article, regardless of preceding verb).
3. **Close Short-Entity Stem Leakage Blind Spot**:
   - In `check_absence_of_clueing()`: Change `len(correct_text) > 3` to `len(correct_text) >= 3`, ensuring 3-letter concepts like "Fog", "Ice", "Sun", "Ore" are checked against the stem using whole-word boundary matching `r'\b' + re.escape(correct_text) + r'\b'`.
4. **Expand Placeholder Regex**:
   - In `check_semantic_plausibility()`: Update `placeholder_regex` to match:
     `r'^(?:Alternative\s+[0-9A-Z]+|Option\s+[0-9A-Z]+|Choice\s+[0-9A-Z]+|None\b|TBD|Placeholder|Unknown|N/A|NA|All of the above)\b'`
5. **Deduplicate `OntologyRegistry` Category Memberships**:
   - Remove `Hadley cell` from `climatic_phenomena` (retaining it exclusively in `circulation_cells`).
   - Clean `fluvial_landforms` so that glacial landforms (`Cirque`, `Moraine`) and aeolian landforms (`Mushroom rock`) are properly separated.

---

## 5. Verification Method

To independently reproduce all observations and empirical findings:

```powershell
# 1. Run standard distractor engine unit tests (24/24 PASS)
python -m unittest tests/test_v13_distractor_engine.py

# 2. Run full E2E test suite (202/202 PASS)
python run_e2e_tests.py

# 3. Run Challenger comprehensive 28-test adversarial stress suite (28/28 PASS)
python .agents/challenger_m4_1/test_adversarial_m4.py

# 4. Run real corpus batch leakage inspector (reproduces 14 failing questions)
python .agents/challenger_m4_1/inspect_failing_batch.py

# 5. Run article and placeholder bypass scripts
python .agents/challenger_m4_1/test_article_bypass.py
python .agents/challenger_m4_1/test_placeholder_bypass.py
python .agents/challenger_m4_1/find_collisions.py
```

**Artifact Files in Agent Directory**:
- `.agents/challenger_m4_1/test_adversarial_m4.py`: Comprehensive 28-test adversarial test suite
- `.agents/challenger_m4_1/inspect_failing_batch.py`: Script isolating the 14 real-corpus questions failing stem leakage
- `.agents/challenger_m4_1/test_article_bypass.py`: Empirical verification of article clueing bypass
- `.agents/challenger_m4_1/test_placeholder_bypass.py`: Empirical verification of placeholder regex bypass
- `.agents/challenger_m4_1/find_collisions.py`: Analysis of 17 category member collisions in `OntologyRegistry`
- `.agents/challenger_m4_1/BRIEFING.md`: Challenger situational memory
- `.agents/challenger_m4_1/progress.md`: Liveness heartbeat
