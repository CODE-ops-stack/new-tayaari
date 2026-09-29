# Execution Plan — Orchestrator Generation 2

## Mission Objective
Drive project through Milestones M2 (Iteration 3), M3, M4, M5, and M6 to completion with 100% genuine implementations, 0 integrity violations, and full verification.

## Step-by-Step Plan

### Phase 1: Milestone 2 Iteration 3 Remediation & Authoritative Clean Gate
1. **Explorer Dispatch**:
   - Spawn 3 Explorers:
     - `teamwork_preview_explorer_m2_it3_1_rep`: Analyze PATTERNS and formulate generalized syntactic/linguistic grammar replacements for lines 358, 363, 458, 463, 572, completely purging dataset strings while handling variations (linking verbs, superlatives, comparative constructions, classification markers).
     - `teamwork_preview_explorer_m2_it3_2_rep`: Design comprehensive generalization verification suite (unseen counter-examples across all 14 intents, including auditor Experiments A, B, C) ensuring robust generalization without test-fitting.
     - `teamwork_preview_explorer_m2_it3_3_rep`: Design principled anaphoric pronoun handling and ungrounded pronoun rejection so isolated pronouns are not treated as valid primary entities without context.
2. **Worker Dispatch**:
   - Spawn `teamwork_preview_worker_m2_3` with explorer findings, strict anti-cheating warning, clear file ownership (`v13_discovery/semantic_extractor.py`, `v13_discovery/normalizer.py`, and test files).
   - Worker implements generalized grammar, verifies unit tests, runs generalization suites, and builds cleanly.
3. **Gate Review**:
   - Spawn 2 Reviewers (`teamwork_preview_reviewer`), 2 Challengers (`teamwork_preview_challenger`), and 1 Forensic Auditor (`teamwork_preview_auditor`).
   - Evaluate `GATE_STATUS.md`. Require APPROVE from all reviewers and challengers, and CLEAN from Forensic Auditor.

### Phase 2: Milestone 3 — 3-Approach Comparative Experimentation Framework
1. **Explorer Investigation**: Map the 3 viable approaches (e.g., Rule/Regex Semantic Synthesizer, Dependency-Tree Semantic Graph, and Local/API LLM Ingestion), provenance data structure, and evaluation metrics (Precision, Recall, FAR, FRR).
2. **Worker Implementation**: Ingest >=100 real source units, benchmark all 3 approaches, record metrics in `data/experiment_metrics.json`, and guarantee 6-link unbreakable provenance.
3. **Gate Verification**: Reviewers, Challengers, Forensic Auditor.

### Phase 3: Milestone 4 — Question & Defensible Distractor Engineering Engine
1. **Explorer Investigation**: Question Intent taxonomy, category compatibility matrices, distractor generation rules, absence of clueing/contradiction, Room DB `DistractorDissection` trap mappings.
2. **Worker Implementation**: Implement `v13_discovery/question_synthesizer.py`, generate >=100 high-quality candidate questions with 4 verified options and trap annotations, strictly forbidding quotation templates.
3. **Gate Verification**: Reviewers, Challengers, Forensic Auditor.

### Phase 4: Milestone 5 — Multi-Agent Auditing Quality Gate & Self-Repair
1. **Explorer Investigation**: Independent Cognitive Auditor, Exam-Fit Auditor, Adversarial Auditor architectures, audit feedback loop, systemic repair & complete regeneration cycle.
2. **Worker Implementation**: Implement `v13_discovery/auditors.py`, audit >=50 candidate questions, execute systemic repair, and re-run complete regeneration cycle.
3. **Gate Verification**: Reviewers, Challengers, Forensic Auditor.

### Phase 5: Milestone 6 — Android Integration, Final E2E Suite & Gradle Verification
1. **Explorer Investigation**: Sync formatted questions into `source-material/consolidated_grounding.md`, inspect Gradle assets copy task and Room database ingestion.
2. **Worker Implementation**: Write new regression tests (MCQ leakage, OCR fragments, multi-word entities, non-SVO facts, duplicates, provenance), update assets, run `testDebugUnitTest` and `assembleDebug`.
3. **Gate Verification**: Reviewers, Challengers, Forensic Auditor.
4. **Final Victory Report**: Synthesize evidence and notify parent.
