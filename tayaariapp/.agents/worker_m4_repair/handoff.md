# Handoff Report: Milestone 4 Adversarial Fixes & Gate Hardening

**Date**: 2026-09-06T17:25:00Z  
**Agent**: worker_m4_repair (implementer, qa, specialist)  
**Parent Orchestrator**: teamwork_preview_orchestrator_5 (`d497dcb5-7f26-4e7c-bd7e-8bd149a1669d`)  
**Status**: COMPLETE (100% PASS across all verification commands; 0% stem leakage across 100 corpus questions)

---

## 1. Observation

### 1.1 Direct Observations of Addressed Vulnerabilities

1. **Defect 1 (Gate Bypassing & Stem Leakage)**:
   - *Initial State*: In `v13_discovery/question_synthesizer.py`, `synthesize()` executed `is_valid, violations = DistractorVerificationGate.verify_all(...)` but only performed capitalization repair without filtering or repairing leaking stems. In `synthesize_from_corpus()`, 14 out of 100 questions (14%) generated from `source-material/geography_extracted.txt` contained stem leakage (e.g., Q#17 leaked "Saptarishi", Q#18 leaked "Ursa Major", Q#52 leaked "Pluto", Q#88 leaked "Mars", and 10 questions leaked "Earth").
   - *Fix Applied*:
     - Added `valid: bool = True` field to dataclass `CandidateQuestion`.
     - In `NaturalStemSynthesizer.synthesize_stem()`, added optional parameter `target_entity: Optional[str] = None` and enhanced `clean_evidence_for_stem()` to de-identify target entity mentions using whole-word matching.
     - In `QuestionSynthesizer.synthesize()`, passed `target_entity=correct_answer_text`. If `verify_all()` flags violations, targeted entity de-identification is applied to the stem replacing full answer text and significant non-stopword tokens (`>= 3` chars), option casing is normalized, and the gate is re-verified. `cq.valid` is set to `is_valid`.
     - In `synthesize_from_corpus()`, questions failing `cq.valid`, `DistractorVerificationGate.verify_all()`, or `DistractorVerificationGate.check_absence_of_clueing()` are strictly filtered and discarded until `min_questions` (100) strictly valid, gate-passing questions are generated.

2. **Defect 2 (Stem-Terminal Indefinite Article Detection Loophole)**:
   - *Initial State*: `check_grammatical_fit()` matched only four specific verbs before articles via `r'\b(?:is|as|called|termed)\s+(?:a|an)$'`. General interrogative verbs (`"creates an?"`, `"represents a?"`, `"forms an:"`, `"constitutes a?"`) bypassed the gate.
   - *Fix Applied*: Replaced regex with `r'\b(?:a|an)$'` in line 984, matching any stem-terminal indefinite article regardless of preceding verb.

3. **Defect 3 (Short-Entity Stem Leakage Blind Spot)**:
   - *Initial State*: `check_absence_of_clueing()` enforced `len(correct_text) > 3` and `len(correct_text) > 4` for verbatim matching. 3-letter educational concepts (`Fog`, `Ice`, `Sun`, `Ore`) bypassed the stem leakage check.
   - *Fix Applied*: Updated to `len(correct_text) >= 3` with regex word-boundary matching `r'\b' + re.escape(correct_text) + r'\b'` and token check `r'\b[a-z]{3,}\b'`.

4. **Defect 4 (Synthetic Placeholder Text Incompleteness)**:
   - *Initial State*: `placeholder_regex` only matched `Alternative \d+` and `Option [A-Z]`. Common variants (`Option 1`, `Option 2`, `Choice A`, `Choice 1`, `All of the above`, `N/A`, `NA`) bypassed the filter.
   - *Fix Applied*: Expanded regex to:
     `r'^(?:Alternative\s+[0-9A-Za-z]+|Option\s+[0-9A-Za-z]+|Choice\s+[0-9A-Za-z]+|None\b|TBD|Placeholder|Unknown|N/A|NA|All of the above|None of the above|Dummy|Sample|Test\s+Option)\b'`.

5. **Defect 5 (Ontology Multi-Category Collision & Domain Hijacking)**:
   - *Initial State*: `Hadley cell` was registered under both `circulation_cells` and `climatic_phenomena`. Because `climatic_phenomena` was registered last, `Hadley cell` resolved to `climatic_phenomena`, generating distractors like `Coriolis force` and `Rossby waves` that violated `circulation_cells`. In addition, `fluvial_landforms` contained glacial (`Cirque`, `Moraine`) and aeolian (`Mushroom rock`) landforms.
   - *Fix Applied*:
     - Removed `Hadley cell` from `climatic_phenomena`, replacing it with `Jet stream`. `Hadley cell` is now exclusively in `circulation_cells`.
     - Cleaned `fluvial_landforms` by removing `Cirque`, `Moraine`, and `Mushroom rock`, populating it with authentic river landforms (`Oxbow lake`, `Delta`, `Gorge`, `Meander`, `Floodplain`, `Alluvial fan`). `Cirque` and `Moraine` now map cleanly to `glacial_landforms`, and `Mushroom rock` to `aeolian_landforms`.

---

### 1.2 Verification Commands and Verbatim Outputs

#### Command 1: Milestone 4 Distractor Engine Unit Test Suite (30 Tests)
```powershell
python -m unittest tests/test_v13_distractor_engine.py
```
**Output**:
```text
..............................
----------------------------------------------------------------------
Ran 30 tests in 0.723s

OK
```

#### Command 2: Adversarial Stress Test Suite (28 Tests)
```powershell
python .agents/challenger_m4_1/test_adversarial_m4.py
```
**Output**:
```text
test_01_cross_category_detection_comprehensive (__main__.TestAdversarialCategoryCompatibility.test_01_cross_category_detection_comprehensive) ... ok
test_02_all_options_foreign (__main__.TestAdversarialCategoryCompatibility.test_02_all_options_foreign) ... ok
test_03_valid_siblings_pass (__main__.TestAdversarialCategoryCompatibility.test_03_valid_siblings_pass) ... ok
test_04_synthesizer_generates_options_matching_resolved_category (__main__.TestAdversarialCategoryCompatibility.test_04_synthesizer_generates_options_matching_resolved_category) ... ok
test_05_multi_category_collision_causes_conceptual_cross_leakage (__main__.TestAdversarialCategoryCompatibility.test_05_multi_category_collision_causes_conceptual_cross_leakage) ... ok
test_11_stem_terminal_copula_article_caught (__main__.TestAdversarialGrammaticalClueing.test_11_stem_terminal_copula_article_caught) ... ok
test_12_non_copula_stem_terminal_article_bypass_vulnerability (__main__.TestAdversarialGrammaticalClueing.test_12_non_copula_stem_terminal_article_bypass_vulnerability) ... ok
test_13_mixed_capitalization_detected (__main__.TestAdversarialGrammaticalClueing.test_13_mixed_capitalization_detected) ... ok
test_14_uniform_capitalization_accepted (__main__.TestAdversarialGrammaticalClueing.test_14_uniform_capitalization_accepted) ... ok
test_15_extremely_long_option_rejected (__main__.TestAdversarialLengthOutliers.test_15_extremely_long_option_rejected) ... ok
test_16_extremely_short_option_rejected (__main__.TestAdversarialLengthOutliers.test_16_extremely_short_option_rejected) ... ok
test_17_balanced_lengths_pass (__main__.TestAdversarialLengthOutliers.test_17_balanced_lengths_pass) ... ok
test_18_standard_placeholder_options_rejected (__main__.TestAdversarialPlaceholdersAndDuplicates.test_18_standard_placeholder_options_rejected) ... ok
test_19_unlisted_placeholder_options_bypass_vulnerability (__main__.TestAdversarialPlaceholdersAndDuplicates.test_19_unlisted_placeholder_options_bypass_vulnerability) ... ok
test_20_single_character_options_rejected (__main__.TestAdversarialPlaceholdersAndDuplicates.test_20_single_character_options_rejected) ... ok
test_21_exact_and_case_insensitive_duplicates_rejected (__main__.TestAdversarialPlaceholdersAndDuplicates.test_21_exact_and_case_insensitive_duplicates_rejected) ... ok
test_22_insufficient_option_count_rejected (__main__.TestAdversarialPlaceholdersAndDuplicates.test_22_insufficient_option_count_rejected) ... ok
test_06_verbatim_answer_leakage_detected (__main__.TestAdversarialStemLeakage.test_06_verbatim_answer_leakage_detected) ... ok
test_07_multi_word_keyword_leakage_detected (__main__.TestAdversarialStemLeakage.test_07_multi_word_keyword_leakage_detected) ... ok
test_08_distractor_mention_does_not_falsely_trigger_answer_leakage (__main__.TestAdversarialStemLeakage.test_08_distractor_mention_does_not_falsely_trigger_answer_leakage) ... ok
test_09_natural_stem_synthesizer_strips_target_entity (__main__.TestAdversarialStemLeakage.test_09_natural_stem_synthesizer_strips_target_entity) ... ok
test_10_short_3_letter_entity_leakage_bypass_vulnerability (__main__.TestAdversarialStemLeakage.test_10_short_3_letter_entity_leakage_bypass_vulnerability) ... ok
test_23_all_8_trap_types_generate_valid_rationales (__main__.TestAdversarialTrapDissections.test_23_all_8_trap_types_generate_valid_rationales) ... ok
test_24_dissections_never_assigned_to_correct_answer (__main__.TestAdversarialTrapDissections.test_24_dissections_never_assigned_to_correct_answer) ... ok
test_25_dissections_cover_all_distractor_keys (__main__.TestAdversarialTrapDissections.test_25_dissections_cover_all_distractor_keys) ... ok
test_26_scale_batch_yields_100_distinct_stems (__main__.TestRealCorpusBatchQuality.test_26_scale_batch_yields_100_distinct_stems) ... ok
test_27_batch_audit_distractor_dissections (__main__.TestRealCorpusBatchQuality.test_27_batch_audit_distractor_dissections) ... ok
test_28_batch_stem_leakage_rate_documented (__main__.TestRealCorpusBatchQuality.test_28_batch_stem_leakage_rate_documented) ... ok

----------------------------------------------------------------------
Ran 28 tests in 0.676s

OK

[EMPIRICAL FINDING] Real corpus batch has 0 / 100 questions failing stem leakage gate.
```

#### Command 3: Full Project Unit Test Discovery (536 Tests)
```powershell
python -m unittest discover -s tests -p "test_*.py"
```
**Output**:
```text
Ran 536 tests in 13.106s

OK
```

#### Command 4: Full End-to-End Test Suite (202 Tests)
```powershell
python run_e2e_tests.py
```
**Output**:
```text
----------------------------------------------------------------------
Ran 202 tests in 1.169s

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
  DURATION: 1.191s | STATUS: ALL SUITES PASSED (EXIT CODE 0)
  TELEMETRY REPORT: C:\Users\harsh\Downloads\tayaari\tayaariapp\test_reports\e2e_test_report.json
==============================================================================
```

#### Command 5: Dedicated 100-Question Corpus Verification Script
```powershell
python .agents/worker_m4_repair/test_corpus_generation_100.py
```
**Output**:
```text
Initializing QuestionSynthesizer...
Synthesizing 100 questions from C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt...
Total questions synthesized: 100
Gate failures: 0 / 100
Stem leakage failures: 0 / 100

SUCCESS: All 100 questions strictly passed DistractorVerificationGate.verify_all() with 0% stem leakage!
```

---

## 2. Logic Chain

1. **Gate Enforcement & Filtering (Observation 1.1 §1)**:
   - `synthesize()` now actively de-identifies both the primary entity and the canonicalized correct answer text during stem synthesis.
   - When `verify_all()` flags any violation, targeted entity de-identification is attempted across the stem and option casing is repaired.
   - The question is re-verified, and `cq.valid = is_valid` is bound directly onto the `CandidateQuestion` object.
   - In `synthesize_from_corpus()`, any candidate question where `cq.valid == False` or failing `DistractorVerificationGate.verify_all()` is immediately discarded, and extraction iterates over the 586 corpus nodes until 100 strictly valid questions are accumulated.
   - This reduced real corpus batch stem leakage from 14/100 (14%) to **0/100 (0.0%)**, directly satisfying **ORIGINAL_REQUEST.md §R3** and **§R4**.

2. **Indefinite Article Hardening (Observation 1.1 §2)**:
   - The regex `r'\b(?:a|an)$'` strictly checks the final word of the trimmed stem regardless of the preceding verb.
   - Non-copula frames such as `"creates an?"` or `"represents a?"` are now caught, preventing phonetic onset clueing for vowel-initial distractors (e.g. Oxbow lake, Arete, Esker).

3. **Short-Entity Leakage Prevention (Observation 1.1 §3)**:
   - Lowering the length threshold from `> 3` to `>= 3` with regex word boundaries (`\b`) ensures 3-letter concepts ("Fog", "Ice", "Sun", "Ore") cannot appear as standalone words in the stem without tripping the gate.
   - Substring false-positives (e.g. "ore" inside "before", "ice" inside "surface") are prevented by the `\b` word boundary anchors.

4. **Placeholder Text Robustness (Observation 1.1 §4)**:
   - Expanding the regex to `[0-9A-Za-z]+` and including `N/A`, `NA`, and `All of the above` prevents synthetic generators or mock fallbacks from emitting artificial placeholder distractors.

5. **Ontological Purity (Observation 1.1 §5)**:
   - Removing `Hadley cell` from `climatic_phenomena` ensures that questions targeting `Hadley cell` draw distractors exclusively from `circulation_cells` (`Ferrel cell`, `Polar cell`, `Walker circulation`), preventing heterogeneous mixtures of forces, waves, and circulation cells.
   - Cleaning `fluvial_landforms` isolates glacial and aeolian landforms to their proper geological processes.

---

## 3. Caveats

1. **Domain Word Stopwords in Stem De-Identification**:
   - The token-level de-identification loop ignores common generic domain words (e.g. "rock", "layer", "river", "zone", "valley") to prevent over-scrubbing educational context sentences. Specific proper names and concepts (e.g. "Basalt", "Troposphere", "Ursa Major") are always de-identified.
2. **Deterministic Fallbacks**:
   - If a category has fewer than 3 sibling members, `synthesize()` falls back to domain rocks to ensure 4 distinct options are always available.

---

## 4. Conclusion

All 5 targeted adversarial fixes requested by `challenger_m4_1` and parent orchestrator `teamwork_preview_orchestrator_5` have been implemented, verified, and regression-tested.

- **0% stem leakage** across 100 generated questions from NCERT corpus.
- **100% pass** on distractor engine unit tests (30/30).
- **100% pass** on adversarial stress test suite (28/28).
- **100% pass** on full project unit test discovery (536/536).
- **100% pass** on full end-to-end test suite (202/202).

Milestone 4 Distractor Engineering and Quality Gate are hardened and ready for Milestone 5 (Multi-Agent Auditing).

---

## 5. Verification Method

To independently verify the complete repair:

```powershell
# 1. Milestone 4 Unit Test Suite with 6 new adversarial regression tests (30/30 PASS)
python -m unittest tests/test_v13_distractor_engine.py

# 2. Challenger Adversarial Stress Suite verifying hardened behavior (28/28 PASS, 0/100 failing)
python .agents/challenger_m4_1/test_adversarial_m4.py

# 3. Dedicated 100-Question Corpus Verification (0 Gate failures, 0% Stem leakage)
python .agents/worker_m4_repair/test_corpus_generation_100.py

# 4. Full Project Unit Test Discovery (536/536 PASS)
python -m unittest discover -s tests -p "test_*.py"

# 5. Full End-to-End Test Suite (202/202 PASS)
python run_e2e_tests.py
```
