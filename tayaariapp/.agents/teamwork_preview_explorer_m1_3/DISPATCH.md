# Task Assignment: M1 Dataset Validation Explorer

You are teamwork_preview_explorer_m1_3.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_3
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md

Objective:
Investigate and design the validation harness and verification logic for the Golden Evaluation Set:
1. Design an automated validator script (e.g. `tests/test_golden_eval_set.py` or `scripts/validate_eval_set.py`) that strictly checks:
   - File format and JSON schema conformity of `data/golden_eval_set.json`.
   - Count constraints: total items >= 100, positive examples >= 50, negative examples >= 50.
   - Representation constraints: all 14 semantic intents represented among positive examples.
   - Non-triviality constraints: no empty strings, valid provenance fields (`source_file`, `line_or_page`), non-overlapping IDs.
   - Negative categories: presence of MCQ noise, watermark noise, incomplete clause fragments, OCR artifacts.
2. Outline how subsequent milestones (M2, M3) will consume this evaluation set to calculate Precision, Recall, False Acceptance Rate (FAR), and False Rejection Rate (FRR).
3. Write your handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_3\handoff.md
4. Send a message to parent orchestrator upon completion.

## 2026-09-03T10:47:29Z
You are teamwork_preview_explorer_m1_3.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_3
Read your instructions in: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_3\DISPATCH.md
Also read ORIGINAL_REQUEST.md and PROJECT.md.
Investigate and design the validation harness and verification logic for the Golden Evaluation Set (schema conformity, count constraints >=100, 14 intents representation, negative types, P/R/FAR computation).
Write your handoff report to: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_3\handoff.md
Send a completion message back to parent orchestrator.
