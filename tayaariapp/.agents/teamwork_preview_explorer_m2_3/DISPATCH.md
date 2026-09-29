# Task Assignment: M2 Semantic Test & Verification Explorer

You are teamwork_preview_explorer_m2_3.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_3
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md
Golden eval set: c:\Users\harsh\Downloads\tayaari\tayaariapp\data\golden_eval_set.json

Objective:
Investigate and design the comprehensive unit test suite for Milestone 2 (`tests/test_v13_semantic_extractor.py`):
1. Design test cases verifying that the V13 semantic extractor successfully identifies and slots each of the 14 semantic intents from `data/golden_eval_set.json`:
   - 1 test case per intent (14 tests total) covering `definition`, `attribute`, `cause/effect`, `comparison`, `spatial`, `distribution`, `classification`, `quantity`, `sequence`, `condition`, `exception`, `process`, `part-of`, `member-of`.
2. Design test cases verifying negative noise rejection:
   - Verify that all 6 noise categories in `golden_eval_set.json` (MCQ leakage, watermarks, fragments, broken reading order, table formatting artifacts, anaphoric references) are correctly rejected with 0 false acceptances.
3. Design test cases for the normalizer:
   - Markdown table ingestion -> produces valid propositions.
   - Broken column stitcher -> reconstructs continuous sentences.
   - Watermark filter -> strips headers without altering prose.
4. Write your test architecture, sample assertions, and handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_3\handoff.md
## 2026-09-03T14:45:32Z
You are teamwork_preview_explorer_m2_3.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_3
Read DISPATCH.md, ORIGINAL_REQUEST.md, PROJECT.md, and golden_eval_set.json.
Investigate and design the comprehensive unit test suite (tests/test_v13_semantic_extractor.py) verifying all 14 semantic intents and negative noise rejection.
Write handoff.md and send a completion message back to parent orchestrator.
