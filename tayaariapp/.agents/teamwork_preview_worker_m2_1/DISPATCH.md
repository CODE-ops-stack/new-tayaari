# Task Assignment: M2 Implementation Worker

You are teamwork_preview_worker_m2_1.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m2_1
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md
Explorer 1 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_1\handoff.md
Explorer 2 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2\handoff.md
Explorer 3 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_3\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership:
You own exclusively:
- `v13_discovery/__init__.py`
- `v13_discovery/normalizer.py`
- `v13_discovery/semantic_extractor.py`
- `tests/test_v13_semantic_extractor.py`

Implementation Tasks:
1. Create `v13_discovery/__init__.py` exporting key classes (`NormalizedBlock`, `Normalizer`, `KnowledgeNode`, `SemanticExtractor`, `LinguisticSemanticExtractor`, `HybridSemanticExtractor`).
2. Implement `v13_discovery/normalizer.py`:
   - Incorporate reference implementation from Explorer 2 (`.agents/teamwork_preview_explorer_m2_2/proposed_normalizer.py`).
   - Implement `TableParser` (parse Markdown tables into structured factual propositions).
   - Implement `LayoutDesegmenter` (unmerge PascalCase headings, stitch line wraps).
   - Implement `WatermarkOcrCleaner` (strip watermarks, clean OCR noise, reject negative noise samples).
3. Implement `v13_discovery/semantic_extractor.py`:
   - Incorporate reference architecture from Explorer 1 (`.agents/teamwork_preview_explorer_m2_1/handoff.md`).
   - Define `KnowledgeNode` data model with full semantic slotting (`intent_type`, `primary_entity`, `predicate`, `secondary_entities`, `conditions`, `quantitative_data`, `raw_evidence`, `provenance`).
   - Implement `NoiseFilterGate` (rejects noise at 0ms latency).
   - Implement `LinguisticSemanticExtractor` supporting all 14 intents with discourse clause stripping and passive inversion.
   - Implement `HybridSemanticExtractor` combining fast deterministic parsing with Gemini API fallback where needed.
4. Install `tests/test_v13_semantic_extractor.py`:
   - Incorporate test suite from Explorer 3 (`.agents/teamwork_preview_explorer_m2_3/proposed_test_v13_semantic_extractor.py`).
   - Verify that all 25 unit tests pass cleanly.
5. Execute and verify all suites:
   - `python -m unittest tests/test_v13_semantic_extractor.py`
   - `python run_e2e_tests.py`
   - `python scripts/validate_eval_set.py data/golden_eval_set.json`
   - `.\gradlew.bat clean testDebugUnitTest`
   - `.\gradlew.bat clean assembleDebug`
6. Write comprehensive handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m2_1\handoff.md
7. Send completion message back to parent orchestrator.
