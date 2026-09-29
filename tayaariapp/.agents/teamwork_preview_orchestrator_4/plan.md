# Plan — Project Orchestrator Generation 4

## Objective
Verify and close Milestone 2 Gate 5 (Semantic Extractor & Normalizer), then execute Milestones 3, 4, 5, and 6 to achieve complete delivery and Victory Audit readiness.

## Step-by-Step Plan
1. **Gate 5 Evaluation for Milestone 2**:
   - Dispatch 2 Reviewers (`teamwork_preview_reviewer`) to verify code quality, tests, interface conformance, and edge case coverage.
   - Dispatch 2 Challengers (`teamwork_preview_challenger`) to empirically stress-test generalization, boundary conditions, anti-overfitting, and all 111 golden evaluation items.
   - Dispatch 1 Forensic Auditor (`teamwork_preview_auditor`) to independently execute full AST scans, n-gram overlap checks, token search, and integrity forensics against golden eval set.
   - Collect results into `GATE_STATUS.md`.
   - Gate verdict: Require unanimous APPROVE and CLEAN. Mark Milestone 2 DONE.

2. **Milestone 3 Execution: 3-Approach Comparative Experimentation Framework**:
   - Dispatch Explorers / Workers to build and run 3-approach comparative benchmark on >=100 real source units:
     * Approach A: Rule-Based / Generalized Grammar & NLP Dependency Patterns.
     * Approach B: Few-Shot In-Context Learning / Structured LLM Extraction (Gemini API with offline mock/stub deterministic fallback).
     * Approach C: Hybrid Pipeline (Rule-based candidate extraction + LLM semantic classification/verification).
   - Document metrics: Precision, Recall, False Acceptance Rate (FAR), False Rejection Rate (FRR), throughput. Save in `data/experiment_metrics.json`.
   - Build Unbreakable Provenance Registry (`v13_discovery/provenance.py`): Question -> Intent -> Knowledge Unit -> Evidence -> Source -> Location.
   - Gate evaluation (Reviewers, Challengers, Forensic Auditor) -> Mark M3 DONE.

3. **Milestone 4 Execution: Question & Defensible Distractor Engineering Engine**:
   - Build `v13_discovery/question_synthesizer.py`:
     * Explicit Question Intents (Recall, Contrast, Sequence, Cause-Effect, etc.) without generic quotation templates.
     * Ontological Distractor Engine: Category compatibility, grammatical fit, semantic plausibility, evidence support, absence of clueing/contradiction.
     * Distractor Dissection Generator: Diagnostic trap annotations (ABSOLUTE_WORDING, FACT_DISTORTION, TEMPORAL_ANACHRONISM, etc.) compatible with Android Room DB schema.
   - Gate evaluation (Reviewers, Challengers, Forensic Auditor) -> Mark M4 DONE.

4. **Milestone 5 Execution: Multi-Agent Auditing Quality Gate & Self-Repair**:
   - Build `v13_discovery/auditors.py`:
     * Cognitive Auditor (Bloom taxonomy: RECALL, UNDERSTAND, COMPARE, APPLY).
     * Exam-Fit Auditor (UPSC, BPSC, SSC CGL syllabus & question style).
     * Adversarial Auditor (ambiguity, clueing, factual errors, grammar, leakages).
   - Execute auditing on >=50 candidate questions.
   - Implement systemic repair feedback loop and run a complete regeneration cycle after audit failures.
   - Gate evaluation -> Mark M5 DONE.

5. **Milestone 6 Execution: Regression Suite, Android Asset Sync & Gradle Build Verification**:
   - Implement new comprehensive regression tests (`tests/test_v13_new_regressions.py`).
   - Sync accepted questions into `source-material/consolidated_grounding.md`.
   - Execute and verify Android Gradle commands:
     * `.\gradlew.bat clean testDebugUnitTest` (100% pass)
     * `.\gradlew.bat clean assembleDebug` (BUILD SUCCESSFUL)
   - Final end-to-end verification.
   - Prepare final documentation and notify Sentinel for Victory Audit.
