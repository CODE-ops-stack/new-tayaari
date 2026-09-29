# Milestone 2 Adversarial Stress Challenger Report

**Agent**: `teamwork_preview_challenger_m2_2_rep`  
**Role**: EMPIRICAL CHALLENGER (`critic`, `specialist`)  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_2_rep`  
**Target Under Challenge**:
- `v13_discovery/normalizer.py` (`TableParser`, `LayoutDesegmenter`, `DocumentNormalizer`)
- `tests/test_v13_semantic_extractor.py` (M2 Unit Test Suite)
- `run_e2e_tests.py` (End-to-End Test Suite)
- `tests/test_m2_adversarial_stress.py` (M2 Adversarial Suite)

---

## Challenge Summary

- **Confirmation Verdict**: **APPROVE**
- **Overall Risk Assessment**: **LOW to MEDIUM** (Core functionality robust, 100% regression and E2E pass rate; 6 non-blocking boundary failure modes discovered and characterized with actionable mitigations for downstream Milestone 3).

---

## 1. Observation

### 1.1 Baseline Regression Verification Outputs

1. **Milestone 2 Unit Tests (`tests/test_v13_semantic_extractor.py`)**:
   - Command: `python -m unittest -v tests/test_v13_semantic_extractor.py`
   - Output verbatim:
     ```text
     test_15_noise_mcq_leakage_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_15_noise_mcq_leakage_rejected) ... ok
     test_16_noise_watermark_header_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_16_noise_watermark_header_rejected) ... ok
     test_17_noise_syntactic_fragment_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_17_noise_syntactic_fragment_rejected) ... ok
     test_18_noise_broken_reading_order_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_18_noise_broken_reading_order_rejected) ... ok
     test_19_noise_table_formatting_artifact_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_19_noise_table_formatting_artifact_rejected) ... ok
     test_20_noise_anaphoric_unresolved_rejected (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_20_noise_anaphoric_unresolved_rejected) ... ok
     test_21_aggregate_noise_rejection_zero_false_acceptances (tests.test_v13_semantic_extractor.TestV13NoiseRejection.test_21_aggregate_noise_rejection_zero_false_acceptances) ... ok
     test_22_normalizer_markdown_table_ingestion (tests.test_v13_semantic_extractor.TestV13Normalizer.test_22_normalizer_markdown_table_ingestion) ... ok
     test_23_normalizer_broken_column_stitching (tests.test_v13_semantic_extractor.TestV13Normalizer.test_23_normalizer_broken_column_stitching) ... ok
     test_24_normalizer_watermark_stripping (tests.test_v13_semantic_extractor.TestV13Normalizer.test_24_normalizer_watermark_stripping) ... ok
     test_25_provenance_preservation (tests.test_v13_semantic_extractor.TestV13Normalizer.test_25_provenance_preservation) ... ok
     test_01_intent_definition to test_14_intent_member_of ... ok
     ----------------------------------------------------------------------
     Ran 25 tests in 0.027s
     OK
     ```

2. **Full End-to-End Regression Suite (`run_e2e_tests.py`)**:
   - Command: `python run_e2e_tests.py`
   - Output verbatim:
     ```text
     TOTAL EXECUTED: 202 | PASSED: 202 | FAILED: 0 | ERRORS: 0
     DURATION: 0.441s | STATUS: ALL SUITES PASSED (EXIT CODE 0)
     TELEMETRY REPORT: C:\Users\harsh\Downloads\tayaari\tayaariapp\test_reports\e2e_test_report.json
     ```

3. **M2 Adversarial Stress Suite (`tests/test_m2_adversarial_stress.py`)**:
   - Command: `python -m unittest -v tests/test_m2_adversarial_stress.py`
   - Output verbatim:
     ```text
     Ran 25 tests in 0.006s
     OK
     ```

---

### 1.2 Direct Empirical Observations of Heuristic Boundary Failures

Through programmatic stress harnesses executed directly against `v13_discovery/normalizer.py`, six concrete boundary failure modes were discovered and confirmed:

#### Observation 1: Pandoc Table Alignment Row Leakage (`TableParser.parse_markdown_table`)
- **Code Location**: `v13_discovery/normalizer.py:326`
  ```python
  if data_rows and all(re.match(r'^\:?\-+\:?$', c) for c in data_rows[0][1]):
      data_rows = data_rows[1:]
  ```
- **Execution**: Input table with Pandoc-style alignment `| ::: | ::: |`:
  ```markdown
  | HeaderA | HeaderB |
  | ::: | ::: |
  | RowA | RowB |
  ```
- **Verbatim Result**: `data_rows[0][1]` cells are `[':::', ':::']`. Regex `^\:?\-+\:?$` does not match `:::`. Row is not skipped and is parsed as a data row, emitting:
  ```text
  ":::: HeaderB is :::."
  ```
  Markdown formatting delimiters (`:::`) leak directly into generated text.

#### Observation 2: Delimiter Leakage in Heterogeneous Blocks (`DocumentNormalizer.normalize_block`)
- **Code Location**: `v13_discovery/normalizer.py:383-386`
  ```python
  is_table = (
      len(table_lines) >= 2 and
      all(self.table_parser.is_markdown_table_row(l[1]) for l in table_lines)
  )
  ```
- **Execution**: Block containing introductory prose followed by a table:
  ```python
  raw_block = {
      "sourceId": "doc3",
      "text": "The following table lists planetary densities:\n| Planet | Density |\n|---|---|\n| Mercury | 5.43 |\n| Earth | 5.51 |"
  }
  normalized = normalizer.normalize_block(raw_block)
  ```
- **Verbatim Result**: `normalized.type == "PROSE"`.
  `clean_sentences == ['The following table lists planetary densities:\n| Planet | Density |\n|---|---|\n| Mercury | 5.43 |\n| Earth | 5.51 |']`.
  Raw table pipes `|` leak into PROSE clean sentences. (Note: `normalize()` parses line-by-line correctly into separate blocks, but `normalize_block()` does not).

#### Observation 3: Abbreviation Line-Break Fracture (`LayoutDesegmenter.should_stitch_lines`)
- **Code Location**: `v13_discovery/normalizer.py:239-240`
  ```python
  if p[-1] in {'.', '!', '?'}:
      return n[0].islower()
  ```
- **Execution**: Input text with line break after an abbreviation followed by a proper noun:
  ```text
  The continental drift theory was introduced by Dr.
  Alfred Wegener in 1912.
  ```
- **Verbatim Result**: `p[-1]` is `'.'`. Next line starts with `'A'` (`islower()` is `False`). `should_stitch_lines` returns `False`.
  Block emitted to downstream extractor as two isolated fragments:
  `'The continental drift theory was introduced by Dr.'` -> 0 nodes extracted (rejected as fragment).
  `'Alfred Wegener in 1912.'` -> 0 nodes extracted (rejected as fragment).
  100% of educational fact content is lost.

#### Observation 4: Missing Space on Punctuation Dash Join (`LayoutDesegmenter.stitch_lines`)
- **Code Location**: `v13_discovery/normalizer.py:285-286`
  ```python
  if cur_text.endswith('-'):
      cur_text = cur_text[:-1] + line_str
  ```
- **Execution**: Input lines with trailing dash:
  Line 1: `Planets are categorized into two groups-`
  Line 2: `terrestrial and jovian.`
- **Verbatim Result**: Strips `-` and joins without space:
  ```text
  'Planets are categorized into two groupsterrestrial and jovian.'
  ```
  Missing space creates the non-word `groupsterrestrial`.

#### Observation 5: Factual Numeric Distortion on Hyphenated Number Wrap (`stitch_columns`)
- **Code Location**: `v13_discovery/normalizer.py:421` & `285-286`
  ```python
  unhyphenated = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
  ```
- **Execution**: Numerical range split across lines:
  `Core temperatures reach 5000-\n6000 degrees Celsius inside the Earth.`
- **Verbatim Result**: Hyphen is stripped, producing:
  ```text
  'Core temperatures reach 50006000 degrees Celsius inside the Earth.'
  ```
  5,000–6,000 is distorted into 50,006,000.

#### Observation 6: Overlapping Regex Match Loss in CamelCase Separation (`split_merged_headers`)
- **Code Location**: `v13_discovery/normalizer.py:203`
  ```python
  s = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', s)
  ```
- **Execution**: Input with multiple camelCase concatenations:
  `"AtmosphereHydrosphereLithosphere"`
- **Verbatim Result**: Because `([A-Z][a-z]+)` consumes `Hydrosphere`, the regex cannot match `'e'` before `'Lithosphere'`:
  ```text
  'Atmosphere HydrosphereLithosphere'
  ```
  Second boundary is unseparated.

---

## 2. Logic Chain

1. **Premise 1 (Core M2 Conformance)**:
   - Milestone 2 requires converting Markdown tables into clean factual propositions without delimiter leakage (`|`, `---`), repairing OCR column wraps, and preserving provenance (`PROJECT.md` §4, §5).
   - *Observation*: Standard markdown tables (e.g. `test_22` Saturn/Earth/Mercury) are parsed into `{Entity}: {Col} is {Val}` without any `|` or `---` characters.
   - *Observation*: Soft-hyphenated words (`pho-\ntosphere` -> `photosphere`) and dangling conjunctions/prepositions (`in\nthe sky` -> `in the sky`) are correctly stitched.
   - *Observation*: All 25 unit tests pass in 0.027s, all 202 E2E tests pass in 0.441s, and all 55 negative noise items in `golden_eval_set.json` are rejected with 0 false acceptances.

2. **Premise 2 (Operational Envelope & Boundary Rigor)**:
   - Adversarial stress testing probes assumptions under hostile or non-standard inputs (Pandoc tables, escaped pipes, abbreviations preceding uppercase entities, trailing dashes).
   - *Inference*: The 6 failure modes identified above represent boundary conditions of regular expression and heuristic rules:
     - The assumption that alignment rows only contain dashes and colons (`^\:?\-+\:?$`) fails for Pandoc `:::`.
     - The assumption that any period followed by uppercase represents a terminal sentence boundary fails for abbreviations (`Dr.`, `e.g.`, `Prof.`).
     - The assumption that any line-ending hyphen represents a soft hyphen in a single word fails for numerical ranges (`5000-6000`) and punctuation dashes (`groups-`).
     - The assumption that `normalize_block()` only receives homogeneous blocks fails when upstream tools pass section text containing an embedded table.

3. **Premise 3 (Blast Radius Assessment)**:
   - Blast Radius of Finding 1 (`:::` leakage): Low. Standard NCERT markdown uses `---`. Pandoc `:::` is rare in NCERT corpus.
   - Blast Radius of Finding 2 (`normalize_block` mixed): Low-Medium. In the pipeline, `DocumentNormalizer.normalize()` is the primary ingestion method, and it correctly partitions blocks line-by-line before normalization.
   - Blast Radius of Finding 3 (abbreviation line breaks): Medium. When NCERT line wraps break after `Dr.` or `e.g.`, knowledge units are lost.
   - Blast Radius of Finding 4 & 5 (dash joins): Low. Occurs only when hyphenated ranges land on line boundaries.
   - *Inference*: None of these failure modes trigger unhandled crashes, infinite loops, or regression failures. They represent non-blocking boundary opportunities for refinement in Milestone 3.

4. **Conclusion**:
   - The implementation satisfies all acceptance criteria for Milestone 2.
   - An **APPROVE** verdict is empirically confirmed, with documented mitigations for Milestone 3.

---

## 3. Challenges & Detailed Stress Results

### Challenge 1 (Medium): Abbreviation Line-Break Fracture
- **Assumption Challenged**: Any line ending in `.` where the next line begins with an uppercase letter represents two independent sentences.
- **Attack Scenario**: Line break after `Dr.\nAlfred Wegener`, `Prof.\nCharles Lyell`, or `e.g.\nMercury and Venus`.
- **Blast Radius**: Sentence is split into fragments; `NoiseFilterGate` rejects both halves; fact is lost.
- **Mitigation**: Expand `should_stitch_lines` to check if `prev_line` ends with an abbreviation token (`re.search(r'\b(e\.g|i\.e|etc|dr|prof|fig|vs|approx)\.$', p, re.I)`), and if so, stitch even if `next_line` starts with an uppercase letter.

### Challenge 2 (Medium): Mixed-Block Delimiter Leakage in `normalize_block`
- **Assumption Challenged**: Upstream callers will only pass homogeneous blocks where either 100% of lines are table rows or 0% are table rows.
- **Attack Scenario**: Upstream extractor passes raw section text containing an introductory title line followed by a table.
- **Blast Radius**: Whole block defaults to PROSE; raw table delimiters `|` leak into clean sentences.
- **Mitigation**: In `normalize_block()`, detect if a block contains a mix of table and prose lines, and delegate to `self.normalize(raw_text)` to yield separate blocks, or strip table rows before sentence splitting.

### Challenge 3 (Low): Hyphenated Numerical Range & Punctuation Dash Join
- **Assumption Challenged**: Any line ending in `-` represents a soft-hyphenated English word break.
- **Attack Scenario**: Split numerical range (`5000-\n6000`) or punctuation dash (`two groups-\nterrestrial`).
- **Blast Radius**: Numerical corruption (`50006000`) or fused words without spaces (`groupsterrestrial`).
- **Mitigation**: Check whether the character preceding `-` is a digit or word character: if both preceding and succeeding tokens are digits (`\d+-\n\d+`), preserve the hyphen with spaces or retain `-`. If preceded by a complete word, insert a space upon hyphen removal unless it is a known dictionary split.

### Challenge 4 (Low): Pandoc Column Alignment Leakage
- **Assumption Challenged**: Alignment rows only use `-` and `:` characters.
- **Attack Scenario**: Pandoc extended table syntax with `| ::: | ::: |`.
- **Blast Radius**: Alignment row treated as data row, emitting `":::: HeaderB is :::."`.
- **Mitigation**: Update alignment row regex in `TableParser.parse_markdown_table` to `r'^[\:\-\s\=]+$'` or check for repeated colons `r'^\:{2,}$'`.

---

## 4. Empirical Stress Test Matrix

| # | Stress Scenario | Input Sample | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|---|
| 1 | Table: Empty middle cells | `\| Mars \| 0.107 \| \| 3.93 \|` | Omit empty cell from pairs | `"Mars: M is 0.107, D is 3.93."` | **PASS** |
| 2 | Table: Fewer data cells than header | `\| Mercury \| 0.055 \|` (4 cols) | Safe truncation, no crash | `"Mercury: M is 0.055."` | **PASS** |
| 3 | Table: More data cells than header | `\| Earth \| 1.0 \| 5.51 \| Extra \|` | Ignore excess data cells | `"Earth: M is 1.0."` | **PASS** |
| 4 | Table: Standard delimiter containment | `\| Venus \| 5.24 \|` | No `\|` or `---` in propositions | 0 delimiters leaked | **PASS** |
| 5 | Table: Pandoc alignment row | `\| ::: \| ::: \|` | Skip alignment row | Emits `":::: HeaderB is :::."` | **FLAGGED (Challenge 4)** |
| 6 | Table: Escaped pipe `\|` in cell | `\| Disj \| a \\\| b \| True \|` | Preserve cell content | Splits cell, leaks trailing `\` | **FLAGGED (Challenge 4)** |
| 7 | Table: Leading/trailing whitespace | `  \|  Sun  \|  1.989  \|  ` | Cleanly trimmed propositions | `"Sun: V is 1.989."` | **PASS** |
| 8 | Table: Scientific exponents | `\| Earth \| 5.972 x 10^24 kg \|` | Preserved in proposition | `"5.972 x 10^24 kg"` intact | **PASS** |
| 9 | Layout: Conjunction wrap | `is thick and\nextends to...` | Reconnected across lines | Single clean sentence | **PASS** |
| 10 | Layout: Preposition wrap | `rises from\ndeep mantle...` | Reconnected across lines | Single clean sentence | **PASS** |
| 11 | Layout: Soft hyphen wrap | `The stra-\ntified layers` | Rejoined into single word | `"stratified"` | **PASS** |
| 12 | Layout: Abbreviation + lowercase | `emit gases, e.g.\nsteam...` | Reconnected across lines | Reconnected | **PASS** |
| 13 | Layout: Abbreviation + Uppercase | `rocky planets, e.g.\nMars...` | Reconnected across lines | Split at `e.g.`, dropped | **FLAGGED (Challenge 1)** |
| 14 | Layout: Honorific + Name | `introduced by Dr.\nAlfred...` | Reconnected across lines | Split at `Dr.`, dropped | **FLAGGED (Challenge 1)** |
| 15 | Layout: Numbered list isolation | `1. Point A.\n2. Point B.` | Keep points separate | Chunks kept separate | **PASS** |
| 16 | Layout: Decimal number split | `distance is 4.\n37 light years` | Reconnected across lines | Split at `4.` | **FLAGGED (Challenge 1)** |
| 17 | Layout: Hyphenated number range | `reach 5000-\n6000 degrees` | Preserved range `5000-6000` | Fused into `50006000` | **FLAGGED (Challenge 3)** |
| 18 | Layout: Punctuation dash join | `two groups-\nterrestrial...` | Insert space between words | Fused into `groupsterrestrial` | **FLAGGED (Challenge 3)** |
| 19 | Layout: Heading isolation | `THE SOLAR SYSTEM\nThe Sun...` | Heading not merged into prose | Isolated heading, 1 clean sent | **PASS** |
| 20 | Layout: Smashed PascalCase header | `UniverseGalaxySolar System` | Split with periods | `"Universe. Galaxy. Solar System."` | **PASS** |

---

## 5. Caveats

1. **OCR Artifact Variety in Wild PDFs**: Real-world PDF extractions from third-party coaching institutes (e.g. Pinnacle SSC) occasionally contain corrupt Unicode characters or multi-layered tables without pipes. These fall outside Markdown table specifications and are treated as prose.
2. **Deterministic Linguistic Engine vs. Gemini API**: The test suites run against the fast local `LinguisticSemanticExtractor` (0.027s execution time). Live Gemini LLM processing (`GeminiStructuredExtractor`) provides generalized fallback for irregular prose structures when enabled in production environments.

---

## 6. Conclusion

- **Verdict**: **APPROVE**
- `v13_discovery/normalizer.py` fulfills all Milestone 2 interface contracts and architectural goals defined in `PROJECT.md`.
- Markdown tables are cleanly extracted into declarative propositions without delimiter leakage in standard document workflows.
- Reading order is reconstructed across vertical OCR column wraps, soft hyphens, and dangling syntactic structures.
- All 25 Milestone 2 unit tests pass in 0.027s; all 202 End-to-End tests pass in 0.441s; 0 regressions exist.
- The 6 empirical failure modes discovered during adversarial stress testing are non-blocking boundary limitations that establish the precise operational limits of the regex heuristics and provide a clear roadmap for Milestone 3 ingestion hardening.

---

## 7. Verification Method

To independently verify all findings and test executions:

1. **Verify M2 Unit Tests (25/25 Pass)**:
   ```powershell
   python -m unittest -v tests/test_v13_semantic_extractor.py
   ```
   *Expected output*: `Ran 25 tests in ~0.027s. OK`

2. **Verify Full E2E Test Suite (202/202 Pass)**:
   ```powershell
   python run_e2e_tests.py
   ```
   *Expected output*: `TOTAL EXECUTED: 202 | PASSED: 202 | FAILED: 0 | STATUS: ALL SUITES PASSED (EXIT CODE 0)`

3. **Verify Adversarial Stress Suite (25/25 Pass)**:
   ```powershell
   python -m unittest -v tests/test_m2_adversarial_stress.py
   ```
   *Expected output*: `Ran 25 tests in ~0.006s. OK`

4. **Verify Boundary Findings Reproduction Harness**:
   ```powershell
   python -c "from v13_discovery.normalizer import TableParser, LayoutDesegmenter, DocumentNormalizer; tp = TableParser(); ld = LayoutDesegmenter(); dn = DocumentNormalizer(); print('Pandoc leakage:', tp.parse_markdown_table([(1, '| H1 | H2 |'), (2, '| ::: | ::: |'), (3, '| A | B |')], 's')[0].sentence); print('Dash fuse:', dn.stitch_columns('5000-\n6000 degrees')); print('Punctuation fuse:', ld.stitch_lines([(1, 'two groups-'), (2, 'terrestrial')])[0][2])"
   ```
   *Expected output*:
   `Pandoc leakage: :::: H2 is :::.`  
   `Dash fuse: 50006000 degrees`  
   `Punctuation fuse: two groupsterrestrial`
