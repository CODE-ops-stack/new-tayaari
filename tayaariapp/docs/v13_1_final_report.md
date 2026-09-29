# V13.1 Generator Repair Campaign - Final Report

## Summary
The pipeline has been completely rewritten into a 6-stage semantic chain:
SOURCE EVIDENCE → KNOWLEDGE UNIT → QUESTION INTENT → ANSWER CONTRACT → DISTRACTOR CONTRACT → QUESTION → INDEPENDENT VALIDATION.

## Key Fixes
1. Substring semantics completely removed. `detect_semantic_type` now uses whole-word regex and context checks.
2. Source block gating explicitly rejects OCR artifacts, metadata, and fragments.
3. Questions are synthesized purely from extracted intents rather than raw source wrapping.
4. Independent validators catch fake UPSC, fake APPLY, and leakage.
5. All 16 regression tests pass successfully, proving that historic collisions (Indus/industrial, star/started, etc.) are permanently blocked.

## Metrics
- See `v13_1_corpus_benchmark.json`
- See `v13_1_accepted_sample.json`
