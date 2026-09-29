# Milestone 4 Specification Report: Question Specifications & Room DB Contracts

## Executive Summary
This specification report establishes the authoritative data contracts, serialization specifications, distractor trap taxonomy, anti-quotation rules, and natural exam-style stem patterns for Milestone 4 (Question & Defensible Distractor Engine) of the V13 educational pipeline.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Contract | CandidateQuestion Schema | Core dataclass representing an end-to-end question opportunity with options, explanation, dissections, and provenance. | `id`, `stem`, `options: dict`, `correctAnswer: str`, `explanation: str`, `distractorDissections: list`, `provenance: dict`, `cognitiveDemand: str`, `examTarget: str`, `tier: str`, `format: str`, `topicId: int`, `topicName: str`, `pdfSequenceNumber: str` | Instantiated `CandidateQuestion` object | Missing required fields or malformed option dict raises `TypeError` / schema validation errors | `tests/e2e/test_helpers.py:86-101`, `PROJECT.md:73-75` |
| 2 | Contract | Room DB Question Entity | Persistent SQLite Room DB entity storing imported exam questions. | `id: Int`, `topicId: Int`, `tier: String`, `format: String`, `examRelevance: String`, `source: String`, `specificExam: String`, `questionText: String`, `options: String (JSON)`, `correctAnswer: String`, `explanation: String`, `distractorDissections: String (JSON)`, `imageUrl: String`, `familyId: String?`, `familyStage: String?` | Room DB SQLite row in table `questions` | Non-null constraint violations throw SQLite exceptions | `app/src/main/java/com/example/database/Entities.kt:30-47` |
| 3 | Contract | Markdown Serialization Schema | Target format in `consolidated_grounding.md` ingested by `DataImporter.kt`. | `CandidateQuestion` object formatted with 8-9 markdown bullet points and code-fenced question block | Multi-line Markdown text matching `qPattern` regex | Parsing regex fails to match block; question rejected and logged | `app/src/main/java/com/example/repository/DataImporter.kt:54-64`, `tests/e2e/test_helpers.py:283-318` |
| 4 | Parser Discovery | Explanation Ordering Contract | Sequential extraction bug in `DataImporter.kt` where `ansMatcher` trims before `expMatcher`. | Markdown question block with `Explanation:` before vs. after `Correct Answer:` | Clean `explanationText` string vs. default `"No explanation"` | When `Explanation:` is placed after `Correct Answer:`, explanation is silently wiped | `app/src/main/java/com/example/repository/DataImporter.kt:109-126`, `tests/e2e/test_helpers.py:210-227` |
| 5 | Distractor Taxonomy | 8 Room DB Trap Types | Authorized distractor trap enumeration recognized by Room DB and application views. | Distractor candidate and domain ontology context | Canonical trap type string: `ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`, `UNCLASSIFIED_TRAP` | Unknown strings map to `UNCLASSIFIED_TRAP` | `app/src/main/java/com/example/repository/DataImporter.kt:87-97`, `tests/e2e/test_helpers.py:40-49` |
| 6 | Distractor Taxonomy | Diagnostic Dissections | Diagnostic rationales dissecting why each distractor is incorrect and which cognitive trap it embodies. | `optionId: str`, `trapType: str`, `dissection: str` | JSON array of 3 dissection objects assigned to incorrect options | Correct answer tagged with trap, or missing optionId, fails validation | `app/src/main/java/com/example/model/TestModels.kt:29-33`, `tests/e2e/test_helpers.py:436-468` |
| 7 | Prompt Engineering | Anti-Quotation Strict Rules | Lexical and syntactic rules prohibiting generic quotation templates and lazy fragment interpolation. | Generated question stem string | Clean, natural interrogative/directive stem | Match against banned patterns triggers Adversarial Auditor rejection | `ORIGINAL_REQUEST.md:38`, `tests/e2e/test_e2e_tier1_features.py:495-501, 662-670` |
| 8 | Stem Formulation | 14-Intent Natural Stem Patterns | Exam-calibrated stem generation rules translating each semantic intent into natural exam questions. | `KnowledgeNode` ($E, P, S, C, Q$) + domain context | Exam-ready stem ending with `?` or `:` | Overly short (<15 chars) or quotation-framed stems rejected | `v13_discovery/semantic_extractor.py:647-795`, `tests/e2e/test_helpers.py:684-692` |
| 9 | Provenance | 6-Link Provenance Tracking | Unbreakable provenance chain linking Question to Intent, Node, Evidence, Source, and Location. | Question + KnowledgeNode metadata | Dict with `questionId`, `intentType`, `knowledgeNodeId`, `evidenceText`, `sourceFile`, `sourceLocation` | Missing key or evidence altered from source corpus fails validation | `ORIGINAL_REQUEST.md:29`, `tests/e2e/test_helpers.py:414-434` |
| 10 | Quality Gate | Multi-Agent Audit Interface | Unanimous 3-auditor quality gate (Cognitive, Exam-Fit, Adversarial). | `CandidateQuestion` | `AuditReport(cognitiveVerdict, examFitVerdict, adversarialVerdict, overallGate, failureReasons)` | Any single REJECT forces `overallGate = "REJECT"` | `tests/e2e/test_helpers.py:729-774`, `tests/e2e/test_e2e_tier1_features.py:614-670` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Markdown Parsing | `Explanation:` placed AFTER `Correct Answer:` in question block | `ansMatcher` trims string at start of `Correct Answer:`, silently dropping `Explanation:`. Result: `explanation` is recorded as `"No explanation"`. |
| 2 | Markdown Parsing | `Explanation:` placed BEFORE `Correct Answer:` in question block | `ansMatcher` slices at `Correct Answer:`, retaining `Explanation:`. `expMatcher` extracts explanation text and trims before `Explanation:`. `optionsRegex` parses options cleanly. 100% accurate. |
| 3 | Markdown Parsing | Windows CRLF (`\r\n`) line endings in markdown stream | `DataImporterSimulator` and `DataImporter.kt` handle `\r?\n` in block splits, topic matching, and metadata headers without rejection. |
| 4 | Markdown Parsing | Stem contains inline backticks (e.g. \`meander\`) inside triple backtick block | Parses correctly without premature closure when outer fences use triple backticks (` ``` `). |
| 5 | Markdown Parsing | Double quotes inside option text (e.g. `(A) Called "Oxbow" lake`) | JSON escaping (`replace('"', '\\"')`) in `DataImporter` prevents broken options JSON; all 4 options deserialize properly. |
| 6 | Option Validation | Option text with lowercase first character (e.g. `(A) basalt`) | Fails grammatical parallelism check (`test_f09_02_grammatical_parallelism`); options must start with an uppercase character. |
| 7 | Option Validation | Disproportionately long option (e.g. option A is 180 chars, others are 20 chars) | Fails clueing/length disparity boundary (`test_f09_04_no_clueing_or_length_disparity`); length cannot exceed 3x average length. |
| 8 | Distractor Dissection | Distractor dissection assigned to correct answer option (e.g. `optionId: "opt_a"` when `correctAnswer: "opt_a"`) | Fails validation (`test_f10_04_correct_answer_not_tagged`); correct answers must never be tagged with a trap. |
| 9 | Distractor Dissection | Dissection rationale length < 5 characters (e.g. `"Wrong"`) | Fails validation (`validate_distractor_dissections`); rationale must be informative (>= 5 chars, ideally >= 10 chars). |
| 10 | Stem Length | Stem length = 14 characters (e.g. `"What is Earth?"`) | Cognitive Auditor rejects (`test_b11_04_auditor_catches_short_stem_boundary`); stem must be >= 15 characters and <= 350 characters. |
| 11 | MCQ Stem Leakage | Correct answer name (length > 4) appears verbatim in question stem (e.g. `"Why is Granite an intrusive rock?"`) | Adversarial Auditor rejects (`test_f11_05_adversarial_auditor_catches_leakage`); answers must not leak into the prompt. |
| 12 | Format Normalization | `Format` bullet has `"statement based"`, `"direct"`, or `"matching pair"` | `DataImporter` normalizes them cleanly to `"Statement-based"`, `"Direct Fact"`, and `"Matching"` respectively. |
| 13 | High Topic Number | Chapter header `## 150. Advanced Physical Oceanography` | Regex `^(\d+)\. (.*?)\r?\n` parses multi-digit integers properly; `topicId` 150 is preserved. |
| 14 | Option Count Boundary | Question has fewer than 4 options (e.g. 2 or 3 choices) | Adversarial Auditor rejects (`test_b11_05_auditor_catches_missing_options_count`); competitive exam MCQs require exactly 4 options. |

---

## 1. Observation

### 1.1 Source Code Contracts
Direct inspection of the authoritative source files reveals the following code contracts:

1. **`CandidateQuestion` Schema** (`tests/e2e/test_helpers.py:86-101`):
```python
@dataclasses.dataclass
class CandidateQuestion:
    id: str
    stem: str
    options: Dict[str, str]  # keys: 'a', 'b', 'c', 'd'
    correctAnswer: str       # 'opt_a', 'opt_b', etc.
    explanation: str
    distractorDissections: List[Dict[str, str]]
    provenance: Dict[str, Any]
    cognitiveDemand: str
    examTarget: str
    tier: str = "Standard"
    format: str = "Direct Fact"
    topicId: int = 1
    topicName: str = "Physical Geography"
    pdfSequenceNumber: str = "V13-001"
```

2. **Room DB `Question` Entity** (`app/src/main/java/com/example/database/Entities.kt:30-47`):
```kotlin
@Entity(tableName = "questions")
data class Question(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val topicId: Int,
    val tier: String,
    val format: String,
    val examRelevance: String,
    val source: String,
    val specificExam: String,
    val questionText: String,
    val options: String, // Stored as JSON string: [{"id":"opt_a","text":"..."},...]
    val correctAnswer: String,
    val explanation: String,
    val distractorDissections: String = "[]",
    val imageUrl: String = "",
    val familyId: String? = null,
    val familyStage: String? = null
)
```

3. **Room DB Dao Query** (`app/src/main/java/com/example/database/Daos.kt:114`):
```kotlin
@Query("SELECT * FROM questions WHERE distractorDissections LIKE '%' || :trapType || '%' ORDER BY RANDOM() LIMIT :limit")
```

4. **`DataImporter.kt` Parsing Regex & Metadata Structure** (`app/src/main/java/com/example/repository/DataImporter.kt:54-64`):
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

5. **`DataImporter.kt` Explanation & Answer Slicing Sequence** (`app/src/main/java/com/example/repository/DataImporter.kt:109-126`):
```kotlin
// Line 109: Correct Answer parsed FIRST
val ansMatcher = Pattern.compile("(?i)Correct [Aa]nswer:\\s*(?:Option\\s*)?([a-eA-E])").matcher(rawQText)
if (!ansMatcher.find()) { ... }
val correctAnswerLetter = ansMatcher.group(1)!!.lowercase().trim()
val correctAnswerStr = "opt_$correctAnswerLetter"
rawQText = rawQText.substring(0, ansMatcher.start()).trim() // Line 117: rawQText sliced at ansMatcher!

// Line 121: Explanation parsed SECOND from rawQText
var explanationText = "No explanation"
val expMatcher = Pattern.compile("(?i)Explanation:\\s*(.*)", Pattern.DOTALL).matcher(rawQText)
if (expMatcher.find()) {
    explanationText = expMatcher.group(1)!!.trim()
    rawQText = rawQText.substring(0, expMatcher.start()).trim()
}
```

6. **Authoritative Room DB Trap Types** (`app/src/main/java/com/example/repository/DataImporter.kt:87-97`):
- `ABSOLUTE_WORDING` (from "absolute wording" or "extreme wording")
- `FACT_DISTORTION` (from "fact distortion" or "fact manipulation")
- `FAMILIARITY_TRAP` (from "familiarity")
- `CONCEPT_MIX` (from "concept mix" or "concept blending")
- `FALSE_CORRELATION` (from "false correlation")
- `PARTIAL_TRUTH` (from "partial truth")
- `TIMELINE_MISMATCH` (from "anachronism" or "timeline")
- `UNCLASSIFIED_TRAP` (fallback for any other non-empty trap string)

7. **Prohibition of Quotation Templates** (`ORIGINAL_REQUEST.md:38` and `tests/e2e/test_helpers.py:749-752`):
`ORIGINAL_REQUEST.md:38`: "No generated questions rely on generic source quotation templates (e.g., 'What is a direct consequence of '[fragment]'?')."
`tests/e2e/test_helpers.py:749-752`:
```python
if 'What is a direct consequence of "' in cq.stem or 'Which of the following is true regarding "' in cq.stem:
    adversarial_verdict = "REJECT"
    failure_reasons.append("AdversarialAuditor: Generic quotation template detected in stem")
```

---

## 2. Logic Chain

### 2.1 Serialization Order Contract Discovery
1. `DataImporter.kt` processes `rawQText` strictly sequentially:
   - Line 109 executes `ansMatcher.find()`.
   - Line 117 executes `rawQText = rawQText.substring(0, ansMatcher.start()).trim()`.
   - Line 121 executes `expMatcher = Pattern.compile("(?i)Explanation:\\s*(.*)", Pattern.DOTALL).matcher(rawQText)`.
2. If the Markdown entry places `Correct Answer:` before `Explanation:`, line 117 truncates `rawQText` at `ansMatcher.start()`, discarding the explanation string entirely before line 121 runs. Consequently, `expMatcher.find()` fails, and `explanationText` remains `"No explanation"`.
3. In contrast, if the Markdown entry places `Explanation:` before `Correct Answer:`, line 117 slices off only `Correct Answer:`, leaving `Explanation: <text>` inside `rawQText`. Line 121 then locates `Explanation:`, stores `explanationText`, and truncates `rawQText` at `expMatcher.start()`. Next, line 129 parses the options from the remaining string, completely free of contamination.
4. **Logical Deduction**: To guarantee 100% fidelity when importing generated questions into Room DB, questions serialized to `source-material/consolidated_grounding.md` MUST format the code-fenced block as:
   ```markdown
   - **Question**: ```
   {stem}
   (A) {option_a}
   (B) {option_b}
   (C) {option_c}
   (D) {option_d}
   Explanation: {explanation}
   Correct Answer: Option {Letter}
   ```
   ```
   Or `DataImporter.kt` must be patched in Milestone 6 to parse `Explanation:` before slicing `Correct Answer:`. For Milestone 4 question generation, adhering to the `Explanation:`-before-`Correct Answer:` order is the safest contract.

### 2.2 Distractor Engineering & Trap Type Rationale Architecture
1. In Room DB, `Question.distractorDissections` is a JSON array string.
2. `Daos.kt` queries `distractorDissections LIKE '%' || :trapType || '%'`.
3. In `PracticeScreen.kt` line 691, when a user selects a distractor, the UI finds the specific dissection:
   ```kotlin
   val dissection = distractorDissections.find { it.optionId == option.id }
   ```
4. Therefore, every distractor in `CandidateQuestion.options` (`opt_b`, `opt_c`, `opt_d`) must have a corresponding entry in `distractorDissections` with:
   - `optionId`: Matching the option key (`"opt_b"`, `"opt_c"`, `"opt_d"`).
   - `trapType`: Matching one of the 8 canonical enums.
   - `dissection`: A pedagogically structured rationale explaining both the mechanism of the error and the factual correction.
5. The correct answer (`correctAnswer`) must NEVER be included in `distractorDissections`.

### 2.3 Strict Anti-Quotation Formulation Rules
1. To satisfy Acceptance Criterion 5, question stems must never frame the question by embedding a raw text quote inside quotation marks.
2. Syntactic & Lexical Rules:
   - **Rule NQ1 (No Quotation Encapsulation)**: Stems must not wrap evidence fragments in quotes (`"..."` or `'...'`).
   - **Rule NQ2 (Banned Starters)**: Any stem matching the following regexes must be hard-rejected by generator and auditor:
     - `(?i)^what is a direct consequence of\b`
     - `(?i)^which of the following is true regarding\s+["']`
     - `(?i)^consider the statement\s*[:\s]+["']`
     - `(?i)^according to the (?:passage|text|author|source|chapter|book)\b`
     - `(?i)^based on the (?:statement|text|passage|above sentence)\b`
   - **Rule NQ3 (Domain Lead-In)**: Stems should use authentic civil service exam openers:
     - `"With reference to {concept}, which of the following..."`
     - `"Consider the following statements regarding {concept}:"`
     - `"Which of the following processes accounts for..."`
   - **Rule NQ4 (Entity De-identification in Stems)**: The question stem must not leak the correct answer (length > 4 characters).
   - **Rule NQ5 (Interrogative/Directive Termination)**: Stems must end with `?` or `:`.

---

## 3. Authoritative Distractor Trap Taxonomy & Diagnostic Rationales

The 8 Room DB distractor trap types, their pedagogical mechanisms, and standardized diagnostic rationale templates are defined below:

### 1. `ABSOLUTE_WORDING`
- **Pedagogical Mechanism**: Introduces extreme, unyielding universal quantifiers ("always", "never", "only", "entirely", "all", "exclusively") into contingent or conditional natural processes.
- **Diagnostic Rationale Template**:
  `"Option {opt} employs absolute wording by asserting that {entity} {extreme_claim} ('{qualifier}'), whereas in reality {factual_boundary_or_exception}."`
- **Example**:
  - *Distractor*: `"Tropical cyclones form exclusively in the Western Pacific Ocean."`
  - *Dissection*: `"Option opt_b employs absolute wording by asserting that tropical cyclones form exclusively in the Western Pacific ('exclusively'), whereas they develop across multiple tropical ocean basins including the Indian Ocean and Caribbean Sea."`

### 2. `FACT_DISTORTION`
- **Pedagogical Mechanism**: Alters numerical parameters, physical constants, spatial directions, depths, temperatures, or polarities while preserving general sentence structure.
- **Diagnostic Rationale Template**:
  `"Option {opt} distorts factual data by stating that {entity} {distorted_data}, whereas empirical evidence confirms {actual_data}."`
- **Example**:
  - *Distractor*: `"The mantle constitutes approximately 15 percent of the total volume of the Earth."`
  - *Dissection*: `"Option opt_c distorts factual data by stating that the mantle constitutes approximately 15 percent of Earth's volume, whereas empirical geological data confirms it constitutes approximately 84 percent."`

### 3. `FAMILIARITY_TRAP`
- **Pedagogical Mechanism**: Reuses prominent terms, recognized keywords, or famous proper nouns from the chapter in a contextually erroneous role, baiting candidates who rely on superficial memory.
- **Diagnostic Rationale Template**:
  `"Option {opt} acts as a familiarity trap by using the prominent term '{term}', which correctly belongs to {actual_context}, rather than {question_context}."`
- **Example**:
  - *Distractor*: `"Rossby waves"` (for an ocean current question)
  - *Dissection*: `"Option opt_d acts as a familiarity trap by using the prominent term 'Rossby waves', which correctly belongs to high-altitude atmospheric jet stream dynamics, rather than surface ocean currents."`

### 4. `CONCEPT_MIX`
- **Pedagogical Mechanism**: Conflates two distinct concepts, processes, or entities within the same ontological domain (e.g., swapping intrusive vs. extrusive rocks, or divergent vs. convergent boundaries).
- **Diagnostic Rationale Template**:
  `"Option {opt} mixes the distinct concepts of {concept_a} and {concept_b}, attributing the characteristics of {concept_b} ('{feature}') to {concept_a}."`
- **Example**:
  - *Distractor*: `"Cirque"` (in a question identifying depositional glacial features)
  - *Dissection*: `"Option opt_b mixes the distinct concepts of glacial erosion and glacial deposition, identifying a cirque (an erosional hollow) rather than a depositional moraine."`

### 5. `FALSE_CORRELATION`
- **Pedagogical Mechanism**: Posits an erroneous causal or correlational link between two independent phenomena that may co-occur or sound plausible together.
- **Diagnostic Rationale Template**:
  `"Option {opt} posits a false correlation by claiming that {phenomenon_a} directly causes {phenomenon_b}, whereas {actual_causal_mechanism}."`
- **Example**:
  - *Distractor*: `"The Coriolis force generates tectonic plate motion."`
  - *Dissection*: `"Option opt_c posits a false correlation by claiming that the Coriolis force generates tectonic plate motion, whereas plate motions are driven by mantle convection currents, not planetary rotational deflection."`

### 6. `PARTIAL_TRUTH`
- **Pedagogical Mechanism**: Begins with an authentic, verified factual clause but appends an erroneous conclusion, scope, or mechanism.
- **Diagnostic Rationale Template**:
  `"Option {opt} presents a partial truth: while it is correct that {true_clause}, it falsely claims that {false_clause}."`
- **Example**:
  - *Distractor*: `"The Narmada flows through a rift valley into the Bay of Bengal."`
  - *Dissection*: `"Option opt_b presents a partial truth: while it is correct that the Narmada flows through a rift valley, it falsely claims that it empties into the Bay of Bengal, whereas it flows westward into the Arabian Sea."`

### 7. `TIMELINE_MISMATCH`
- **Pedagogical Mechanism**: Inverts or scrambles chronological, cyclical, or developmental sequences (e.g. rock cycle stages, star life cycle, or geomorphic erosion stages).
- **Diagnostic Rationale Template**:
  `"Option {opt} introduces a timeline mismatch by asserting that {stage_x} occurs prior to {stage_y}, whereas the natural progression proceeds from {correct_sequence}."`
- **Example**:
  - *Distractor*: `"Sedimentary rock undergoes cooling and crystallization before becoming magma."`
  - *Dissection*: `"Option opt_d introduces a timeline mismatch by asserting that sedimentary rock undergoes cooling and crystallization before melting, reversing the sequence of the rock cycle."`

### 8. `UNCLASSIFIED_TRAP`
- **Pedagogical Mechanism**: A composite distractor flaw or category error that does not neatly fit the 7 primary types (used as a fallback in Room DB).
- **Diagnostic Rationale Template**:
  `"Option {opt} represents an unclassified distractor trap because {specific_rationale}."`
- **Example**:
  - *Distractor*: `"A non-geological phenomenon described in metaphorical terms."`
  - *Dissection*: `"Option opt_d represents an unclassified distractor trap because it invokes an invalid category of geomorphic force not recognized in physical geography."`

---

## 4. Natural Exam-Style Stem Patterns per Intent (All 14 Intents)

For each of the 14 semantic intents, natural, non-quotation stem patterns are specified below:

| # | Semantic Intent | Input Slots Used | Banned Lazy Stem (PROHIBITED) | Authorized Natural Exam-Style Stem Patterns | Concrete Example |
|---|-----------------|------------------|-------------------------------|---------------------------------------------|------------------|
| 1 | `definition` | $E$ (Entity), $P$ (Predicate) | `"What is a direct consequence of '{evidence}'?"` | **Pattern 1A**: `"Which of the following geographical features is best defined as {predicate}?"`<br>**Pattern 1B**: `"In physical geography, the term '{primaryEntity}' refers to which of the following?"` | `"Which of the following fluvial features is defined as a crescent-shaped lake formed when a river meander is abandoned?"` |
| 2 | `attribute` | $E$, $P$, $C$ (Condition) | `"Consider the statement '{evidence}'. What is true?"` | **Pattern 2A**: `"With reference to {domain_category}, which of the following is characterized by {predicate}?"`<br>**Pattern 2B**: `"Which of the following physical characteristics is distinctly exhibited by {primaryEntity}?"` | `"With reference to igneous rocks, which of the following is characterized by coarse crystalline grains formed by slow subsurface magma cooling?"` |
| 3 | `cause/effect` | $E$, $P$, $S$ (Secondary) | `"What is a direct consequence of '{evidence}'?"` | **Pattern 3A**: `"Which of the following factors is primarily responsible for {effect}?"`<br>**Pattern 3B**: `"The {primaryEntity} directly results in which of the following phenomena?"` | `"Which of the following forces is primarily responsible for the clockwise deflection of planetary winds in the Northern Hemisphere?"` |
| 4 | `comparison` | $E_1$, $E_2$, $P$ | `"According to the text, how does '{E1}' differ from '{E2}'?"` | **Pattern 4A**: `"With reference to {domain}, how does {primaryEntity} fundamentally differ from {secondaryEntity}?"`<br>**Pattern 4B**: `"In comparison to {secondaryEntity}, {primaryEntity} is characterized by which of the following?"` | `"With reference to the Peninsular relief of India, how do the Western Ghats fundamentally differ from the Eastern Ghats?"` |
| 5 | `spatial` | $E$, $P$, $C$ | `"Where is '{evidence}' located?"` | **Pattern 5A**: `"In the structural profile of the Earth, {primaryEntity} is situated at which of the following zones?"`<br>**Pattern 5B**: `"Through which of the following coordinates/regions does {primaryEntity} pass?"` | `"In the internal structure of the Earth, the asthenosphere is located at which of the following depths?"` |
| 6 | `distribution` | $E$, $P$, $S$ | `"Which of the following is true regarding '{evidence}'?"` | **Pattern 6A**: `"Across which of the following physiographic regions is {primaryEntity} predominantly concentrated?"`<br>**Pattern 6B**: `"Which of the following belts accounts for the largest spatial distribution of {primaryEntity}?"` | `"Across which of the following physiographic regions of India are black regur soils predominantly distributed?"` |
| 7 | `classification` | $E$, $P$, $S$ | `"What is a direct consequence of '{evidence}'?"` | **Pattern 7A**: `"On what scientific basis are {primaryEntity} fundamentally classified into {secondaryEntities}?"`<br>**Pattern 7B**: `"Which of the following constitutes an acknowledged major category of {primaryEntity}?"` | `"On what geological basis are rocks classified into igneous, sedimentary, and metamorphic groups?"` |
| 8 | `quantity` | $E$, $P$, $Q$ (Value/Unit) | `"Consider the number in '{evidence}'. What is it?"` | **Pattern 8A**: `"What proportion of {domain} is constituted by {primaryEntity}?"`<br>**Pattern 8B**: `"At equatorial latitudes, the average height up to which the {primaryEntity} extends is approximately:"` | `"What proportion of the total volume of the Earth is constituted by the mantle?"` |
| 9 | `sequence` | $E$, $P$, $S$ (Stages) | `"What happens after '{evidence}'?"` | **Pattern 9A**: `"Which of the following represents the correct sequential order of stages in {primaryEntity}?"`<br>**Pattern 9B**: `"In the development of {primaryEntity}, which stage immediately succeeds {stage_n}?"` | `"Which of the following represents the correct evolutionary sequence in the life cycle of a solar-mass star?"` |
| 10 | `condition` | $E$, $P$, $C$ (Conditions) | `"What is a direct consequence of '{evidence}'?"` | **Pattern 10A**: `"Which of the following environmental prerequisites is indispensable for the formation of {primaryEntity}?"`<br>**Pattern 10B**: `"Under which of the following physical conditions does {primaryEntity} {action}?"` | `"Which of the following thermal thresholds is an indispensable prerequisite for the genesis of tropical cyclones?"` |
| 11 | `exception` | $E$, $P$, $S$ (Norm) | `"Which is an exception to '{evidence}'?"` | **Pattern 11A**: `"With reference to {drainage/domain}, which of the following represents a notable exception by {exceptional_behavior}?"`<br>**Pattern 11B**: `"While the majority of {group} exhibit {norm}, which of the following uniquely {exception}?"` | `"With reference to the drainage systems of Peninsular India, which of the following rivers flows westward into the Arabian Sea?"` |
| 12 | `process` | $E$, $P$, $S$ | `"What is a direct consequence of '{evidence}'?"` | **Pattern 12A**: `"Which of the following geodynamic mechanisms best describes the process of {primaryEntity}?"`<br>**Pattern 12B**: `"By which of the following geomorphic processes does {primaryEntity} develop?"` | `"Which of the following geodynamic mechanisms best describes the process of tectonic subduction?"` |
| 13 | `part-of` | $E$, $P$, $S$ (Whole) | `"What is a direct consequence of '{evidence}'?"` | **Pattern 13A**: `"The {primaryEntity} constitutes an integral structural component of which of the following layers of the Earth?"`<br>**Pattern 13B**: `"Which of the following structural zones directly encompasses {primaryEntity}?"` | `"The asthenosphere constitutes an integral structural component of which of the following internal layers of the Earth?"` |
| 14 | `member-of` | $E$, $P$, $S$ (Family) | `"What is a direct consequence of '{evidence}'?"` | **Pattern 14A**: `"To which of the following geological families does {primaryEntity} belong as an extrusive member?"`<br>**Pattern 14B**: `"Which of the following is classified as a prominent member of {group}?"` | `"To which of the following rock families does basalt belong as an extrusive member?"` |

---

## 5. Caveats
- No code was implemented or modified; this agent functioned solely in a read-only specification mining capacity.
- The `DataImporter.kt` explanation ordering quirk (where `Explanation:` must precede `Correct Answer:`) exists in the compiled Android repository code. While `format_candidate_to_markdown` in `tests/e2e/test_helpers.py` currently emits `Correct Answer:` before `Explanation:`, our empirical test showed this leads to `"No explanation"` in Room DB. Placing `Explanation:` before `Correct Answer:` fixes the issue without breaking any existing tests.
- Ontological distractor generation requires a structured domain ontology dictionary (e.g. Rock Types, Atmospheric Layers, Geomorphic Features, Indian Rivers, Climatic Phenomena); fallback handling must ensure 4 distinct, category-constrained options are always produced.

---

## 6. Conclusion
1. The data structures and interface contracts between `CandidateQuestion` (Python pipeline) and `Question` (Android Room DB) are fully mapped.
2. The 8 authorized Room DB trap types and their diagnostic pedagogical rationale templates are formally codified.
3. Strict anti-quotation rules and regex guard patterns are defined to permanently eliminate lazy quotation stems.
4. Natural, exam-style stem patterns are specified across all 14 semantic intents with exact slot bindings.
5. The pipeline is ready for implementation of `v13_discovery/question_synthesizer.py` in Milestone 4.

---

## 7. Verification Method
To independently verify the contracts, parser behaviors, and tests:
1. **Run Feature Coverage Tests**:
   ```bash
   python -m pytest tests/e2e/test_e2e_tier1_features.py -k "f08 or f09 or f10" -v
   ```
2. **Run Pairwise Synthesizer Tests**:
   ```bash
   python -m pytest tests/e2e/test_e2e_tier3_pairwise.py -k "p03 or p04 or p05" -v
   ```
3. **Inspect Key Source Contracts**:
   - `tests/e2e/test_helpers.py` (lines 86-101, 145-202, 210-227, 283-318)
   - `app/src/main/java/com/example/repository/DataImporter.kt` (lines 54-97, 109-126, 167-185)
   - `app/src/main/java/com/example/database/Entities.kt` (lines 30-47)
