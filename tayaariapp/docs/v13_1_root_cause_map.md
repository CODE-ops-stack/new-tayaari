# V13.1 Root Cause Map

## 1. Entity Detection
**File**: `v13_discovery/extractor.py` (via `HybridSemanticExtractor.extract_sentence()`)
**Failure**: Extracts raw string `primary_entity` and `raw_evidence`.

## 2. Category Detection
**File**: `run_v13_production_batch.py` (function `detect_category(entity, evidence)`)
**Failure**: Uses raw substring matching (`combined = (entity + " " + evidence).lower()`, `if any(w in combined for w in [...])`).
*   `"indus"` matches `"industrial"` or `"industry"`
*   `"star"` matches `"started"` or `"starting"`
*   `"rice"` matches `"price"`
*   `"ring"` matches `"ring of fire"`
Returns a hardcoded list of fixed ontology members (e.g., `ONTOLOGY_BANKS["rivers_india"]`).

## 3. Answer Selection
**File**: `run_v13_production_batch.py` (Main loop, lines 512-526)
**Failure**: Canonicalizes the correct answer by picking the first category member that is a substring of the entity or evidence (`if len(m) >= 4 and m.lower() in ev.lower(): correct_text = m`). This binds an unrelated word (like "Indus") as the correct answer just because it was substring-matched.

## 4. Defensibility
**File**: `run_v13_production_batch.py` (function `answer_is_defensible(correct, stem, evidence)`)
**Failure**: Checks `return correct.lower() in evidence.lower()`. This validates the broken substring match from step 3.

## 5. Topic Selection
**File**: `run_v13_production_batch.py` (function `classify_topic(text)`)
**Failure**: Uses naive substring matching (`if kw in text.lower()`). If no match is found, it falls back to a hardcoded default: `return 6, "Physical Geography"`, which is why 25% of questions ended up with this incorrect topic.

## 6. Stem Construction
**File**: `run_v13_production_batch.py` (function `build_stem(entity, predicate, evidence, category_name)`)
**Failure**: Uses crude regex templates that wrap the raw source sentence without synthesizing a standalone question intent. For example, fallback template 10 just wraps the sentence: `"With reference to physical geography, which of the following is correctly described: {ev_clean}?"`. The templates cause non-questions and OCR artifacts to leak into the stem.

## 7. Distractor Generation
**File**: `run_v13_production_batch.py` (function `get_distractors(correct, members, n)`)
**Failure**: Generates distractors by shuffling the remaining members of the matched category. Since the category match is often fundamentally wrong (e.g. Celestial Bodies for an Aviation policy question), the distractors are completely unrelated to the question intent.

## 8. Cognitive Classification
**File**: `run_v13_production_batch.py` (Main loop, lines 644-650)
**Failure**: Checks if specific substrings exist in the generated stem (e.g. `"which of the following"` → `"UNDERSTAND"`, `"why"` → `"APPLY"`). This results in almost all simple recall questions being over-classified as UNDERSTAND.

## 9. Exam Classification
**File**: `run_v13_production_batch.py` (function `assign_exam(topic_name, cognitive)`)
**Failure**: Uses crude mapping of topics and cognitive levels to exams, using `random.choice()` among options. This forces recall-level questions into UPSC_CSE merely because they match a topic keyword.

## 10. Provenance
**File**: `run_v13_production_batch.py` (Main loop, lines 661-669)
**Failure**: blindly accepts `ev[:200]`. Lacks rigorous structure binding the exact knowledge unit to the generated question.

## 11. Final Acceptance
**File**: `run_v13_production_batch.py` (Main loop, lines 564-640)
**Failure**: Relies on a series of hardcoded string "gates" (e.g. `Gate 1: planet answers only valid for...`, `Gate 5: reject if evidence ends mid-sentence`) that fail to catch systemic semantic misalignment. Also, the batch audit for duplicates uses simple `SequenceMatcher` which fails to catch semantic duplicates or logic leaks.
