# Orchestration Plan — Generation 5

## Objective
Verify and complete Milestone 4 (Question & Defensible Distractor Engine), advance to and complete Milestone 5 (Multi-Agent Auditing Quality Gate & Self-Repair), and Milestone 6 (Android Integration, Final E2E Suite, Gradle verification).

## Step 1: Milestone 4 Verification & Gate 4 Evaluation
- Step 1.1: Dispatch `worker_m4_verify` to execute full test suite (`python -m unittest tests/test_v13_distractor_engine.py`, `python -m unittest discover -s tests -p "test_*.py"`, `python run_e2e_tests.py`) and verify zero regressions, 100+ questions synthesis, and Room DB markdown formatting.
- Step 1.2: Dispatch Gate 4 evaluation team:
  - `reviewer_m4_1`: Review code quality, Room DB contracts, anti-quotation rules (NQ1-NQ5), 5-point verification gate.
  - `reviewer_m4_2`: Review ontology completeness (32 categories), grammatical parallelism, 6-link cryptographic Merklized provenance.
  - `challenger_m4_1`: Adversarially test distractor plausibility, category leakage, clueing, length outliers.
  - `challenger_m4_2`: Adversarially test scale synthesis (>=100 questions diversity), Room DB markdown sequential parsing (`Explanation:` before `Correct Answer:`).
  - `auditor_m4_1`: Forensic audit for zero fake distractors, zero hardcoded questions, genuine provenance chains.
- Step 1.3: Gate check. Record in `GATE_STATUS_M4.md`. If all pass with unanimous APPROVE and CLEAN, mark M4 DONE in `PROJECT.md` and `progress.md`.

## Step 2: Milestone 5 — Multi-Agent Auditing Quality Gate & Self-Repair
- Step 2.1: Survey/Spec: Dispatch Explorer/Spec Miner to examine audit dimensions (Cognitive, Exam-Fit, Adversarial), self-repair logic, and feedback regeneration loops.
- Step 2.2: Dispatch Worker to implement Multi-Agent Auditing & Self-Repair pipeline (`v13_discovery/auditing.py` or equivalent and corresponding tests).
- Step 2.3: Gate 5 evaluation (Reviewers, Challengers, Forensic Auditor).
- Step 2.4: Gate check and mark M5 DONE.

## Step 3: Milestone 6 — Android Integration, Regression Suite, Gradle Verification
- Step 3.1: Survey/Spec: Examine Room DB, DataImporter.kt, consolidated_grounding sync, Kotlin tests, Gradle build environment.
- Step 3.2: Dispatch Worker to sync generated grounded questions into Android assets, verify DataImporter, run gradle testDebugUnitTest and assembleDebug.
- Step 3.3: Gate 6 evaluation (Reviewers, Challengers, Forensic Auditor).
- Step 3.4: Final comprehensive verification & report to Sentinel for independent Victory Audit.
