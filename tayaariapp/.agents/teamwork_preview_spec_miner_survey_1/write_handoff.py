import os

target = os.path.join(os.path.dirname(__file__), 'handoff.md')

content = """# Handoff Report: Android Application Architecture, Data Contracts, Build/Test Infrastructure, and Pipeline Integration Boundaries

**Agent**: teamwork_preview_spec_miner_survey_1  
**Working Directory**: `c:\\Users\\harsh\\Downloads\\tayaari\\tayaariapp\\.agents\\teamwork_preview_spec_miner_survey_1`  
**Target File**: `c:\\Users\\harsh\\Downloads\\tayaari\\tayaariapp\\.agents\\teamwork_preview_spec_miner_survey_1\\handoff.md`  
**Milestone**: Specification Mining & Architectural Survey  
**Date**: 2026-09-03T10:45:00Z  

---

## 1. Observation

### 1.1 Android Build & Tooling Infrastructure
- **Gradle Version**: `9.3.1` (configured via `gradle/wrapper/gradle-wrapper.properties`: `distributionUrl=https\\://services.gradle.org/distributions/gradle-9.3.1-bin.zip`).
- **Android Gradle Plugin (AGP)**: `9.1.1` (configured in `gradle/libs.versions.toml`: `agp = "9.1.1"`).
- **Kotlin Version**: `2.2.10` in `libs.versions.toml`, with `2.2.21` bundled in the Gradle 9.3.1 runtime. Compose plugin `org.jetbrains.kotlin.plugin.compose` applied.
- **Java / JDK Version**: `Java 22.0.2` (Oracle Corporation build `22.0.2+9-70`, 64-bit Server VM) located at `C:\\Program Files\\Java\\jdk-22`.
- **Toolchain Resolver**: `org.gradle.toolchains.foojay-resolver-convention:1.0.0` applied in `settings.gradle.kts`.
- **JVM Target Compatibility**: `JavaVersion.VERSION_11` specified for `sourceCompatibility` and `targetCompatibility` in `app/build.gradle.kts` lines 51-54.
- **SDK Target & Minimum**: `compileSdk = 36` (with `minorApiLevel = 1`), `minSdk = 24`, `targetSdk = 36` in `app/build.gradle.kts` lines 14-20.
- **KSP Configuration**: KSP version `2.3.5` with `ksp.useKSP2=true` enabled in `gradle.properties`.
- **Pre-Build Asset Sync**: Lines 137-144 of `app/build.gradle.kts` register a task `copyMarkdownToAssets`:
  ```kotlin
  tasks.register<Copy>("copyMarkdownToAssets") {
      from("${rootDir}/source-material/consolidated_grounding.md")
      into("src/main/assets/")
  }
  tasks.named("preBuild") {
      dependsOn("copyMarkdownToAssets")
  }
  ```

### 1.2 Verification of Gradle Test and Build Execution
- **Unit Testing Verification**:
  - Exact command: `.\\gradlew.bat clean testDebugUnitTest`
  - Result: `BUILD SUCCESSFUL in 1m 1s` (clean), `18s` (incremental).
  - Status: Exit code `0`.
  - Report: 20 test classes, 37 test methods executed, 0 failures, 0 errors, 0 skipped (100% pass rate).
  - Breakdown by test class:
    * `DatabasePersistenceTest`: 2 tests passed (Entity serialization, RevisionItemEntity mastery states)
    * `RealMigrationTest`: 1 test passed (Robolectric SQLite migration V17 -> V21 column and table preservation)
    * `SchemaDumpTest`: 1 test passed (Room openHelper table dump)
    * `AttemptOutcomeTest`: 2 tests passed (Outcome enum validation)
    * `BlindSpotEngineTest`: 1 test passed (Topic format stats and evidence gap calculations)
    * `BlueprintRegressionTest`: 3 tests passed (UPSC CSE 2026, BPSC 72nd CCE, SSC CGL 2025 configurations)
    * `ContentImportRulesTest`: 2 tests passed (Question text, options, answer validation)
    * `RevisionMathTest`: 2 tests passed (Spaced repetition intervals and priority sorting)
    * `ConfusionEvidenceTest`: 1 test passed (Confusion pair thresholds)
    * `ConfusionNetworkTest`: 3 tests passed (Concept confusion detection)
    * `FamilyProgressionAndMigrationTest`: 3 tests passed (Family repetition penalties and stage progression bonuses)
    * `LearnerModelReplayIntegrationTest`: 1 test passed (Learner profile and error tracking)
    * `PaperTwinValidationTest`: 1 test passed (Exam DNA proportion sampling)
    * `PatternShockEngineTest`: 4 tests passed (Cognitive load adjustments)
    * `QuestionSelectionEngineTest`: 1 test passed (Paper Twin blueprint distribution)
    * `QuestionSelectionScoringTest`: 1 test passed (Exact repetition vs family repetition scoring penalties)
    * `StopDoingEngineTest`: 3 tests passed (Negative habit detection)
    * `MistakeReplayTest`: 3 tests passed (Replay queue generation and outcome logging)
    * `PracticeScoringRegressionTest`: 1 test passed (ExactFraction rational math across BPSC scoring cases)
    * `TrapLogicTest`: 1 test passed (Distractor trap trigger conditions)
- **APK Assembly Verification**:
  - Exact command: `.\\gradlew.bat clean assembleDebug`
  - Result: `BUILD SUCCESSFUL in 34s`.
  - Status: Exit code `0`.
  - Output Artifact: `app/build/outputs/apk/debug/app-debug.apk` (23,461,399 bytes, ~23.46 MB).

### 1.3 Room Database Schema (Version 21, `tayaari_database`)
In `AppDatabase.kt` (lines 12-22), 9 entities are defined:
1. `Question` (table `questions`):
   - `id`: Int (PrimaryKey, autoGenerate = true)
   - `topicId`: Int (Foreign reference to `topics.id`)
   - `tier`: String (`Basic`, `Medium`, `Advanced`, `Elite`)
   - `format`: String (`Direct Fact`, `Statement-based`, `Matching`, `Assertion-Reason`, `Application`)
   - `examRelevance`: String (`Foundation`, `Core`, `Elite`, `General-Competitive`)
   - `source`: String (e.g. `Real-PYQ`, `NCERT Class 6 Generated`)
   - `specificExam`: String (`SSC-Stenographer`, `UPSC-Prelims`, `SSC-CGL`, `BPSC`, `Any`)
   - `questionText`: String (plain text / markdown containing the question stem and statements/tables)
   - `options`: String (JSON array string: `[{"id":"opt_a","text":"..."}, ...]`)
   - `correctAnswer`: String (option ID, e.g. `"opt_a"`, `"opt_b"`)
   - `explanation`: String
   - `distractorDissections`: String (JSON array string: `[{"optionId":"opt_distractor","trapType":"...","dissection":"..."}]`, default `"[]"`)
   - `imageUrl`: String (default `""`, parsed from `[IMAGE: url]`)
   - `familyId`: String? (Family group identifier)
   - `familyStage`: String? (`FOUNDATION`, `REINFORCEMENT`, `STANDARD`, `APPLICATION`, `TRAP`, `TRANSFER`, `EXAM_STYLE`)
2. `Topic` (table `topics`):
   - `id`: Int (PrimaryKey)
   - `name`: String (e.g. `"1. The Earth in the Solar System"`)
   - `source`: String
   - `module`: String (`"Physical Geography"`, `"Indian Geography"`, `"Human & Economic Geography"`, `"Miscellaneous Topics"`)
3. `BookmarkedQuestionEntity` (table `bookmarks`): `id` String PK, `format` QuestionFormat, `payloadJson` String.
4. `TrapAnalyticsEntity` (table `trap_analytics`): `id` Int PK, `trapType` String, `frequency` Int, `failedQuestionsJson` String.
5. `TestSession` (table `test_sessions`): `id` Int PK, `timestamp` Long, `examProfile` String, `score` Int, `totalQuestions` Int.
6. `RevisionItemEntity` (table `revision_items`): `questionId` String PK, `firstAttemptTime` Long, `lastAttemptTime` Long, `attemptCount` Int, `correctCount` Int, `incorrectCount` Int, `masteryState` String, `nextRevisionDate` Long, `priority` Int, `associatedTrap` String?.
7. `QuestionAttemptEntity` (table `question_attempts`): `id` Int PK, `questionId` String, `timestamp` Long, `outcome` String (`CORRECT`, `INCORRECT`, `ABSTAINED`, `UNANSWERED`), `confidence` String? (`Certain`, `Likely`, `Unsure`, `Guessing`), `timeSpentSeconds` Int, `trapFallenInto` String?.
8. `ConfusionEventEntity` (table `confusion_events`): `id` Int PK, `pairId` String, `questionId` String, `selectedOptionText` String, `timestamp` Long, `evidenceLevel` String.
9. `ReplayOutcomeEntity` (table `replay_outcomes`): `id` Int PK, `originalQuestionId` String, `transferQuestionId` String?, `replayTimestamp` Long, `initialEvidenceType` String, `outcomeState` String.

### 1.4 In-App Question Lifecycle & UI Binding
1. **Seeding Callback**:
   - `AppDatabase.kt` (lines 60-77): In `RoomDatabase.Callback().onOpen()`, if `topicCount == 0 || questionCount == 0`, opens `consolidated_grounding.md` from `context.assets` and executes `DataImporter.importFromMarkdown(context, mdContent)`.
2. **Repository Layer**:
   - `LocalRepository.kt`: Bridges Room DAOs (`AppDao`, `BookmarkDao`, `TrapAnalyticsDao`, `RevisionDao`, `QuestionAttemptDao`, `AnalyticsDao`, `ConfusionEventDao`, `MistakeReplayDao`) and domain engines (`QuestionSelectionEngine`, `MistakeReplayEngine`, `LearnerModelEngine`, `SyllabusEngine`, `TimeBasedStudyPlanEngine`, `PaperTwinEngine`, `ExamDecisionLabEngine`, `FalseMasteryEngine`, `PostTestDebriefEngine`, `PressureLadderEngine`).
3. **Question Selection & Next-Best-Action**:
   - `QuestionSelectionEngine.kt`:
     - Queries questions by exam profile allowed tiers (`allowedTiers`), relevance, topic, and mode.
     - Parses `options` JSON array string and `distractorDissections` JSON array string.
     - If blueprint requires `synthesizeAbstainOption` (e.g. BPSC 72nd CCE), injects `Option("opt_abstain", blueprint.abstainOptionLabel, OptionRole.ABSTAIN)`.
     - Next-Best Scoring: Freshness (`+10.0`), Revision Due (`+25.0`), Error Rate (`errorRate * 15.0`), Overexposure penalty (`-attemptCount * 2.0`), Family repetition penalty (`-20.0` exact, `-10.0` same stage, `-5.0` same family), Progression bonus (`+20.0` across stages).
4. **UI Presentation & ViewModels**:
   - `PracticeScreen.kt` (Jetpack Compose):
     - Displays question progress, timer, topic title, tier/format chips.
     - Renders `PremiumQuestionCard` (question text + bookmark toggle).
     - Renders `PremiumOptionsList` (options, cross-out elimination gestures, confidence selector dialog).
     - Renders `CorrectExplanationCard` (shows correct option text and detailed explanation on answer submission).
     - Displays Distractor Trap Warning if an incorrect option with distractor dissection is picked.
   - `PracticeViewModel.kt`:
     - Uses exact rational scoring via `ExactFraction(numerator, denominator)` to prevent floating-point drift.
     - Handles options pending, confidence dialog, answer submission, confusion detection via `ConfusionNetwork`, question attempt logging, and trap frequency increments.

### 1.5 Pipeline Integration Boundary (`source-material/consolidated_grounding.md`)
1. **Source Corpus & Registry**:
   - `source_registry.json`: Catalogs all raw source PDFs in `source-material/`.
   - `syllabus_knowledge_map.json`: Maps Exam (`EXAM_UPSC`), Subject (`SUBJECT_GEOGRAPHY`), Modules, Topics, Subtopics, and Concepts with coverage states (`WELL_SUPPORTED`, `FORMAT_GAP`, `SOURCE_GAP`).
2. **Asset Pipeline Data Flow**:
   - Python Discovery Pipeline (V12 / V13) analyzes source texts -> generates Question Intents, distractor dissections, and exam metadata -> injects into `${rootDir}/source-material/consolidated_grounding.md`.
   - Gradle `preBuild` task `copyMarkdownToAssets` copies `${rootDir}/source-material/consolidated_grounding.md` -> `app/src/main/assets/consolidated_grounding.md`.
   - Android App Room Database seeds questions from this asset file on startup via `DataImporter.importFromMarkdown`.
3. **Current Asset Contents**:
   - File size: 570,204 bytes, 18,429 lines.
   - 45 topic blocks (`## 1. The Earth in the Solar System` to `## 45. Natural Hazards and Disasters`).
   - 1,075 total questions:
     * Tiers: `Basic` (960), `Medium` (96), `Advanced` (19)
     * Formats: `Direct Fact` (960), `Statement-based` (57), `Matching Pairs` (39), `Assertion-Reason` (19)
     * Relevance: `General-Competitive` (925), `Elite` (150)
     * Exams: `SSC-Stenographer` (925), `UPSC-Prelims` (150)

---

## 2. Logic Chain

1. **Build & Tooling Compatibility**:
   - Direct Observation: `.\\gradlew.bat --version` reported Gradle 9.3.1 running under Launcher JVM Java 22.0.2.
   - AGP 9.1.1 and Kotlin 2.2.10/2.2.21 are fully compatible with JDK 22 and KSP 2 (`ksp.useKSP2=true`).
   - Running `.\\gradlew.bat clean testDebugUnitTest` and `.\\gradlew.bat clean assembleDebug` both succeed with exit code `0`.
   - Inference: The Android development environment is completely healthy, reproducible, and ready for continuous regression testing and packaging.

2. **Question Ingestion & Storage Architecture**:
   - Direct Observation: `AppDatabase.kt` lines 60-77 checks `if (topicCount == 0 || questionCount == 0)` and triggers `DataImporter.importFromMarkdown(context, mdContent)`.
   - Direct Observation: `app/build.gradle.kts` binds `preBuild` to `copyMarkdownToAssets`, which copies `${rootDir}/source-material/consolidated_grounding.md` into `app/src/main/assets/`.
   - Direct Observation: `DataImporter.kt` parses markdown blocks partitioned by `## <topicId>. <topicName>` and individual questions delimited by triple-backtick code fences containing `(a)-(d)` options, `Correct Answer: Option <x>`, and `Explanation: <text>`.
   - Inference: `source-material/consolidated_grounding.md` is the authoritative single source of truth for all pre-seeded questions in the application. Any question discovered or generated by the Python pipeline (V13) must be injected into this file to be consumed by the Android app.

3. **Data Contract Compliance & Schema Integrity**:
   - Direct Observation: `Entities.kt` stores questions in Room table `questions` with columns `topicId`, `tier`, `format`, `examRelevance`, `source`, `specificExam`, `questionText`, `options` (JSON string), `correctAnswer`, `explanation`, `distractorDissections` (JSON string), `imageUrl`, `familyId`, and `familyStage`.
   - Direct Observation: `QuestionSelectionEngine.kt` deserializes `options` into `List<Option>` and `distractorDissections` into `List<DistractorDissection>`.
   - Direct Observation: `ExamBlueprintRegistry.kt` defines strict allowed tiers per exam:
     * UPSC CSE 2026: `allowedTiers = ["Medium", "Advanced", "Elite"]`
     * BPSC 72nd CCE: `allowedTiers = ["Medium", "Advanced"]`
     * SSC CGL 2025: `allowedTiers = ["Basic", "Medium"]`
   - Inference: Questions generated by V13 must match these exact tier strings and format names (`Direct Fact`, `Statement-based`, `Matching Pairs`, `Assertion-Reason`). A question tagged as `Basic` will never be served to a UPSC user, and an `Elite` question will never be served to an SSC user.

4. **Distractor & Trap Architecture**:
   - Direct Observation: `PracticeViewModel.kt` checks if `!isCorrect` and looks up `currentQ.distractorDissections.find { it.optionId == pending }`.
   - Direct Observation: If found, it increments the frequency in `TrapAnalyticsDao` and attaches `{questionText, dissection, timestamp}` to `failedQuestionsJson`.
   - Inference: For V13 question generation, distractors must not merely be random false strings; they must contain structured distractor dissections with valid `trapType` values (`ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`) and clear diagnostic explanations.

---

## 3. Caveats

1. **Database Seeding Lifecycle**:
   - The database auto-seeding callback in `AppDatabase.kt` only triggers when `topicCount == 0 || questionCount == 0`. On an existing installed device or emulator with an already populated SQLite database, modifying `consolidated_grounding.md` does not automatically update the app DB unless the app data is cleared, database version is bumped, or `clearAllQuestions()` is called.
2. **Device / Instrumentation Testing**:
   - Only local unit tests (`testDebugUnitTest` via Robolectric and JVM) were executed. No connected physical Android device or running emulator was present during survey, so `connectedAndroidTest` was not run.
3. **Legacy Assets**:
   - `app/src/main/assets/tayaari.db` and `app/src/main/assets/geography_db` exist in the asset folder as legacy pre-built databases from earlier iterations, but `AppDatabase.kt` constructs `"tayaari_database"` dynamically via `Room.databaseBuilder` and does not use `createFromAsset()`.

---

## 4. Conclusion

1. **Build & Test Status**: The Android app build system (`gradlew.bat clean testDebugUnitTest` and `gradlew.bat clean assembleDebug`) is fully functional, with 37/37 unit tests passing on Gradle 9.3.1, AGP 9.1.1, and Java 22.0.2.
2. **Integration Boundary Established**: The pipeline integration boundary is `source-material/consolidated_grounding.md`. Any questions generated by the V13 educational discovery pipeline must be written in the standardized markdown schema with complete options, correct answers, explanations, distractor dissections, and valid tier/format tags.
3. **Data Contracts Documented**: Room entity schemas, JSON serialization formats, blueprint scoring rules (`ExactFraction`), and next-best-action progression scoring rules are fully surveyed and specified below.

---

## 5. Verification Method

To independently verify these findings, execute the following commands in `c:\\Users\\harsh\\Downloads\\tayaari\\tayaariapp`:
1. **Verify Unit Tests**:
   ```powershell
   .\\gradlew.bat clean testDebugUnitTest
   ```
   *Expected*: `BUILD SUCCESSFUL`, 37 tests completed, 0 failures. Test reports generated in `app/build/test-results/testDebugUnitTest/`.
2. **Verify APK Assembly**:
   ```powershell
   .\\gradlew.bat clean assembleDebug
   ```
   *Expected*: `BUILD SUCCESSFUL`, binary created at `app/build/outputs/apk/debug/app-debug.apk` (approx. 23.5 MB).
3. **Verify Asset Synchronization**:
   ```powershell
   python -c "import os; p1='source-material/consolidated_grounding.md'; p2='app/src/main/assets/consolidated_grounding.md'; print(f'Source: {os.path.getsize(p1)} bytes, Asset: {os.path.getsize(p2)} bytes')"
   ```
   *Expected*: Both files exist and are synchronized by the Gradle `preBuild` task.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Build & Tooling | Gradle Unit Testing | Executes all 20 Robolectric and JUnit test suites | `.\\gradlew.bat clean testDebugUnitTest` | XML reports in `app/build/test-results/` | Non-zero exit code if assertion fails | `app/build.gradle.kts`, `ORIGINAL_REQUEST.md` |
| 2 | Build & Tooling | APK Assembly | Compiles, dexes, and packages debug APK | `.\\gradlew.bat clean assembleDebug` | `app/build/outputs/apk/debug/app-debug.apk` | Build failure on missing symbols or syntax errors | `app/build.gradle.kts`, `ORIGINAL_REQUEST.md` |
| 3 | Build & Tooling | `copyMarkdownToAssets` | Gradle task syncing source markdown to assets directory | `source-material/consolidated_grounding.md` | `app/src/main/assets/consolidated_grounding.md` | Task fails if source file is missing | `app/build.gradle.kts:137-144` |
| 4 | Database & Storage | Room Database (`tayaari_database`) | Manages local SQLite storage at version 21 with migrations 17-21 | Room DB operations | SQLite database instance | Unhandled migration throws IllegalStateException | `AppDatabase.kt:12-84` |
| 5 | Database & Storage | `Question` Entity | Models questions with text, JSON options, answer, tier, format, family | Field values | Room table row in `questions` | SQLite constraint violation on null non-null fields | `Entities.kt:30-47` |
| 6 | Database & Storage | `Topic` Entity | Models topics and associated broad geography module | Topic ID, name, source, module | Room table row in `topics` | Replaced on conflict | `Entities.kt:22-28` |
| 7 | Database & Storage | `DataImporter.importFromMarkdown` | Parses markdown question blocks into `Topic` and `Question` entities | Markdown string from assets | Room database inserts | Skips malformed questions (<2 options, missing answer) | `DataImporter.kt:27-194` |
| 8 | Exam Blueprint & Scoring | Exam Blueprint Registry | Defines positive marks, negative penalty rules, option count, tiers | Exam ID string (`UPSC_CSE_2026`, etc.) | `ExamBlueprint` object | Returns null for unknown exam ID | `ExamBlueprint.kt:34-226` |
| 9 | Exam Blueprint & Scoring | `ExactFraction` Rational Math | Implements exact fractional arithmetic to avoid IEEE-754 float drift | Numerator, Denominator | Reduced rational score | Division by zero throws IllegalArgumentException | `ExactFraction.kt`, `PracticeScoringRegressionTest.kt` |
| 10 | Exam Blueprint & Scoring | BPSC Abstain Synthesis | Synthesizes 5th option E ("I do not wish to answer") for BPSC 72nd CCE | `MCQQuestion` with 4 options | `MCQQuestion` with 5 options (5th role=ABSTAIN) | Ignores if question already has 5 options | `QuestionSelectionEngine.kt:93-100` |
| 11 | Engine & Selection | Next-Best-Action Question Scoring | Scores and ranks questions based on freshness, revision, error rate, family | Topic, blueprint, targetCount | Ranked `List<ExamQuestion>` | Falls back to available questions if count insufficient | `QuestionSelectionEngine.kt:149-216` |
| 12 | Engine & Selection | Paper Twin Distribution | Samples questions matching exact exam DNA theme weightages | Target count, exam blueprint | Proportional question set | Fills remainder with available questions if format pool exhausted | `QuestionSelectionEngine.kt:30-66`, `PaperTwinValidationTest.kt` |
| 13 | Distractor & Traps | Distractor Dissection Parsing | Parses JSON array of trap types and explanations for distractors | `distractorDissections` JSON | `List<DistractorDissection>` | Logs error and returns empty list on malformed JSON | `QuestionSelectionEngine.kt:110-125` |
| 14 | Distractor & Traps | Trap Analytics Tracking | Records trap type frequencies and failed question excerpts on wrong answer | Wrong option selected | Row in `trap_analytics` table | No trap recorded if answer is correct or abstained | `PracticeViewModel.kt:146-155`, `TrapLogicTest.kt` |
| 15 | Cognitive Validation | `ConfusionNetwork` Detection | Detects conceptual confusion pairs between question stem and chosen option | Question stem, selected option text | `ConfusionDetectionResult` | Returns null if no confusion pattern detected | `PracticeViewModel.kt:93-126`, `ConfusionNetworkTest.kt` |
| 16 | Spaced Repetition | `RevisionDao` Smart Revision | Tracks mastery states (`NEW`, `DUE`, `IMPROVING`, `MASTERED`) and schedules reviews | Question attempts, intervals | Due items queue | Defaults to priority 1 if unattempted | `Entities.kt:60-72`, `Daos.kt:119-142` |
| 17 | UI & Presentation | `PracticeScreen` & `PracticeViewModel` | Interactive Jetpack Compose test screen with timer, bookmarks, elimination | `TestUiState`, user gestures | Rendered UI state | Displays error banner if question set fails to load | `PracticeScreen.kt`, `PracticeViewModel.kt` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | BPSC 72nd Scoring | All 10 questions answered with Abstain option (`opt_abstain`) | Score is exactly `0/1` (ExactFraction.ZERO), no negative penalty applied |
| 2 | BPSC 72nd Scoring | All 10 questions left completely unanswered | Score is penalized at 1/3 mark per question if unanswered penalty rule is active; returns exact fraction |
| 3 | Question Ingestion | Question text missing `Correct Answer: Option <X>` | Question is rejected by `DataImporter` and logged as malformed; total rejected count incremented |
| 4 | Question Ingestion | Question has fewer than 2 parsed options | Question is rejected by `DataImporter` to prevent invalid single-option questions in Room DB |
| 5 | Question Selection | Question family repetition: user failed stage `FOUNDATION` | Engine applies `-20.0` penalty for exact question repetition, but awards `+20.0` bonus for sibling question in stage `REINFORCEMENT` |
| 6 | Question Selection | Question family repetition: user answered stage `TRANSFER` correctly | Engine awards `+20.0` bonus for advancing to stage `EXAM_STYLE` in the same family |
| 7 | Trap Analytics | User selects correct answer on a question with configured distractors | Trap analytics does NOT increment; trap dissection is not displayed |
| 8 | Trap Analytics | User chooses "I do not wish to answer" (Abstain) | Trap analytics does NOT increment; abstention is treated as a strategic decision, not a trap failure |
| 9 | Question Selection | Target exam is `UPSC_CSE_2026` but question tier is `Basic` | Question is filtered out and excluded by SQL query (`tier IN ('Medium', 'Advanced', 'Elite')`) |
| 10 | Question Selection | Target exam is `SSC_CGL_2025` but question relevance is `Elite` | Question is excluded by SQL query (`allowElite = 0 AND examRelevance != 'Elite'`) |
| 11 | Image Support | Question text includes `[IMAGE: https://...]` tag | Image URL is extracted into `imageUrl` field and removed from `questionText` to preserve clean UI rendering |
| 12 | Module Mapping | Topic name starts with number prefix (e.g. `1. The Earth in the Solar System`) | Stripped via `substringAfter(". ").trim()` and mapped to module (`Physical Geography`) |
"""

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print('Successfully generated handoff.md')

