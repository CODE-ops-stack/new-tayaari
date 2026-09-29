# Project: V13 Educational Question Discovery Pipeline & Multi-Agent Auditing

## Architecture
The V13 pipeline replaces the brittle, single-regex V12 pipeline with an advanced semantic discovery, distractor engineering, multi-agent auditing, and Android integration system:

```
[Raw Educational Corpus: NCERT PDFs, Markdown, Text, JSON]
               │
               ▼
[Ingestion & Normalization: Layout Repair, Table Extraction, Watermark Cleansing]
               │
               ▼
[Semantic Knowledge Representation Engine: 14 Semantic Intents (NLP/LLM)]
               │
               ▼
[3-Approach Comparative Experimentation Framework (R5 Metrics)]
               │
               ▼
[Question & Defensible Distractor Synthesizer: Ontological Category Constraints]
               │
               ▼
[Multi-Agent Auditing Quality Gate: Cognitive + Exam-Fit + Adversarial Auditors]
               │
               ├─► [Failure Feedback Loop] ──► [Systemic Repair & Regeneration]
               │
               ▼
[Golden Provenance Registry: Question → Intent → Knowledge Unit → Evidence → Source]
               │
               ▼
[Android Integration: consolidated_grounding.md → Room DB (Questions + Distractor Dissections)]
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | V12 Forensic Baseline Analysis | Document V12 99.4% false rejection rate, failure points, and regression failures | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Golden Evaluation Dataset | Build >=50 positive and >=50 negative real corpus examples (111 items) | M1 | ORIGINAL_REQUEST §Acceptance 2 |
| 3 | Regression Test Suite Repair | Fix failing tests in test_hardening_regression.py and test environments | M1 | ORIGINAL_REQUEST §Acceptance 6 |
| 4 | 14-Intent Semantic Extraction Engine | Map text/tables to 14 semantic intents (definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of) | M2 | ORIGINAL_REQUEST §R2 |
| 5 | Table & Multi-Column Normalizer | Ingest markdown/PDF tables and repair vertical OCR text columns | M2 | Explorer Survey 2 |
| 6 | 3-Approach Comparative Benchmark | Evaluate 3 extraction paradigms on >=100 real source units with P/R/FAR metrics | M3 | ORIGINAL_REQUEST §R5, §Acceptance 1 |
| 7 | Unbreakable Provenance Tracking | Track Question → Intent → Knowledge Unit → Evidence → Source → Location | M3 | ORIGINAL_REQUEST §R5 |
| 8 | Natural Question Intent Formulation | Generate natural exam-fit question stems without generic quotation templates | M4 | ORIGINAL_REQUEST §R3, §Acceptance 5 |
| 9 | Ontological Distractor Engine | Generate distractors verified for category, grammar, plausibility, and no clueing | M4 | ORIGINAL_REQUEST §R3 |
| 10 | Distractor Dissection Generator | Produce diagnostic trap annotations (ABSOLUTE_WORDING, FACT_DISTORTION, etc.) matching Room DB | M4 | Spec Miner Survey 1 |
| 11 | Multi-Agent Auditing Quality Gate | Independent Cognitive, Exam-Fit, and Adversarial internal auditors | M5 | ORIGINAL_REQUEST §R4 |
| 12 | Systemic Repair & Regeneration Cycle | Audit >=50 questions, fix systemic flaws, and re-run complete generation cycle | M5 | ORIGINAL_REQUEST §Acceptance 3, 4 |
| 13 | New Comprehensive Regression Tests | Tests for MCQ leakage, OCR fragments, multi-word entities, non-SVO facts, duplicates, provenance | M6 | ORIGINAL_REQUEST §Acceptance 6 |
| 14 | Android Asset Integration | Inject verified questions into source-material/consolidated_grounding.md and verify copyMarkdownToAssets | M6 | Spec Miner Survey 1 |
| 15 | Android Unit Test Verification | Execute .\gradlew.bat clean testDebugUnitTest (100% pass) | M6 | ORIGINAL_REQUEST §Acceptance 7 |
| 16 | Android Debug APK Assembly | Execute .\gradlew.bat clean assembleDebug (Build Successful) | M6 | ORIGINAL_REQUEST §Acceptance 8 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Forensic Baseline & Golden Eval Set | Build 50+/50+ golden dataset, repair legacy test regressions | none | DONE |
| M2 | Advanced Semantic Knowledge Representation | Implement 14-intent extractor with NLP/LLM, table & column normalizer, generalized grammar | M1 | DONE |
| M3 | 3-Approach Comparative Experimentation | Benchmark 3 extraction paradigms on 100+ units with metrics & provenance | M2 | DONE |
| M4 | Question & Defensible Distractor Engine | Generate 100+ natural opportunities with category-constrained distractors & trap dissections | M3 | DONE |
| M5 | Multi-Agent Auditing & Self-Repair | Implement 3 independent auditors, audit 50+ questions, run repair & regeneration cycle | M4 | DONE |
| M6 | Regression Suite & Android Integration | New regression tests, consolidated_grounding sync, testDebugUnitTest, assembleDebug | M5 | IN_PROGRESS |

## Interface Contracts
### Ingestion & Normalizer ↔ Semantic Extractor
- Input: Raw corpus text/markdown blocks + source metadata `{sourceId, path, page/line}`
- Output: `NormalizedBlock(id, text, type: PROSE | TABLE, clean_sentences: List[str], metadata: dict)`

### Semantic Extractor ↔ Question Generator
- Input: `NormalizedBlock`
- Output: `KnowledgeNode(nodeId, intentType: 1 of 14, primaryEntity, relatedEntities, predicate, conditions, quantitativeData, rawEvidence, sourceLocation)`

### Question Generator ↔ Multi-Agent Auditor
- Input: `KnowledgeNode` + Domain Ontology
- Output: `CandidateQuestion(id, stem, options: dict[a-d], correctAnswer, explanation, distractorDissections: list[dict], provenance: dict, cognitiveDemand, examTarget)`

### Multi-Agent Auditor ↔ Final Quality Gate
- Input: `CandidateQuestion`
- Output: `AuditReport(questionId, cognitiveVerdict, examFitVerdict, adversarialVerdict, overallGate: PASS | REJECT, failureReasons: list[str])`

### Pipeline ↔ Android Application
- Input: Passed `CandidateQuestion` objects
- Output: Formatted markdown entries matching `DataImporter.kt` schema in `source-material/consolidated_grounding.md`

## Code Layout
- `v13_discovery/`: Core V13 Python package
  - `__init__.py`
  - `normalizer.py`: Table extraction, OCR/watermark cleaning, column layout repair
  - `semantic_extractor.py`: 14-intent knowledge representation engine
  - `experiments.py`: 3-approach comparative benchmark runner & metrics calculator
  - `provenance.py`: Provenance tracker (Question → Intent → Knowledge Unit → Evidence → Source)
  - `question_synthesizer.py`: Question & category-constrained distractor engine
  - `auditors.py`: Cognitive, Exam-Fit, and Adversarial auditing engines
  - `pipeline.py`: End-to-end V13 orchestrating pipeline
- `data/`: Evaluation datasets & experiment outputs
  - `golden_eval_set.json`: >=50 positive and >=50 negative examples
  - `experiment_metrics.json`: Comparative precision/recall/FAR metrics
- `tests/`: Test suites
  - `test_v13_semantic_extractor.py`
  - `test_v13_distractor_engine.py`
  - `test_v13_multi_agent_auditor.py`
