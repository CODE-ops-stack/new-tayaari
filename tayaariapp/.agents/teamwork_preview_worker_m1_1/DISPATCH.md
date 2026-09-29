# Task Assignment: M1 Implementation Worker

You are teamwork_preview_worker_m1_1.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m1_1
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You own exclusively:
- `v5_discovery_pipeline.py`
- `test_hardening_regression.py`
- `test_discovery_regression.py`
- `scripts/validate_eval_set.py`
- `scripts/metrics_evaluator.py`
- `tests/test_golden_eval_set.py`
- `data/golden_eval_set.json`
- `docs/v12_forensic_baseline.json`

Implementation Tasks:
1. Ensure `data/golden_eval_set.json` is placed at `c:\Users\harsh\Downloads\tayaari\tayaariapp\data\golden_eval_set.json` (source from `.agents/teamwork_preview_explorer_m1_1/golden_eval_set.json`).
2. Install `scripts/validate_eval_set.py`, `scripts/metrics_evaluator.py`, and `tests/test_golden_eval_set.py` (source from `.agents/teamwork_preview_explorer_m1_3/proposed_validate_eval_set.py`, `proposed_metrics_evaluator.py`, `proposed_test_golden_eval_set.py`).
3. Apply the concrete fix to `v5_discovery_pipeline.py`:
   In `ClaimExtractor.extract()` (around lines 84-86), validate the sentence start before the relation loop:
   ```python
   # Validate sentence start before attempting relation matching
   first_word_match = re.match(r'^([A-Za-z]+)', sentence)
   if first_word_match and first_word_match.group(1) in self.BAD_SUBJECTS:
       self.rejected_inputs.append({"sentence": sentence, "reason": f"Invalid subject start '{first_word_match.group(1)}'"})
       continue
   ```
4. In `test_hardening_regression.py`, line 52:
   Update assertion to accept `"The Chota Nagpur plateau"`:
   ```python
   self.assertIn(claims[0]["subject"], ["The Chota Nagpur", "The Chota Nagpur plateau"])
   ```
5. In `test_discovery_regression.py`, replace the dummy `pass` statements in `test_rejects_unresolved_entities` and `test_rejects_fragmentary_claims` with active assertions on rejection reasons.
6. Create `docs/v12_forensic_baseline.json` documenting the consolidated forensic baseline metrics (46,121 sentences, 21 matches, 0.045% recall, 99.95% rejection, 1,771 lost facts, 100% false acceptance rate in V12 production run).
7. Execute and verify all tests:
   - `python -m unittest test_hardening_regression.py`
   - `python -m unittest test_discovery_regression.py`
   - `python -m unittest test_advanced_regression.py`
   - `python -m unittest test_generator_v3.py`
   - `python -m unittest discover -s tests -p "test_golden_eval_set.py"`
   - `python scripts/validate_eval_set.py data/golden_eval_set.json`
   - `.\gradlew.bat clean testDebugUnitTest`
   - `.\gradlew.bat clean assembleDebug`
8. Write comprehensive handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m1_1\handoff.md
9. Send completion message back to parent orchestrator.

## 2026-09-03T11:03:00Z
Task execution complete. All M1 deliverables implemented and verified.

