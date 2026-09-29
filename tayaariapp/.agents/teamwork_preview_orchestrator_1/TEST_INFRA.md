# E2E Test Infra: V13 Educational Question Discovery Pipeline

## Test Philosophy
- Requirement-driven, opaque-box testing derived from ORIGINAL_REQUEST.md.
- Independent of implementation details; exercises pipeline and Android integration as black boxes.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial Testing + Real-World Workload Testing.

## Feature Inventory & Test Coverage Goals
| # | Feature | Source (Requirement) | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Workload) |
|---|---------|----------------------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| 1 | Forensic Baseline Analysis | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 2 | Golden Evaluation Dataset | ORIGINAL_REQUEST §Acceptance 2 | 5 | 5 | ✓ | ✓ |
| 3 | Regression Test Suite Repair | ORIGINAL_REQUEST §Acceptance 6 | 5 | 5 | ✓ | ✓ |
| 4 | 14-Intent Semantic Extraction | ORIGINAL_REQUEST §R2 | 14 (1/intent) | 10 | ✓ | ✓ |
| 5 | Table & Multi-Column Normalizer | Explorer Survey 2 | 5 | 5 | ✓ | ✓ |
| 6 | 3-Approach Comparative Benchmark | ORIGINAL_REQUEST §R5, §Acceptance 1 | 5 | 5 | ✓ | ✓ |
| 7 | Unbreakable Provenance Tracking | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |
| 8 | Natural Question Intent Formulation | ORIGINAL_REQUEST §R3, §Acceptance 5 | 5 | 5 | ✓ | ✓ |
| 9 | Ontological Distractor Engine | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 10 | Distractor Dissection Generator | Spec Miner Survey 1 | 5 | 5 | ✓ | ✓ |
| 11 | Multi-Agent Auditing Quality Gate | ORIGINAL_REQUEST §R4 | 6 (2/auditor) | 6 | ✓ | ✓ |
| 12 | Systemic Repair & Regeneration | ORIGINAL_REQUEST §Acceptance 3, 4 | 5 | 5 | ✓ | ✓ |
| 13 | New Comprehensive Regression Tests | ORIGINAL_REQUEST §Acceptance 6 | 6 (1/leakage type) | 6 | ✓ | ✓ |
| 14 | Android Asset Integration | Spec Miner Survey 1 | 5 | 5 | ✓ | ✓ |
| 15 | Android Unit Test Verification | ORIGINAL_REQUEST §Acceptance 7 | 5 | 5 | ✓ | ✓ |
| 16 | Android Debug APK Assembly | ORIGINAL_REQUEST §Acceptance 8 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **E2E Test Runner**: `python -m unittest discover -s tests -p "test_e2e_*.py"` & `.\gradlew.bat clean testDebugUnitTest`
- **Output Artifacts**: Test reports in `test_reports/`, `GATE_STATUS.md`, and `TEST_READY.md`.
- **Pass/Fail Semantics**: All test suites must return exit code 0. Zero tolerance for false positives, unverified distractors, or broken provenance links.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full NCERT Physical Geography Ingestion | Normalizer, 14-Intent Extractor, Provenance | High |
| 2 | Comparative Benchmark Execution on 100+ Units | 3 Approaches, Evaluation Dataset, Metric Computation | High |
| 3 | Question & Ontological Distractor Generation | Synthesizer, Category Verification, Trap Annotations | High |
| 4 | Multi-Agent Auditing Gate & Regeneration Cycle | Cognitive, Exam-Fit, Adversarial Auditors, Feedback Repair | High |
| 5 | End-to-End Pipeline to Android DB Verification | Grounding Markdown Injection, Asset Sync, Robolectric Room Seeding | High |

## Coverage Thresholds
- Tier 1: ≥80 test cases across 16 features
- Tier 2: ≥80 boundary and corner cases
- Tier 3: Pairwise coverage of all critical pipeline interface combinations
- Tier 4: ≥5 comprehensive end-to-end real-world workload scenarios
