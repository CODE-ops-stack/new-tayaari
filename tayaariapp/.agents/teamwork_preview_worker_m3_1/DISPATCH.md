# Dispatch: Worker 1 Milestone 3 (worker_m3_1)

## 2026-09-06T07:17:31Z

**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m3_1`
**Parent Conversation ID**: `870ebe31-b7b8-4990-b9a6-83148369f1f4`
**Parent Orchestrator**: `teamwork_preview_orchestrator_4`
**Target Milestone**: Milestone 3 (3-Approach Comparative Experimentation Framework & Provenance Registry)

## Mandatory Reference Documents
1. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md` (Read first)
2. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md`
3. Explorer 1 Handoff: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_1\handoff.md`
4. Explorer 2 Handoff & Prototypes:
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_2\handoff.md`
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_2\proposed_experiments.py`
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_2\proposed_test_v13_experiments.py`
5. Explorer 3 Handoff & Prototypes:
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3\handoff.md`
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3\proposed_provenance.py`
   - `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3\test_proposed_provenance.py`

## Implementation Tasks
1. **Implement `v13_discovery/provenance.py`**:
   - Install the verified immutable 6-link `ProvenanceRecord` and `ProvenanceTracker` from Explorer 3.
   - Ensure complete coverage of `Question ID -> Intent -> Knowledge Unit -> Evidence -> Source -> Location`.
   - Ensure SHA-256 tamper-evident payload hashing and Merklized link failure diagnostics.
   - Implement `verify_provenance_chain` with dual boolean/tuple unpacking semantics and `audit_provenance_integrity`.
2. **Implement `tests/test_v13_provenance.py`**:
   - Install Explorer 3's 35-test unit suite.
   - Verify all tests pass cleanly.
3. **Implement `v13_discovery/experiments.py`**:
   - Install the 3-approach comparative benchmark runner from Explorer 2, integrating Explorer 1's 120-unit real corpus sampling capabilities and reference standards.
   - Wrap Approach A (Rule-Based NLP), Approach B (Structured LLM with offline `DeterministicLLMStub`), and Approach C (Hybrid Pipeline).
   - Ensure mathematical metric calculation for Precision, Recall, FAR, FRR, F1, Intent-level Micro/Macro-F1, Noise Rejection, and Latency/Throughput percentiles.
4. **Implement `tests/test_v13_experiments.py`**:
   - Install Explorer 2's unit test suite.
   - Verify all tests pass cleanly.
5. **Execute the Comparative Benchmark**:
   - Run the benchmark on >=100 real source units (using `data/golden_eval_set.json` 111 units and real corpus samples).
   - Generate and save `data/experiment_metrics.json` conforming to schema.
   - Document metrics in your report.
6. **Run Full Verification Suite**:
   - Run `python -m unittest discover -s tests -p "test_*.py"`
   - Run `python -m pytest tests/test_v13_experiments.py tests/test_v13_provenance.py`
   - Run `python run_e2e_tests.py`
7. **Write Complete Handoff Report**:
   - Write self-contained handoff report to `handoff.md`.
   - Send completion message to parent orchestrator.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A forensic auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
