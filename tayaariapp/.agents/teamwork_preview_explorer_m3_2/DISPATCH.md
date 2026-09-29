# Dispatch: Explorer 2 Milestone 3 (explorer_m3_2)

**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_2`
**Parent Conversation ID**: `870ebe31-b7b8-4990-b9a6-83148369f1f4`
**Parent Orchestrator**: `teamwork_preview_orchestrator_4`

## Mandatory Reference Documents
1. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md` (Read first)
2. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md`
3. `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py`

## Tasks
1. Design the 3 comparative extraction paradigms for Milestone 3:
   - **Approach A (Rule-Based / Generalized Grammar & NLP)**: Current enhanced `SemanticExtractor`.
   - **Approach B (Structured LLM / In-Context Learning)**: `GeminiStructuredExtractor` with structured prompt design and robust offline deterministic mock/stub fallback when no API key is provided.
   - **Approach C (Hybrid Multi-Stage Pipeline)**: `HybridSemanticExtractor` that combines rule-based candidate proposal with model-driven intent refinement and noise rejection.
2. Formulate explicit mathematical definitions for all evaluation metrics:
   - Precision = TP / (TP + FP)
   - Recall = TP / (TP + FN)
   - False Acceptance Rate (FAR) = FP / (FP + TN)
   - False Rejection Rate (FRR) = FN / (TP + FN)
   - F1-Score = 2 * P * R / (P + R)
   - Latency / Throughput (units/sec)
3. Design the schema for `data/experiment_metrics.json` and the architecture of `v13_discovery/experiments.py`.
4. Provide drop-in class skeletons and unit test design (`tests/test_v13_experiments.py`).
5. Write complete exploration report to `handoff.md` and send message to parent orchestrator.

## 2026-09-06T07:11:12Z
Received task instructions to design 3-Approach Comparative Architecture & Metrics Engine for Milestone 3.

