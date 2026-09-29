# Handoff Report: Forensic Survey of V12 Content Discovery Pipeline & Test Suites

## 1. Observation

### 1.1 Pipeline Architecture & Call Graph (`v12_discovery_pipeline.py`)
Direct inspection of `c:\Users\harsh\Downloads\tayaari\tayaariapp\v12_discovery_pipeline.py` reveals the end-to-end execution flow:

- **Stage 1: Source Parser (`SourceParser.parse()`, lines 11–53)**:
  - Glob reads `source-material/*.txt` (fallback to `source-material/geography_extracted.txt`).
  - Implements a crude state machine using `skip_block` flag:
    ```python
    29: if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line) or re.match(r'^\([a-e]\)', line, re.IGNORECASE):
    30:     skip_block = True
    ...
    36: if re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
    37:     skip_block = False
    38:     line = re.sub(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*', '', line, flags=re.IGNORECASE)
    40: if "|" in line or line.startswith("http") or line.startswith("www"):
    44:     blocks.append({"sourceId": fn, "type": "TABLE_OR_META", "text": line})
    47: if not skip_block:
    48:     current_prose.append(line)
    ```
  - Joins lines with spaces (`" ".join(current_prose)`).

- **Stage 2: Knowledge Extractor (`KnowledgeExtractor.extract()`, lines 58–158)**:
  - Discards all blocks where `type != "PROSE"` (line 66).
  - Splits text into sentences using simple regex: `re.split(r'(?<=[.!?])\s+', block["text"])` (line 70).
  - Discards sentences outside character bounds: `len(sentence) < 20 or len(sentence) > 300` (line 73).
  - Discards sentences matching option markers: `re.search(r'\([a-e]\)', sentence) or re.search(r'\b[A-E]\b\)', sentence)` (line 77).
  - Applies exactly **five hardcoded regex patterns**:
    1. **COMPARISON** (line 84): `^([A-Z][a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects)\s+(.*?),?\s+(while|whereas)\s+([a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects|lies|focuses|grow|grows)\s+(.*)`
    2. **DEFINITION** (line 100): `^([A-Z][a-zA-Z\s]+)\s+(is known as|refers to|comprises|consists of|includes)\s+(.*)`
    3. **CAUSE_EFFECT_INVERTED** (line 114): `^([A-Z][a-zA-Z\s]+)\s+(is due to|occurs because of|is caused by)\s+(.*)`
    4. **CAUSE_EFFECT** (line 128): `^([A-Z][a-zA-Z\s]+)\s+(causes|leads to|results in)\s+(.*)`
    5. **SPATIAL** (line 142): `^([A-Z][a-zA-Z\s]+)\s+(is located in|borders|is situated in|flows through|lies in)\s+(.*)`
  - Rejects if any single word in subject is in `BAD_ENTITIES = {"it", "this", "that", "these", "those", "they", "he", "she", "which", "app", "download", "pinnacle"}` (line 59).

- **Stage 3: Intent Synthesizer (`IntentSynthesizer.synthesize()`, lines 163–275)**:
  - Builds global pools: `pools["DEFINITION"]`, `pools["CAUSE"]`, `pools["EFFECT"]`, `pools["LOC"]`, `pools["PRED_X"]`, `pools["PRED_Y"]` (lines 168–176).
  - Uses fixed template stems:
    - DEFINITION: `"Which of the following best describes the geographic concept of '{node['subj']}'?"` (line 202)
    - CAUSE_EFFECT_INVERTED: `"Which of the following is the primary geographic reason why {node['effect']}?"` (line 215)
    - CAUSE_EFFECT: `"What is a direct geographical consequence of {node['cause']}?"` (line 227)
    - SPATIAL: `"Which of the following accurately describes the spatial location of {node['subj']}?"` (line 239)
    - COMPARISON: `"Which of the following statements accurately compares {node['subj_x']} and {node['subj_y']}?"` (line 182)
  - Distractor generation:
    - DEFINITION / CAUSE / EFFECT / SPATIAL: Samples randomly from global pool matching only the verb string: `f"It {node['verb']} {p}."` (lines 208, 220, 232, 244).
    - COMPARISON: Swaps predicates `subj_x` + `pred_y` vs `subj_y` + `pred_x`, or mixes randomly from `pools["PRED_X"]` and `pools["PRED_Y"]` (lines 186, 193, 195).
  - Hardcoded cognitive demand and exam mapping:
    - DEFINITION -> always `SSC CGL` + `RECALL` (lines 210–211).
    - COMPARISON -> always `UPSC` + `COMPARE` (lines 197–198).
    - SPATIAL -> always `SSC CGL` + `RECALL` (lines 246–247).
    - CAUSE_EFFECT -> `UPSC` if `len(node['cause'].split()) > 6` else `BPSC`, always `UNDERSTAND` (lines 222–223, 234–235).

- **Stage 4: Quality Gate & Auditor (`BatchAuditor.audit()`, lines 280–307)**:
  - Deduplicates on exact string match: `q["text"] in texts_seen or q["options"][q["correctIndex"]] in answers_seen` (line 288).
  - Checks minimal length: `len(q["text"]) < 20 or "{" in q["text"]` (line 292).
  - Shuffles options, re-indexes answer, prepends UUID `Q-PROD-V12-{uuid[:8]}` (lines 298–301).
  - Contains **zero** semantic auditing, zero grammar checks, zero factual verification, and zero distractor plausibility validation.

---

### 1.2 Quantitative Extraction Results (`docs/v12_discovery_report.json`)
Inspection of `c:\Users\harsh\Downloads\tayaari\tayaariapp\docs\v12_discovery_report.json` documents the exact metrics of V12 execution on the real corpus:
- Sources processed: 5
- Source units: 1,204
- **Valid nodes extracted**: 23
- **Rejected nodes**: 3,785
- **Opportunity yield**: 17 questions
- **Accepted by gate**: 17 (0 rejected by gate)
- **Node Rejection Rate**: **99.39%** (3,785 out of 3,808 sentences rejected).
- **Cognitive Mix**: `COMPARE`: 5, `RECALL`: 12, `UNDERSTAND`: 0, `APPLY`: 0.

---

### 1.3 Verbatim Architectural Blunders in Generated V12 Questions
Direct quotes from `docs/v12_discovery_report.json`:

1. **Catastrophic Non-Entity Subject Extraction (False Acceptance)**:
   - *Question ID*: `Q-PROD-V12-518874c5` (lines 73–79)
     - **Stem**: `"Which of the following best describes the geographic concept of 'The  Nile basin  is  huge  and'?"`
     - **Source Sentence**: `"The Nile basin is huge and includes parts of Tanzania, Burundi, Rwanda, Congo (Kinshasa), Kenya."`
     - **Extracted Subject**: `'The Nile basin is huge and'`
     - **Cause**: Greedy regex `^([A-Z][a-zA-Z\s]+)\s+includes\s+(.*)` captures the clause conjunction `"and"` into the subject entity!
   - *Question ID*: `Q-PROD-V12-ad9a8717` (lines 44–50)
     - **Stem**: `"Which of the following best describes the geographic concept of 'The example of open channel flow'?"`
     - **Extracted Subject**: `'The example of open channel flow'`
   - *Question ID*: `Q-PROD-V12-418aaaef` (lines 450–456)
     - **Stem**: `"Which of the following best describes the geographic concept of 'Out  of  total  water resources  on  earth  Ocean'?"`
     - **Extracted Subject**: `'Out of total water resources on earth Ocean'`
     - **Source Sentence**: `"Out of total water resources on earth Ocean comprises 97.25%, Ice caps- 2.05%..."`

2. **Absurd Distractor Cross-Pollination (Domain Mismatch)**:
   - *Question ID*: `Q-PROD-V12-5c725fc7` (lines 15–21)
     - **Stem**: `"Which of the following statements accurately compares The  average  density  of oceanic  crust and continental  crust?"`
     - **Distractor 1**: `"The average density of oceanic crust has the highest share of out-migrants, whereas continental crust has an average of 2.7 g/cm 3 ."`
       *(Human migration statistics cross-polled into oceanic crust geology)*
     - **Distractor 3**: `"The average density of oceanic crust is 3.0 g/cm 3, whereas continental crust reduces visibility to one to two kilometers."`
       *(Atmospheric fog definition cross-polled into continental crust geology)*
   - *Question ID*: `Q-PROD-V12-71eb40e3` (lines 276–282)
     - **Stem**: `"Which of the following best describes the geographic concept of 'Ecological  diversity'?"`
     - **Distractor**: `"It includes 97.25%, Ice caps- 2.05%, Groundwater- 0.68%, Lakes- 0.1%, Soil moisture- 0.005% , Atmosphere- 0.001% , Streams and river- 0.0001% , Biosphere- 0.00004% ."`
       *(Global hydrosphere water distribution percentages injected as a distractor for biodiversity)*
   - *Question ID*: `Q-PROD-V12-8216311d` (lines 334–340)
     - **Stem**: `"Which of the following statements accurately compares Uttar  Pradesh and Maharashtra?"`
     - **Distractor 3**: `"Uttar pradesh reduces visibility to less than one kilometer, whereas Maharashtra has the highest share of in-migrants."`

3. **MCQ Parser Inversion & Explanation Destruction**:
   - In `source-material/question_extracted.txt` (lines 79–94):
     - The text contains an explanation for star life cycle:
       `1. Nebula / Protostar stage ...`
       `2. Main Sequence ...`
       `3. Red Giant ...`
       `4. White Dwarf ...`
     - Because line 80 matches `^\d+\.\s+[A-Z]`, `SourceParser` flips `skip_block = True` and discards all 4 stages because it mistakenly identifies numbered steps as question stems.

4. **OCR Artifacts**:
   - Pervasive double spaces inside entities: `'The  central stretch  of  Arabian  Sea'`, `'Kannad  Plain'`, `'The  Nile basin  is  huge  and'`.
   - Broken hyphenations (`flar es`).
   - Watermarks and page numbers (`PARMAR SSC`, `Pinnacle Geography`, `ISBN 81-7450-491-5`, `0656`, `Page 1`).

---

### 1.4 Test Suites Status

#### Python Test Suites
Executed via terminal with verbatim results:
1. `python -m unittest test_discovery_regression.py`
   - **Status**: PASSED (Ran 5 tests in 0.017s, OK).
   - **Finding**: Lines 18–19 and line 29 contain dummy `pass` statements with no assertions on rejection reasons.
2. `python -m unittest test_advanced_regression.py`
   - **Status**: PASSED (Ran 4 tests in 0.008s, OK).
3. `python -m unittest test_hardening_regression.py`
   - **Status**: **FAILED (2 Failures out of 5 tests)**:
     - Failure 1: `test_reject_in_rural`: `AssertionError: False is not true` (`"Invalid subject start"` not in reasons).
     - Failure 2: `test_valid_chota_nagpur`: `AssertionError: 'The Chota Nagpur plateau' != 'The Chota Nagpur'`.
4. `python -m unittest test_generator_v3.py`
   - **Status**: PASSED (Ran 8 tests in 0.005s, OK).
5. `python test_db.py`
   - **Status**: FAILED (`sqlite3.OperationalError: no such table: topics` in `dev-tools/geography_test.db`).
6. `python test_importer.py`
   - **Status**: FAILED (`FileNotFoundError: [Errno 2] No such file or directory: '/app/applet/source-material/consolidated_grounding.md'` due to hardcoded Linux container path).

#### Android Test Suites & Build
Executed via Gradle wrapper:
1. `.\gradlew.bat testDebugUnitTest`
   - **Status**: **BUILD SUCCESSFUL** (in 1m 6s).
   - **Unit Test Count**: **37 tests, 0 failures, 0 errors, 0 skipped**.
   - **XML Reports**: Verified across all test suites (`DatabasePersistenceTest`, `RealMigrationTest`, `BlueprintRegressionTest`, `ContentImportRulesTest`, `QuestionSelectionEngineTest`, `PracticeScoringRegressionTest`, `TrapLogicTest`, etc.).
2. `.\gradlew.bat assembleDebug`
   - **Status**: **BUILD SUCCESSFUL** (in 24s, 40 actionable tasks up-to-date).

---

## 2. Logic Chain

1. **From Observation 1.1 & 1.2 to High False Rejection Rate (99.4%)**:
   - V12 relies on 5 regex patterns strictly anchored to sentence start `^([A-Z][a-zA-Z\s]+)`.
   - In standard English textbooks (NCERT Class 6–12), sentences routinely begin with prepositional phrases ("In the northern hemisphere..."), adverbials ("Generally, ..."), pronouns ("They are made of..."), or passive constructions.
   - The verb whitelists are microscopic (e.g. Definition allows only `is known as`, `refers to`, `comprises`, `consists of`, `includes`; omitting `is defined as`, `means`, `denotes`, `represents`, `is called`, `are known as`, `is a`).
   - Consequently, out of 3,808 sentences parsed from the corpus, 3,785 (99.39%) were rejected. Only 23 nodes and 17 questions survived.

2. **From Observation 1.1 & 1.3 to Non-Entity False Acceptance**:
   - The regex `^([A-Z][a-zA-Z\s]+)` followed by a verb matches any sequence of alphabetic words.
   - When a sentence contains compound predicates or clauses ("The Nile basin is huge and includes..."), the regex greedily includes the conjunction `"and"` into the subject group.
   - The single-word check `any(w in self.BAD_ENTITIES for w in subj.lower().split())` checks individual words against single-word pronouns, but cannot detect clause fragments or invalid multi-word syntactic heads.
   - As a result, meaningless strings (`'The Nile basin is huge and'`, `'The example of open channel flow'`, `'Out of total water resources on earth Ocean'`) were recognized as valid concepts and emitted as exam questions without triggering any quality gate rejections.

3. **From Observation 1.1 & 1.3 to Semantic Distractor Corruption**:
   - V12 uses global pools (`pools["LOC"]`, `pools["DEFINITION"]`, `pools["PRED_X"]`) that lump together extractions across all topics.
   - When generating distractors for oceanic crust density, the synthesizer randomly draws predicates from human geography ("has the highest share of out-migrants") and meteorology ("reduces visibility to one to two kilometers").
   - This produces nonsensical, laughable options that destroy the cognitive demand and exam validity required for UPSC/BPSC/SSC.

4. **From Observation 1.1 & 1.3 to Complete Knowledge Type Omission**:
   - The schema supports only 5 relations: COMPARISON, DEFINITION, CAUSE_EFFECT, CAUSE_EFFECT_INVERTED, SPATIAL.
   - Crucial educational knowledge types required by R2 (classification, attribute, quantity/measurement, sequence/chronology, condition/rule, exception, process, part-of, member-of) have zero representation in the extraction rules.
   - Furthermore, `SourceParser` drops 100% of tabular data (`if "|" in line -> TABLE_OR_META`), discarding critical tabular facts (river lengths, mineral distributions, mountain passes, census data).

5. **From Observation 1.1, 1.3 & 1.4 to MCQ Leakage & Regressions**:
   - `SourceParser`'s binary toggle `skip_block` misinterprets numbered list items in explanations as question stems, dropping valuable explanation text.
   - Conversely, question stems lacking `Q.` or starting with "Consider the following" bypass the filter and pollute prose blocks.
   - Existing tests in `test_hardening_regression.py` already fail because earlier pipeline versions patched regexes without maintaining backward compatibility.

---

## 3. Caveats

- **External NLP Packages**: The local Python 3.12 environment has `pymupdf`, `pypdf`, `pytesseract`, `torch`, `scikit-learn`, `pytest`, and `requests` installed, but `spacy` and `nltk` are not currently installed. However, per requirement R2 & R4, external libraries can be installed or API-based LLMs can be utilized (valid `GEMINI_API_KEY` is present in `.env`).
- **Pre-packaged SQLite DB vs Assets**: `app/src/main/assets/tayaari.db` and `app/src/main/assets/geography_db` are pre-compiled SQLite databases. Dynamic ingestion at runtime is driven by `DataImporter.kt` parsing markdown files (such as `consolidated_grounding.md`).
- **Scope of Survey**: This survey is read-only and forensic. No modifications to application code or pipeline source code were made during this turn.

---

## 4. Conclusion

The V12 content discovery pipeline suffers from critical architectural deficiencies that make it unusable for production exam preparation without fundamental redesign:
1. **Recall Collapse**: A 99.4% false rejection rate due to brittle SVO regex matching.
2. **Semantic Incoherence**: Hallucinated distractors created by unconstrained cross-polling across unrelated knowledge domains.
3. **Severe False Acceptances**: Grammatical fragment capture (`'The Nile basin is huge and'`) entering production question pools.
4. **Knowledge Blindness**: Total inability to capture classifications, processes, tabular data, chronological sequences, and conditions.
5. **Auditing Absence**: Zero adversarial, cognitive, or exam-fit validation gates in `BatchAuditor`.

All 37 Android unit tests and the debug build (`assembleDebug`) currently pass, proving the Android application framework is healthy and ready to consume a properly engineered V13 pipeline.

### Specific Architectural Recommendations for V13
- **Dependency & Semantic Parsing (NLP / LLM-driven)**: Replace SVO regexes with structured semantic intent extraction mapping to the 14 explicit categories defined in R2.
- **Strict Distractor Validation Pipeline**: Distractors must be drawn from category-compatible entities within the same topic ontology, verified for grammatical agreement, semantic plausibility, and non-clueing.
- **Independent Multi-Agent Auditing**: Implement Cognitive, Exam-Fit, and Adversarial auditors using LLM quality gates to reject invalid generator outputs before database insertion.
- **Table & Multi-Format Ingestion**: Ingest tabular data and multi-line NCERT narrative structures rather than discarding non-prose blocks.

---

## 5. Verification Method

To independently reproduce and verify all observations and test results:

1. **Verify V12 Discovery Metrics**:
   ```powershell
   python v12_discovery_pipeline.py
   ```
   Inspect output and `docs/v12_discovery_report.json` to verify 23 valid nodes, 17 accepted questions, and 3,785 rejected nodes.

2. **Verify Python Test Regressions**:
   ```powershell
   python -m unittest test_discovery_regression.py
   python -m unittest test_advanced_regression.py
   python -m unittest test_hardening_regression.py
   python -m unittest test_generator_v3.py
   ```
   Observe that `test_hardening_regression.py` fails with 2 errors.

3. **Verify Android Test Suite & Build**:
   ```powershell
   .\gradlew.bat testDebugUnitTest
   .\gradlew.bat assembleDebug
   ```
   Confirm that all 37 Android unit tests pass and `assembleDebug` completes with `BUILD SUCCESSFUL`.

4. **Verify Generated Question Defects**:
   Inspect `docs/v12_discovery_report.json` lines 15–21, 44–50, 73–79, 276–282, 450–456 to verify verbatim quotes of non-entity subjects and absurd distractor cross-pollination.
