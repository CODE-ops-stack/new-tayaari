# Task Assignment: M2 Iteration 2 Remediation Worker

You are teamwork_preview_worker_m2_2.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m2_2
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Gate status: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\GATE_STATUS.md
Explorer 1 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_1\handoff.md
Explorer 2 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_2\handoff.md
Explorer 3 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_3\handoff.md
Patches available:
- `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_1\proposed_remediation.patch`
- `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_2\semantic_extractor.patch`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You own exclusively:
- `v13_discovery/semantic_extractor.py`
- `v13_discovery/normalizer.py`
- `tests/test_v13_adversarial_challenge.py`
- `tests/test_v13_adversarial_m2_challenge.py`
- `tests/test_v13_semantic_extractor.py`

Tasks:
1. Apply the systemic remediations to `v13_discovery/semantic_extractor.py`:
   - Completely PURGE hardcoded bypass logic (`It is characterized by` and `Physical Geography Phenomenon` at lines 441-451).
   - Purge literal golden dataset string branches from `NoiseFilterGate` and `PATTERNS`.
   - Fix entity prefix truncation bug: replace `^(?:The|An|A)?\s*` with `^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>...)`.
   - Implement chained while-loop clause stripper for multi-prepositional introductory clauses.
   - Fix passive definition inversion (`"The Western Ghats are known as Sahyadri in Maharashtra"`).
   - Fix locative inversion trailing period bug in `LOCATIVE_INV_REGEX`.
   - Add generalized patterns for singular classifications, passive cause/effects, scientific processes, and measurement quantities.
2. Apply boundary refinements to `v13_discovery/normalizer.py`:
   - Update `TableParser` alignment row regex to `^[\:\-\=\s]{2,}$` to handle Pandoc `| ::: | ::: |`.
   - Update `LayoutDesegmenter.should_stitch_lines` to preserve lines breaking after abbreviations (`Dr.`, `Prof.`, `e.g.`) and decimal splits (`4.\n37`).
   - Implement classified dash joins in `stitch_lines` and `stitch_columns` (preserve `5000-6000`, space `two groups - terrestrial`, fuse `stratified`).
3. Execute and verify all test suites:
   - `python -m unittest -v tests/test_v13_adversarial_m2_challenge.py` (Must pass 20/20)
   - `python -m unittest -v tests/test_v13_adversarial_challenge.py` (Must pass 9/9)
   - `python -m unittest -v tests/test_v13_semantic_extractor.py` (Must pass 25/25)
   - `python run_e2e_tests.py` (Must pass 202/202)
   - `python scripts/validate_eval_set.py data/golden_eval_set.json` (Must pass)
   - `.\gradlew.bat clean testDebugUnitTest` (Must pass)
   - `.\gradlew.bat clean assembleDebug` (Must pass)
4. Write comprehensive handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m2_2\handoff.md
5. Send completion message back to parent orchestrator.

## 2026-09-04T15:50:00Z
Apply the systemic remediations to v13_discovery/semantic_extractor.py and boundary refinements to v13_discovery/normalizer.py.
Run all test suites:
- python -m unittest -v tests/test_v13_adversarial_m2_challenge.py (20/20)
- python -m unittest -v tests/test_v13_adversarial_challenge.py (9/9)
- python -m unittest -v tests/test_v13_semantic_extractor.py (25/25)
- python run_e2e_tests.py (202/202)
- python scripts/validate_eval_set.py data/golden_eval_set.json
- gradlew.bat clean testDebugUnitTest & assembleDebug
Write handoff.md and send completion message to parent orchestrator.
