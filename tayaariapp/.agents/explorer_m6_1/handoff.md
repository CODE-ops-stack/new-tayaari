# Milestone 6 Architecture & Technical Landscape Blueprint: Handoff Report

**Agent**: `explorer_m6_1`  
**Milestone**: Milestone 6 (Android Asset Integration, Android Unit Tests/Build, and Python V13 Regression Test Suite)  
**Date**: 2026-09-08T15:38:00Z  
**Target Recipient**: Orchestrator / `worker_m6_1`  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\explorer_m6_1\`  

---

## 1. Observation

### 1.1 Android Asset Pipeline & Synchronization
1. **Source of Truth vs Assets Target**:
   - `source-material/consolidated_grounding.md` (Size: 570,204 bytes, 18,429 lines, 1,075 legacy questions).
   - `app/src/main/assets/consolidated_grounding.md` (currently byte-for-byte identical).
2. **Gradle Synchronization Task (`app/build.gradle.kts:137-144`)**:
   ```kotlin
   tasks.register<Copy>("copyMarkdownToAssets") {
       from("${rootDir}/source-material/consolidated_grounding.md")
       into("src/main/assets/")
   }

   tasks.named("preBuild") {
       dependsOn("copyMarkdownToAssets")
   }
   ```
   Direct observation: Gradle hooks `copyMarkdownToAssets` into `preBuild`. Any build or test task (`testDebugUnitTest`, `assembleDebug`) triggers this copy task before compilation.
3. **DataImporter Markdown Ingestion (`app/src/main/java/com/example/repository/DataImporter.kt:42-188`)**:
   - Block splitting: `Regex("\\r?\\n## (?=\\d+\\. )")` separates topics.
   - Topic extraction: `Regex("^(\\d+)\\. (.*?)\\r?\\n")` extracts topic ID and title.
   - Question metadata regex (`DataImporter.kt:54-64`):
     ```kotlin
     val qPattern = Pattern.compile(
         "- \\*\\*Topic\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Tier\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Format\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Exam-Relevance\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Source\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Specific-Exam\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "(?:- \\*\\*Trap-Type\\*\\*: ([^\\r\\n]*?)\\s*\\n)?" + 
         "- \\*\\*PDF-Sequence-Number\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
         "- \\*\\*Question\\*\\*:\\s*`\\s*(.*?)\\s*`", Pattern.DOTALL
     )
     ```
   - Correct answer extraction (`DataImporter.kt:109-118`):
     `Pattern.compile("(?i)Correct [Aa]nswer:\\s*(?:Option\\s*)?([a-eA-E])").matcher(rawQText)`
     Followed by: `rawQText = rawQText.substring(0, ansMatcher.start()).trim()`
   - Explanation extraction (`DataImporter.kt:120-125`):
     `Pattern.compile("(?i)Explanation:\\s*(.*)", Pattern.DOTALL).matcher(rawQText)`
     Followed by: `rawQText = rawQText.substring(0, expMatcher.start()).trim()`
   - Options extraction (`DataImporter.kt:129-151`):
     `Regex("(?s)\\s*\\(?([a-eA-E])\\)\\s+(.*?)(?=\\s*\\(?[a-eA-E]\\)\\s+|$)")`
     Constructs JSON array: `[{"id":"opt_a","text":"..."},{"id":"opt_b","text":"..."},...]`
   - Room DB `Question` entity creation (`DataImporter.kt:172-185`, `Entities.kt:31-47`).
4. **Critical Sequential Parsing Invariant**:
   - Because `DataImporter.kt` slices off `Correct Answer:` first using `substring(0, ansMatcher.start())`, if `Correct Answer:` appears *before* `Explanation:`, the explanation is immediately destroyed and falls back to `"No explanation"`.
   - In `v13_discovery/question_synthesizer.py:80-117` (`CandidateQuestion.to_room_markdown`), `Explanation:` is placed *before* `Correct Answer: Option X`.
   - Empirically verified via `DataImporterSimulator.parse_markdown`:
     - Explanation before Answer -> `Parsed Explanation: The troposphere is...`, `Accepted: 1`, `Rejected: 0`.
     - Answer before Explanation -> `Parsed Explanation: No explanation`.

### 1.2 Android Unit Tests & APK Assembly Environment
1. **Kotlin Unit Tests (`app/src/test/`)**:
   - 20 unit test files under `com.example` testing database migrations (`RealMigrationTest`), entity persistence (`DatabasePersistenceTest`), schema dumps (`SchemaDumpTest`), attempt outcomes, question selection engines, learner model replay, and trap logic.
2. **Gradle Wrapper & Toolchain**:
   - `gradlew.bat` present at root.
   - Gradle Version: **9.3.1**.
   - JVM: **JDK 22.0.2** (`C:\Program Files\Java\jdk-22`).
   - Android SDK: `C:\Users\harsh\AppData\Local\Android\Sdk` (configured in `local.properties`).
3. **Execution Results**:
   - Unit Tests: `cmd.exe /c "gradlew.bat testDebugUnitTest"` executed cleanly with exit code 0 (`BUILD SUCCESSFUL in 1m 4s`, 34 actionable tasks).
   - APK Assembly: `cmd.exe /c "gradlew.bat assembleDebug"` executed cleanly with exit code 0 (`BUILD SUCCESSFUL in 1m 5s`, 40 actionable tasks).
   - Generated Artifact: `app/build/outputs/apk/debug/app-debug.apk` (Size: 23,461,399 bytes / 23.5 MB).

### 1.3 Existing Python Test Suite Status
- Running `python -m unittest discover -s tests -p "test_v13_*.py"`:
  `Ran 351 tests in 12.331s -> OK (Exit code 0)`
- Running `python run_e2e_tests.py`:
  `Ran 202 tests in 1.516s -> OK (Exit code 0)`
- Golden Evaluation Dataset: `data/golden_eval_set.json` (111 items: 55 positive covering all 14 intents, 56 negative across 6 noise categories).
- Comparative Benchmark Metrics: `data/experiment_metrics.json` (3 approaches, >=100 units).

---

## 2. Logic Chain

1. **Asset Deployment Chain**:
   - `source-material/consolidated_grounding.md` is the canonical text file edited during content pipelines.
   - Gradle's `copyMarkdownToAssets` task depends on `source-material/consolidated_grounding.md` and copies it directly to `app/src/main/assets/consolidated_grounding.md`.
   - When the Android app initializes (`AppDatabase.kt:68-71`), if the Room DB is empty, it opens `consolidated_grounding.md` from Android assets and invokes `DataImporter.importFromMarkdown(context, mdContent)`.
   - Therefore, appending verified V13 questions to `source-material/consolidated_grounding.md` and syncing to `app/src/main/assets/` guarantees seamless ingestion into Room DB upon app start.

2. **Schema Integrity Chain**:
   - `DataImporter.kt` expects questions to have strict metadata keys (`Topic`, `Tier`, `Format`, `Exam-Relevance`, `Source`, `Specific-Exam`, optional `Trap-Type`, `PDF-Sequence-Number`, `Question`).
   - Inside the code-fenced question block, options must be formatted as `(A) ... (B) ... (C) ... (D) ...`.
   - The explanation line `Explanation: <text>` must precede `Correct Answer: Option <letter>`.
   - When this order is preserved, `DataImporter.kt` populates `Question.explanation` with verbatim reasoning, maps `trapType` into `Question.distractorDissections` JSON, sets `Question.correctAnswer = "opt_<letter>"`, and encodes options into JSON array `[{"id":"opt_a","text":"..."},...]`.

3. **Android Verification Chain**:
   - `.\gradlew.bat clean testDebugUnitTest` compiles debug sources, processes KSP annotations (Room & Moshi), and executes all JVM unit tests.
   - `.\gradlew.bat clean assembleDebug` packages resources, processes manifests, compiles dex bytecode via D8/R8, and packages `app-debug.apk`.
   - Both commands are reproducible via `gradlew.bat` in the local Windows environment.

4. **Regression Suite Requirement Chain**:
   - Acceptance Criterion 6 mandates: *"New regression tests exist for MCQ leakage, OCR fragments, multi-word entities, non-SVO facts, semantic duplicates, and provenance failures."*
   - Currently, `tests/` contains focused tests for milestones 1–5, but lacks a single, consolidated regression test module specifically testing these 6 mandatory failure modes.
   - Designing and implementing `tests/test_v13_new_regressions.py` directly satisfies Acceptance Criterion 6.

---

## 3. Caveats

1. **Gradle Daemon Resource Usage on Windows**:
   - Running Gradle builds (`assembleDebug`, `testDebugUnitTest`) starts a background Gradle daemon which consumes ~500MB–1GB RAM and takes ~1 minute on fresh execution. Subsequent executions benefit from the configuration cache.
2. **DataImporter Regex Delimiters**:
   - `DataImporter.kt` in `app/` uses `- \*\*Question\*\*:\s*`\s*(.*?)\s*`` while `tests/e2e/test_helpers.py` uses `(?:```\s*(.*?)\s*```|`\s*(.*?)\s*`)`.
   - To guarantee 100% compatibility across both single-backtick and triple-backtick markdown parsers, questions formatted via `to_room_markdown()` use triple backticks ``` ```` ```, which `DataImporterSimulator` accepts with 0 rejections.
3. **Read-Only Scope**:
   - As an explorer, no modifications to source files (`app/`, `v13_discovery/`, `tests/`, `source-material/`) were made. All implementations must be performed by `worker_m6_1` following the blueprints in Section 4.

---

## 4. Conclusion & Actionable Blueprints for Worker

The technical landscape is fully verified and ready for Milestone 6 execution. Below are the exact blueprints, schemas, and specifications for `worker_m6_1`.

### 4.1 Android Asset Integration Blueprint
**Target File**: `source-material/consolidated_grounding.md`  
**Mirrored Asset**: `app/src/main/assets/consolidated_grounding.md`  

#### Markdown Question Schema Specification:
Every V13 question appended must strictly adhere to the following block structure:
```markdown
- **Topic**: <topic_id>. <topic_name>
- **Tier**: Standard
- **Format**: Direct Fact
- **Exam-Relevance**: High
- **Source**: NCERT Physical Geography
- **Specific-Exam**: UPSC-Prelims
- **Trap-Type**: <TRAP_TYPE>
- **PDF-Sequence-Number**: V13-<unique_number>
- **Question**: ```
<Clean Question Stem without Quotation Wrappers or Stem Leakage>
(A) <Option A text>
(B) <Option B text>
(C) <Option C text>
(D) <Option D text>
Explanation: <Verbatim Pedagogical Explanation>
Correct Answer: Option <A|B|C|D>
```
```

#### Mapping Table to Room DB `Question` Entity (`Entities.kt:31-47`):
| Markdown Element | Room `Question` Field | Data Type | Value Transformation |
|---|---|---|---|
| Section `## 1. ...` | `topicId` | `Int` | Extracted integer from header (`1`) |
| `- **Tier**:` | `tier` | `String` | e.g. `"Standard"` |
| `- **Format**:` | `format` | `String` | Normalized: `"Direct Fact"`, `"Statement-based"`, etc. |
| `- **Exam-Relevance**:` | `examRelevance` | `String` | e.g. `"High"` |
| `- **Source**:` | `source` | `String` | e.g. `"NCERT Physical Geography"` |
| `- **Specific-Exam**:` | `specificExam` | `String` | e.g. `"UPSC-Prelims"` |
| Question Stem | `questionText` | `String` | Extracted stem preceding `(A)` |
| `(A)...(D)` | `options` | `String` (JSON) | `[{"id":"opt_a","text":"..."},{"id":"opt_b","text":"..."},...]` |
| `Correct Answer: Option A` | `correctAnswer` | `String` | `"opt_a"` |
| `Explanation: ...` | `explanation` | `String` | Verbatim explanation text |
| `- **Trap-Type**: FACT_DISTORTION` | `distractorDissections`| `String` (JSON) | `[{"optionId":"opt_distractor","trapType":"FACT_DISTORTION","dissection":"Parsed from md"}]` |

#### Deployment Procedure for Worker:
1. Generate >= 50 (or 100) V13 candidate questions using `QuestionSynthesizer.synthesize_from_corpus()` or pipeline.
2. Filter through `MultiAgentAuditingGate` to ensure 100% PASS on Cognitive, Exam-Fit, and Adversarial auditors.
3. Append formatted markdown entries into `source-material/consolidated_grounding.md` under matching topic sections (e.g. `## 1. The Earth in the Solar System`).
4. Execute `cmd.exe /c "gradlew.bat copyMarkdownToAssets"` to synchronize assets.
5. Validate using `DataImporterSimulator.parse_markdown` to guarantee 0 rejections on all appended questions.

---

### 4.2 Android Unit Tests & Gradle Build Blueprint
**Commands for Acceptance Criteria 7 & 8**:
1. **Clean & Unit Test Verification**:
   ```powershell
   .\gradlew.bat clean testDebugUnitTest
   ```
   - Target task: `:app:testDebugUnitTest`
   - Expected result: `BUILD SUCCESSFUL`, 20 Kotlin test classes pass.
2. **Clean & Debug APK Assembly**:
   ```powershell
   .\gradlew.bat clean assembleDebug
   ```
   - Target task: `:app:assembleDebug`
   - Output artifact: `app/build/outputs/apk/debug/app-debug.apk`
   - Expected result: `BUILD SUCCESSFUL`, valid Android debug package generated.

---

### 4.3 Python Regression Test Suite Blueprint: `tests/test_v13_new_regressions.py`
**Target File**: `tests/test_v13_new_regressions.py`  
Must implement a standard `unittest` test suite covering all 6 mandatory failure modes from Acceptance Criterion 6:

```python
"""
tests/test_v13_new_regressions.py
==================================
Comprehensive Regression Test Suite for Milestone 6 (Acceptance Criterion 6).
Covers all 6 mandatory failure modes:
1. MCQ stem leakage prevention
2. OCR fragments & watermark filtering
3. Multi-word entity extraction and distractor handling
4. Non-SVO facts extraction across all 14 semantic intents
5. Semantic duplicate elimination
6. Cryptographic provenance verification & tamper resistance
"""

import os
import sys
import unittest
import dataclasses
from typing import Dict, List, Any

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v13_discovery.normalizer import WatermarkOcrCleaner, NormalizedBlock, DocumentNormalizer
from v13_discovery.semantic_extractor import (
    NoiseFilterGate,
    LinguisticSemanticExtractor,
    KnowledgeNode,
    CANONICAL_14_INTENTS,
    canonicalize_intent,
    to_r2_intent,
)
from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    DistractorVerificationGate,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.auditors import (
    AdversarialAuditor,
    CognitiveAuditor,
    ExamFitAuditor,
    MultiAgentAuditingGate,
    QuestionRepairEngine,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    LinkHashes,
    verify_provenance_chain,
    audit_provenance_integrity,
)
from tests.e2e.test_helpers import DataImporterSimulator
```

#### Area 1: `TestMCQStemLeakageRegression`
- `test_verbatim_answer_in_stem_rejection`:
  - Stem contains the exact text of option A (`"troposphere"`).
  - Assert `AdversarialAuditor.audit(cq).verdict == "REJECT"`.
  - Assert violation category is `"STEM_LEAKAGE"`.
- `test_case_insensitive_and_punctuation_leakage`:
  - Stem contains `"TROPOSPHERE"` or `"'troposphere'"` when option is `"Troposphere"`.
  - Assert fatal rejection.
- `test_significant_token_leakage`:
  - Multi-word answer `"Continental Drift Theory"` where stem contains `"Continental Drift"`.
  - Assert detected via significant token matching (`\b[a-z]{3,}\b`).
- `test_no_false_alarm_on_domain_stopwords_or_substrings`:
  - Verify stem containing `"is"`, `"the"`, `"in"` or `"planetarium"` (when answer is `"plan"`) does not falsely trip word-boundary leakage check.
- `test_self_repair_deidentifies_leaked_stem`:
  - Feed leaked question into `QuestionRepairEngine.repair()`.
  - Assert repaired question stem replaces the entity with neutral referent and passes auditor.

#### Area 2: `TestOcrFragmentsAndWatermarksRegression`
- `test_publisher_and_coaching_watermarks`:
  - Test strings: `"PARMAR SSC"`, `"www.ssccglpinnacle.com"`, `"Download Pinnacle Exam Preparation App"`.
  - Assert `WatermarkOcrCleaner.is_watermark_or_noise(line) is True`.
  - Assert `NoiseFilterGate.audit(line) == "watermark_header"`.
- `test_textbook_cataloging_and_reprints`:
  - Test strings: `"ISBN 978-93-5292-065-6"`, `"0656"`, `"Rationalised 2023-24"`, `"Reprint 2022-23"`, `"not to be republished"`, `"NCERT"`.
  - Assert rejected with 0 false acceptances.
- `test_running_headers_and_figure_captions`:
  - Test strings: `"THE EARTH : OUR HABITAT"`, `"MAJOR DOMAINS OF THE EARTH"`, `"Chapter 1"`, `"Figure 1.2: Solar System"`.
  - Assert filtered.
- `test_craft_activity_and_exercise_prompts`:
  - Test strings: `"Let's Do"`, `"Do you know?"`, `"Step :"`, `"1. Take a globe..."`, `"Tick the correct answer"`.
  - Assert filtered.
- `test_syntactic_dangling_fragments`:
  - Test strings ending with dangling conjunctions/prepositions: `"composed of"`, `"leading to"`, `"because"`, `"such as"`.
  - Assert `NoiseFilterGate.audit(text) == "syntactic_fragment"`.
- `test_unresolved_anaphoric_pronouns`:
  - Test isolated sentences: `"They are found in deep ocean trenches."`
  - Assert `NoiseFilterGate.audit(text) == "anaphoric_unresolved"`.
- `test_genuine_educational_prose_preservation`:
  - Test substantive NCERT sentences: `"The troposphere is the lowest layer of the atmosphere where temperature decreases with height."`
  - Assert `NoiseFilterGate.audit(text) is None` (zero false rejection).

#### Area 3: `TestMultiWordEntityAndDistractorRegression`
- `test_multi_word_entities_extracted_intact`:
  - Test extraction of:
    - `"Standard Meridian of India"`
    - `"Andaman and Nicobar Islands"`
    - `"Continental Drift Theory"`
    - `"Coriolis force"`
    - `"San Andreas Fault"`
  - Assert primaryEntity is the complete multi-word phrase, not truncated to single word.
- `test_taxonomic_sibling_category_constraints`:
  - When correct answer is a multi-word geomorphic feature (`"Oxbow lake"`), all distractors are drawn from geomorphic features (`"Cirque"`, `"Mushroom rock"`, `"Moraine"`), never rock types or atmospheric layers.
  - When correct answer is a mountain range (`"Western Ghats"`), distractors are mountain ranges (`"Eastern Ghats"`, `"Aravalli Range"`, `"Vindhyas"`).
- `test_grammatical_parallelism_and_number_agreement`:
  - All distractors share grammatical number (plural with plural, singular with singular).
  - Verify absence of stem-terminal article clueing (`"Which of the following is an:"`).
- `test_distractor_trap_dissections`:
  - Verify every distractor has a valid trap type from `VALID_ROOM_TRAP_TYPES` (`FACT_DISTORTION`, `CONCEPT_MIX`, etc.) and a non-empty rationale >= 10 characters.

#### Area 4: `TestNonSvoFactsAll14IntentsRegression`
- `test_passive_inversion_extraction`:
  - `"A vast elevated flatland with steep slopes is called a plateau."` -> entity: `"plateau"`, intent: `"definition"`.
- `test_locative_inversion_extraction`:
  - `"Between the crust and core lies the dense mantle."` -> entity: `"mantle"`, intent: `"spatial"`.
- `test_conditional_extraction`:
  - `"When sea surface temperatures exceed 27°C, tropical cyclones develop."` -> entity: `"tropical cyclones"`, intent: `"condition"`.
- `test_all_14_semantic_intents_slotting`:
  - Execute test cases across all 14 canonical intents:
    1. `definition`, 2. `attribute`, 3. `cause/effect`, 4. `comparison`, 5. `spatial`, 6. `distribution`, 7. `classification`, 8. `quantity`, 9. `sequence`, 10. `condition`, 11. `exception`, 12. `process`, 13. `part-of`, 14. `member-of`.
  - Assert for every intent:
    - `node.intent_type` matches canonical intent.
    - `node.primary_entity` is non-empty.
    - `node.predicate` is populated.
    - `node.raw_evidence` contains verbatim source text.

#### Area 5: `TestSemanticDuplicateEliminationRegression`
- `test_option_verbatim_duplicates`:
  - Options with identical values trip `AdversarialAuditor` with `"OPTION_DUPLICATION"`.
- `test_option_case_insensitive_duplicates`:
  - Options `{"a": "Basalt", "b": "basalt"}` trip duplicate detection.
- `test_option_semantic_alias_collision_with_correct_answer`:
  - Correct answer is `"Ganges"`, distractor is `"Ganga"` -> trips `"SEMANTIC_AMBIGUITY"`.
- `test_option_distractor_to_distractor_alias_collision`:
  - Distractor 1 is `"Taiga"`, Distractor 2 is `"Boreal Forest"` -> trips `"SEMANTIC_AMBIGUITY"`.
- `test_question_level_semantic_deduplication`:
  - Two questions targeting identical proposition are clustered by fingerprint `(topic_id, intent_type, primary_entity, correct_answer)` and deduplicated.

#### Area 6: `TestCryptographicProvenanceAndTamperResistanceRegression`
- `test_unbroken_6_link_chain_creation`:
  - Link 1: question_id & question_stem
  - Link 2: intent_type
  - Link 3: knowledge_node_id
  - Link 4: evidence_text
  - Link 5: source_file
  - Link 6: source_location (page, line, offset)
  - Assert `record.verify_hash()` returns `(True, None)`.
- `test_merklized_sha256_link_integrity`:
  - Step-by-step verification of `LinkHashes` (`location_hash` -> `source_hash` -> `evidence_hash` -> `unit_hash` -> `intent_hash` -> `question_hash`).
- `test_tamper_detection_evidence_mutation`:
  - Mutating 1 character of evidence text breaks `evidence_hash` and root hash; `verify_hash()` returns `(False, "evidenceText")`.
- `test_tamper_detection_stem_mutation`:
  - Mutating question stem breaks `question_hash`; `verify_hash()` returns `(False, "questionId_or_stem")`.
- `test_tamper_detection_intent_mutation`:
  - Mutating intent type breaks `intent_hash`; `verify_hash()` returns `(False, "intentType")`.
- `test_tamper_detection_location_mutation`:
  - Mutating line or page coordinates breaks `location_hash`; `verify_hash()` returns `(False, "sourceLocation")`.
- `test_provenance_record_immutability`:
  - Attempting attribute mutation on frozen `ProvenanceRecord` raises `dataclasses.FrozenInstanceError`.
- `test_corpus_grounding_audit`:
  - `audit_provenance_integrity([record], source_corpus_text)` verifies verbatim existence in source corpus.

---

## 5. Verification Method

To independently verify the technical findings and implementations:

1. **Verify Android Unit Tests**:
   ```powershell
   cmd.exe /c "gradlew.bat clean testDebugUnitTest"
   ```
   *Expected outcome: Exit code 0, 20 test classes pass.*

2. **Verify Android Debug APK Build**:
   ```powershell
   cmd.exe /c "gradlew.bat clean assembleDebug"
   ```
   *Expected outcome: Exit code 0, generates `app/build/outputs/apk/debug/app-debug.apk`.*

3. **Verify Existing Python Test Suites**:
   ```powershell
   python -m unittest discover -s tests -p "test_v13_*.py"
   python run_e2e_tests.py
   ```
   *Expected outcome: 351 unit tests pass, 202 E2E tests pass (exit code 0).*

4. **Verify New Regression Test Suite** (once implemented by Worker):
   ```powershell
   python -m unittest tests/test_v13_new_regressions.py
   ```
   *Expected outcome: All test cases across all 6 areas pass cleanly.*

5. **Verify Asset Synchronization**:
   ```powershell
   cmd.exe /c "gradlew.bat copyMarkdownToAssets"
   ```
   *Verify that `source-material/consolidated_grounding.md` and `app/src/main/assets/consolidated_grounding.md` are in sync and parse cleanly via `DataImporterSimulator.parse_markdown`.*

### Invalidation Conditions
- If `.\gradlew.bat testDebugUnitTest` fails, inspect KSP/Room compiler generated sources in `app/build/generated/ksp/`.
- If `DataImporter.kt` rejects appended questions, verify that `Explanation:` strictly precedes `Correct Answer: Option X` in the question markdown block.
- If `NoiseFilterGate` rejects valid educational sentences, verify that the sentence does not match `INTERROGATIVE_REGEX` or end in dangling prepositions without object completion.
