# Dispatch Instructions

## 2026-09-03T10:34:37Z

User Request:
Build and validate a substantially better source-driven educational question discovery pipeline (V13) for the Tayaari Pakki Android application to maximize legitimate knowledge recovery (high recall) and minimize false acceptance (high precision) while generating natural exam-quality questions with defensible distractors.

Core Requirements:
- R1: Forensic & Corpus Analysis (Trace V12 pipeline failure points, profile real source corpus).
- R2: Advanced Knowledge Representation (Map source blocks to explicit semantic intents; permitted to use NLP libraries like spacy/nltk and/or local API-based LLMs; no pure SVO regex).
- R3: Question & Distractor Engineering (Explicit Question Intents, independent distractor verification for category, grammar, plausibility, evidence, no clueing).
- R4: Multi-Agent Auditing System (Cognitive Auditor, Exam-Fit Auditor, Adversarial Auditor with independent final quality gate).
- R5: Mandatory Experiments & Provenance (Compare at least 3 extraction/representation approaches; process at least 100 real source units; generate at least 100 opportunities or exhaust corpus; unbreakable provenance chain).

Acceptance Criteria:
1. At least 3 extraction approaches compared with documented precision/recall/false acceptance/rejection metrics.
2. Representative eval set (>=50 positive, >=50 negative) built and tested.
3. At least 50 candidate questions generated and adversarially audited.
4. Complete regeneration cycle after systemic repair of round 1 audit failures.
5. No generic quotation templates.
6. All regression tests pass + new regression tests for MCQ leakage, OCR fragments, multi-word entities, non-SVO facts, semantic duplicates, provenance failures.
7. Android unit tests pass (.\gradlew.bat clean testDebugUnitTest).
8. Android app builds successfully (.\gradlew.bat clean assembleDebug).
