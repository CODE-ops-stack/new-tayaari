# Task Assignment: M1 Dataset & Architecture Reviewer 2

You are teamwork_preview_reviewer_m1_2.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m1_2
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md
Worker handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m1_1\handoff.md

Objective:
Independently review the Golden Evaluation Dataset and Android verification for Milestone 1:
1. Review `data/golden_eval_set.json`:
   - Verify counts: 111 total (56 positive, 55 negative).
   - Check that all 14 semantic intents have 4 verified items each.
   - Check that all 6 noise categories are covered.
   - Verify non-triviality and genuine corpus provenance (source_file, line_or_page).
2. Run dataset validation:
   - `python scripts/validate_eval_set.py data/golden_eval_set.json`
   - `python -m unittest discover -s tests -p "test_golden_eval_set.py"`
3. Verify Android unit tests and build:
   - `.\gradlew.bat clean testDebugUnitTest`
   - `.\gradlew.bat clean assembleDebug`
4. State your explicit verdict (APPROVE or REQUEST_CHANGES) with detailed evidence.
5. Write your handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m1_2\handoff.md
6. Send completion message back to parent orchestrator.

## 2026-09-03T11:04:35Z
You are teamwork_preview_reviewer_m1_2.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m1_2
Read your instructions in: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m1_2\DISPATCH.md
Read ORIGINAL_REQUEST.md, PROJECT.md, and worker handoff.md.
Independently review data/golden_eval_set.json, test_golden_eval_set.py, and Android tests/build.
Deliver your explicit verdict (APPROVE or REQUEST_CHANGES) in handoff.md.
Send a completion message back to parent orchestrator.
