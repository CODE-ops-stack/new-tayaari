# Orchestration Plan: V13 Educational Question Discovery Pipeline

## Overview
This plan governs the end-to-end development, experimentation, verification, multi-agent auditing, and Android integration of the V13 educational question discovery pipeline.

## Phases

### Phase 0: Survey & Specification Mining
- Spawn 3 parallel survey subagents:
  1. `teamwork_preview_explorer_survey_1`: V12 pipeline forensics, failure modes, existing extraction scripts, current questions, regression tests.
  2. `teamwork_preview_explorer_survey_2`: Real source-material corpus analysis, content formats, lost knowledge types, quantity and diversity.
  3. `teamwork_preview_spec_miner_survey_1`: Android app architecture, Gradle configuration, test commands, integration boundaries between pipeline & Android app.
- Synthesize findings into `PROJECT.md` (Feature Inventory, Architecture, Code Layout, Interface Contracts) and `TEST_INFRA.md`.

### Phase 1: Milestone Decomposition & Track Setup
- Implementation Track:
  - M1: Forensic Baseline, Corpus Profiling & Golden Evaluation Set (R1, R5 eval set: >=50 positive, >=50 negative).
  - M2: Advanced Semantic Knowledge Representation Engine (R2: 14+ semantic intents, spacy/nltk/LLM integration, zero pure SVO regex).
  - M3: 3-Approach Comparative Experimentation Framework (R5: precision, recall, false acceptance/rejection on >=100 units).
  - M4: Question & Defensible Distractor Generation Engine (R3: explicit Question Intents, verified distractors, no generic quote templates).
  - M5: Multi-Agent Auditing Quality Gate & Self-Repair Regeneration Cycle (R4, Acceptance 3 & 4: Cognitive, Exam-Fit, Adversarial auditors, full repair cycle).
  - M6: Android Integration, Final E2E Suite, and Full Build Verification (Acceptance 6, 7, 8: regression tests, gradlew clean testDebugUnitTest, gradlew clean assembleDebug).
- E2E Testing Track:
  - Independent requirement-driven test suite (Tiers 1-4).
  - Publishes `TEST_READY.md`.

### Phase 2: Execution via Standard Iteration Loops
- For each milestone: Explorer (3) -> Worker (1) -> Reviewer (2) -> Challenger (2) -> Forensic Auditor (1) -> Gate.
- Forensic Auditor has binary veto.
- Strict AND gate criteria.

### Phase 3: Final Verification & Handover
- Tier 5 Adversarial Coverage Hardening.
- Complete Android app build & unit test verification.
- Comprehensive handoff report and Sentinel notification.
