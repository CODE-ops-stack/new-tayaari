# Plan: Project Orchestrator Generation 3

## Immediate Objective: Milestone 2 Iteration 4 & Full Pipeline Delivery
We are executing Generation 3 of the V13 Question Discovery and Multi-Agent Auditing project. Milestone 1 is completed. Milestone 2 Iteration 3 achieved an authoritative CLEAN forensic audit verdict, and Explorers 1, 2, and 3 for Iteration 4 have provided complete drop-in remediations for all Challenger defects.

## Step-by-Step Execution Plan

### Step 1: Milestone 2 Iteration 4 Execution
- Dispatch `teamwork_preview_worker` (worker_m2_5) to apply the unified remediation patch combining:
  1. Explorer 1: 8 syntactic remediations (past-tense superlatives, open taxonomic class for member-of, comma lookaheads in comparison, compound attribute participles, comma-formatted number parser, sequence colon handling, robust passive definition inversion, spatial prepositions in part-of).
  2. Explorer 2: Noise filtering & desegmentation (interrogative rejection gate in NoiseFilterGate and fallback, trailing hyphen / soft-hyphen desegmentation in LayoutDesegmenter.is_heading, incomplete fragment rejection, text normalization in DocumentNormalizer and semantic_extractor).
  3. Explorer 3: DiscourseContext number agreement & coreference architecture (3-tier plurality detection with verb agreement cues, PROPER_SINGULAR_OVERRIDES, PLURAL_ENTITY_RECOGNITION, leading possessive pronoun detection & ungrounded rejection, kinematic verbs).
  4. Test suite updates: Update assertions in `tests/test_v13_challenger_stress.py` to assert the corrected behavior.
  5. Run all test suites: `tests/test_v13_semantic_extractor.py`, `tests/test_v13_generalization.py`, `tests/test_v13_challenger_stress.py`, `tests/test_v13_adversarial_challenge.py`, E2E suite, and verify zero banned strings.
- Monitor worker completion.

### Step 2: Milestone 2 Gate 4 Verification
- Dispatch Reviewers (2 independent reviewers: `teamwork_preview_reviewer`).
- Dispatch Challengers (2 empirical challengers: `teamwork_preview_challenger`).
- Dispatch Forensic Auditor (`teamwork_preview_auditor`) for static & dynamic integrity analysis.
- Evaluate Gate 4 in `GATE_STATUS.md`: All Reviewers APPROVE, Challengers APPROVE, Forensic Auditor CLEAN.
- Mark Milestone 2 DONE in `PROJECT.md` and `progress.md`.

### Step 3: Milestone 3 — 3-Approach Comparative Experimentation Framework
- Assess and decompose Milestone 3:
  - Benchmark 3 viable extraction approaches (e.g. Pattern-Based Linguistic, Dependency/Constituency Parser, LLM/Semantic Representation) across >=100 real source units.
  - Document precision, recall, false accept rate (FAR), false reject rate (FRR) in `data/experiment_metrics.json`.
  - Implement and verify unbreakable provenance registry (`v13_discovery/provenance.py`).
- Dispatch Worker, Reviewers, Challengers, and Forensic Auditor.
- Gate evaluation and pass Milestone 3.

### Step 4: Milestone 4 — Question & Defensible Distractor Engineering Engine
- Assess and decompose Milestone 4:
  - Natural question stem synthesis matching 14 semantic intents (no generic quotation templates).
  - Category-constrained defensible distractor generation with semantic trap dissections (ABSOLUTE_WORDING, FACT_DISTORTION, etc.).
  - Distractor provenance and test verification.
- Dispatch Worker, Reviewers, Challengers, and Forensic Auditor.
- Gate evaluation and pass Milestone 4.

### Step 5: Milestone 5 — Multi-Agent Auditing Quality Gate & Self-Repair
- Assess and decompose Milestone 5:
  - Independent Cognitive Demand Auditor, Exam-Fit Auditor, and Adversarial Auditor (`v13_discovery/auditors.py`).
  - Audit >=50 questions, execute systemic repair & regeneration cycle.
- Dispatch Worker, Reviewers, Challengers, and Forensic Auditor.
- Gate evaluation and pass Milestone 5.

### Step 6: Milestone 6 — Android Integration, Final E2E Suite, Gradle Verification
- Assess and decompose Milestone 6:
  - New comprehensive regression test suites.
  - Sync verified questions into `source-material/consolidated_grounding.md` and verify `copyMarkdownToAssets`.
  - Android Gradle verification: `.\gradlew.bat clean testDebugUnitTest` and `.\gradlew.bat clean assembleDebug`.
- Dispatch Worker, Reviewers, Challengers, and Forensic Auditor.
- Final gate evaluation and pass Milestone 6.

### Step 7: Final Synthesis & Victory Report to Sentinel
- Compile complete verification evidence across all milestones.
- Present final report to Sentinel for independent Victory Audit.
