# Task Assignment: M1 Dataset Stress Challenger 1

You are teamwork_preview_challenger_m1_1.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m1_1
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md
Worker handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m1_1\handoff.md

Objective:
Empirically challenge and stress-test the Golden Evaluation Dataset and validation harness:
1. Write adversarial test generators / stress scripts against `scripts/validate_eval_set.py` and `tests/test_golden_eval_set.py`:
   - Corrupt JSON structure, missing mandatory keys (`expected_label`, `intent`, `provenance`).
   - Undercounts (<50 positive, <50 negative).
   - Dropped semantic intents (missing 1 of 14).
   - Duplicate IDs or empty text fields.
   - Faulty provenance coordinates.
2. Confirm whether the validation scripts and test suites properly reject corrupted/invalid datasets and accept the real `data/golden_eval_set.json`.
3. Provide your empirical confirmation verdict (APPROVE or REJECT).
4. Write your handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m1_1\handoff.md
5. Send completion message back to parent orchestrator.

## 2026-09-03T11:04:35Z
You are teamwork_preview_challenger_m1_1.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m1_1
Read your instructions in: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m1_1\DISPATCH.md
Read ORIGINAL_REQUEST.md, PROJECT.md, and worker handoff.md.
Adversarially stress-test data/golden_eval_set.json and scripts/validate_eval_set.py.
Deliver your confirmation verdict in handoff.md.
Send a completion message back to parent orchestrator.

