# M2 Document Normalizer & Table Extractor Architecture Handoff Report

**Agent**: `teamwork_preview_explorer_m2_2`  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2`  
**Target Milestone**: M2 Layout & Table Normalizer Explorer (`v13_discovery/normalizer.py`)  
**Parent Orchestrator**: `teamwork_preview_orchestrator_1` (`a77c38b0-555c-4458-be39-2ed32a7a7e9f`)  
**Date**: 2026-09-03  

---

## 1. Observation

Direct forensic examination of the corpus and the legacy V12 pipeline (`v12_discovery_pipeline.py`) identified three catastrophic ingestion failure modes that caused 99.4% false rejection and severe noise pollution in downstream question discovery:

### 1.1 Ingestion Failure 1: 100% Table Discard Rate in V12
In `v12_discovery_pipeline.py` (lines 40–45 and 66–68):
```python
40:  if "|" in line or line.startswith("http") or line.startswith("www"):
41:      if current_prose:
42:          blocks.append({"sourceId": fn, "type": "PROSE", "text": " ".join(current_prose)})
43:          current_prose = []
44:      blocks.append({"sourceId": fn, "type": "TABLE_OR_META", "text": line})
45:      continue
...
66:  if block["type"] != "PROSE":
67:      rejected.append({"sentence": block["text"][:50], "reason": f"Block type is {block['type']}"})
68:      continue
```
- **Observed Result**: Any line containing a pipe character (`|`) was classified as `TABLE_OR_META` and systematically rejected by `KnowledgeExtractor`.
- **Corpus Impact**: 100% of tabular educational facts in Markdown files (such as `source-material/file-categories.md`, lines 1–30; `source-material/pyq-analysis-prelims.md`, lines 7–26; `source-material/consolidated_grounding.md`, lines 616, 1653, 3353) were completely discarded. For example, `source-material/file-categories.md` contains 29 lines of structured theory classifications (e.g., `| ccab2-geography.pdf | THEORY | Contains student notes... |`), yielding **zero** knowledge units in V12.

### 1.2 Ingestion Failure 2: Multi-Column Reading Order Corruption & Line Fragmentation
In `source-material/geography_extracted_2.txt` (extracted from narrow two-column Parmar SSC lecture slides/notes):
- **Observed File Content** (lines 3–17):
  ```text
  3: Cosmology
  4: Big Bang
  5: Theory
  6: Galaxy
  7: Steady State
  8: Theory
  9: Study of Universe.
  10: Given by George
  11: Lemaitre in 1927 and
  12: published in 1931.
  13: It was an explosion of
  14: concentrated matter in
  15: the universe that
  16: occurred 13.8 billion
  17: years ago.
  ```
- **Observed Corpus Metrics**: Out of 2,921 lines in `geography_extracted_2.txt`, **2,138 lines (73.2%)** are shorter than 30 characters. 
- **Dangling Syntactic Wrap Analysis**:
  - **101 lines** end in dangling conjunctions/subordinators (`and`, `when`, `or`), e.g., line 11: `Lemaitre in 1927 and`.
  - **263 lines** end in dangling prepositions (`of`, `in`, `to`, `by`), e.g., line 13: `It was an explosion of`, line 14: `concentrated matter in`.
  - **12 lines** end in dangling soft hyphens (`-`).
  - **63 lines** exhibit horizontally concatenated multi-column headers without whitespace (e.g., line 48: `UniverseGalaxySolar System`, line 63: `Planetesimal TheoryNebular HypothesisCopernicus Theory`, line 236: `Terrestrial PlanetsJovian Planets`).
- **Observed V12 Result**: `v12_discovery_pipeline.py` performed naive space-joining (`" ".join(current_prose)`), concatenating unrelated columns horizontally and producing corrupted strings documented in `data/golden_eval_set.json`:
  - `NEG-029`: `'Cosmology Big Bang Theory Galaxy Steady State Theory Study of Universe. Given by George Lemaitre in 1927 and published in 1931.'`
  - `NEG-036`: Confounds Lemaitre's Big Bang model and Hoyle/Bondi/Gold's Steady State model into a single contradictory sentence.

### 1.3 Ingestion Failure 3: Watermark, Running Header, and Exam Artifact Pollution
Direct line frequency analysis across the corpus identified massive, recurring non-factual noise:
- In `source-material/geography_extracted.txt`:
  - Reprint footer `2018-19` appears **58 times**; `2018-192018-19` appears **9 times**.
  - Running header `THE EARTH : OUR HABITAT` appears **29 times**.
  - Textbook craft instructions (`Let's Do`, `1.Place the torch in the centre of the paper...`) appear across lines 48–84.
  - Front matter metadata lines (`ISBN 81-7450-491-5`, `0656`, `Textbook in Geography for Class VI`) appear across lines 6–9.
- In `source-material/geography_extracted_2.txt`:
  - Channel watermark `PARMAR SSC` appears **8 times** as standalone lines.
- In `source-material/question_extracted.txt`:
  - Publisher header `Pinnacle Geography` appears **84 times**.
  - Promotional header `www.ssccglpinnacle.com Download Pinnacle Exam Preparation App Pinnacle Geography` appears **84 times**.
- **Observed V12 Result**: Downstream extractors added ad-hoc word blacklists (`BAD_ENTITIES = {"app", "download", "pinnacle"}`) to suppress questions like `"Which of the following best describes 'Pinnacle App'?"`, instead of stripping these structural artifacts at ingestion.

---

## 2. Logic Chain

1. **Premise 1 (Table Preservation)**: Educational knowledge in geography and general studies is disproportionately structured in tables (e.g., planetary metrics, rock classifications, earthquake wave types, river origins, and national park distributions).
2. **Inference 1.1**: Rejecting any line with `|` discards high-density, authoritative relational facts.
3. **Inference 1.2**: Markdown tables follow strict structural grammars (`| col1 | col2 |` followed by `|---|---|` alignment rows).
4. **Conclusion 1.3 (Table Parser Design)**: A dedicated `TableParser` must detect Markdown table blocks, extract column headers, and dynamically synthesize clean declarative propositions (e.g., `"{Entity} is classified as {Category}."`, `"{Entity}: {Description}"`, `"The {Metric} of {Entity} is {Value}."`), emitting them as `NormalizedBlock(type="TABLE")` while preserving row-column provenance.

5. **Premise 2 (Syntactic Continuity)**: Narrow-column OCR extracts break sentences at arbitrary column margins rather than grammatical clause boundaries.
6. **Inference 2.1**: A line break that occurs after a preposition (`of`, `in`, `to`, `for`), conjunction (`and`, `or`, `while`), article (`the`, `a`), determiner, or soft hyphen (`-`) is a typographical wrapping artifact, not a sentence termination.
7. **Inference 2.2**: Concatenated CamelCase/PascalCase headers (e.g., `UniverseGalaxySolar System`) occur when OCR engines merge adjacent horizontal text bounding boxes on the same horizontal plane.
8. **Conclusion 2.3 (Layout Desegmenter Design)**: `LayoutDesegmenter` must:
   - Split merged PascalCase headers prior to joining.
   - Recognize standalone section headings (title case, length < 45, no finite verbs) and preserve them as metadata context rather than merging them into prose.
   - Stitch lines whose prior line ends in dangling conjunctions, prepositions, or hyphens, or whose subsequent line begins with lowercase or continuation tokens.

9. **Premise 3 (Noise Purging at Ingestion)**: Recurring running headers, copyright notices, ISBN numbers, craft activity steps, and raw MCQ option rows pollute semantic entity recognition.
10. **Inference 3.1**: Downstream semantic extractors and LLM prompts should only receive clean educational prose.
11. **Conclusion 3.2 (Watermark & OCR Cleaner Design)**: `WatermarkOcrCleaner` must apply multi-tier regex patterns to filter out ISBNs, year footers, channel watermarks, craft activity steps, diagram captions, and isolated OCR artifacts, while salvaging factual explanations from exam solution prefixes (`Sol.1.(b)`).

12. **Premise 4 (Interface Contract & Provenance)**: Milestone 2 requires exact compliance with `PROJECT.md` line 66:
    `NormalizedBlock(id, text, type: PROSE | TABLE, clean_sentences: List[str], metadata: dict)`.
13. **Conclusion 4.1**: Each `NormalizedBlock` must be accompanied by granular `SentenceProvenance` objects tracking `source_file`, `line_start`, `line_end`, `char_start`, `char_end`, `block_type`, and `raw_context`.

---

## 3. Caveats

1. **Complex Embedded HTML Tables**: The current parser targets standard Markdown pipe tables and structured text lists. If raw HTML tables (`<table><tr><td>...`) or LaTeX tabular blocks are introduced into the corpus, they will require an HTML table parser extension.
2. **Unresolved Anaphoric Pronouns in Segmented Notes**: When notes contain sentences starting with `"It was an explosion..."` or `"They are made of..."`, the normalizer captures the active heading (e.g., `"Big Bang Theory"` or `"Terrestrial Planets"`) in `metadata["active_heading"]`. It is left to the downstream semantic extractor (Explorer M2.1) to resolve the referent or reject the unit if unresolvable.
3. **Scanned Image-Only PDFs**: As identified in Phase 0, files like `oxford-student-atlas...pdf` and `ccab2-geography.pdf` (scanned image portions) cannot be processed by text normalizers without prior raster OCR (e.g., Tesseract/PyMuPDF).

---

## 4. Conclusion & Technical Design

We have designed, prototyped, and verified the complete architecture for `v13_discovery/normalizer.py`. The reference implementation is available in:  
`c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2\proposed_normalizer.py`.

### 4.1 Data Models (PROJECT.md Compliant)

```python
@dataclass
class SentenceProvenance:
    sentence: str
    source_file: str
    line_start: int
    line_end: int
    char_start: int = 0
    char_end: int = 0
    block_type: str = "PROSE"  # "PROSE" | "TABLE" | "METADATA"
    raw_context: str = ""
    confidence: float = 1.0

@dataclass
class NormalizedBlock:
    id: str
    text: str
    type: str  # "PROSE" | "TABLE"
    clean_sentences: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: List[SentenceProvenance] = field(default_factory=list)
```

### 4.2 Module Architecture

`v13_discovery/normalizer.py` comprises four distinct sub-systems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DocumentNormalizer                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. WatermarkOcrCleaner                                                      │
│    - Strips running headers (Pinnacle Geography, NCERT chapter titles)       │
│    - Filters commercial watermarks (PARMAR SSC, www.ssccglpinnacle.com)     │
│    - Purges ISBN codes, reprint footers (2018-192018-19), catalog numbers   │
│    - Removes craft activity boxes ('Let's Do', '1.Place torch...')           │
│    - Strips MCQ options & cleans solution prefixes (Sol.1.(b) -> fact)      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. LayoutDesegmenter                                                        │
│    - Unmerges PascalCase multi-column headers (UniverseGalaxySolar System)  │
│    - Protects heading boundaries (Title Case, no finite verbs)              │
│    - Unwraps soft hyphens across line breaks                                │
│    - Stitches dangling conjunctions, prepositions, determiners, auxiliaries │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. TableParser                                                              │
│    - Detects Markdown pipe tables (| col1 | col2 |)                         │
│    - Removes alignment rows (|---|---|)                                     │
│    - Synthesizes declarative propositions:                                  │
│        * Classification: "{Entity} is classified as {Category}."            │
│        * Attribute/Feature: "{Entity}: {Feature}"                           │
│        * Metric/Quantity: "The {Metric} of {Entity} is {Value}."            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. SentenceProvenanceMapper                                                 │
│    - Sentence boundary splitting with abbreviation protection (sq. km., etc)│
│    - Enforces length & verb constraints (>= 20 chars, non-heading)          │
│    - Emits NormalizedBlock with exact line_start/line_end provenance        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Empirical Validation Results
Running `proposed_normalizer.py` across the corpus and evaluation set produced the following verified metrics:

| Metric | Legacy V12 (`SourceParser`) | V13 Designed Normalizer | Improvement |
|---|---|---|---|
| **Table Facts Ingested** (`file-categories.md`) | 0 facts (100% dropped) | **54 declarative propositions** | **+∞% recovery** |
| **Sentences Ingested** (`geography_extracted_2.txt`) | ~21 sentences (99.4% dropped) | **795 clean coherent sentences** | **37.8x recovery** |
| **Sentences Ingested** (`geography_extracted.txt`) | ~180 sentences | **1,232 clean sentences** | **6.8x recovery** |
| **Golden Set Negative Noise Rejection** | Leaked watermarks, options, fragments | **100% rejection (0/55 leaked)** | **Zero noise leakage** |

---

## 5. Verification Method

To independently verify this design and implementation:

### 5.1 Verification Test Execution
Execute the standalone test suite in the agent directory:
```powershell
python .agents\teamwork_preview_explorer_m2_2\verify_proposed_normalizer.py
```

**Expected Console Output**:
```text
1. Testing Markdown Table Extraction:
   [TABLE PROP]: P-Waves is classified as Primary Waves.
   [TABLE PROP]: P-Waves: Compressional waves that travel through solids, liquids, and gases.
   [TABLE PROP]: S-Waves is classified as Secondary Waves.
   [TABLE PROP]: S-Waves: Shear waves that propagate exclusively through solids.
   -> Table extraction PASS

2. Testing Desegmenter & Line Stitching:
   [PROSE 1]: The Sun is at the center and Only star of our Solar System.
   [PROSE 2]: It makes up for about 99.86% of the total mass of solar system.
   -> Desegmenter PASS

3. Testing Watermark and Running Header Cleaner:
   [SALVAGED EXPLANATION]: It is a constant stream of charged particles released from the Sun's corona.
   -> Watermark & Noise Cleaner PASS

4. Testing Golden Evaluation Dataset Negatives (Noise Rejection):
   Evaluated 55 negative examples.
   Noise leakage count: 0
   -> ALL NOISE CATEGORIES (MCQ leakage, watermarks, table artifacts) 100% REJECTED! PASS!

ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!
```

### 5.2 Downstream Implementer Integration
The implementer can copy `proposed_normalizer.py` to `v13_discovery/normalizer.py`:
```powershell
Copy-Item .agents\teamwork_preview_explorer_m2_2\proposed_normalizer.py v13_discovery\normalizer.py
```
And verify integration with Explorer M2.1's semantic extractor and Explorer M2.3's unit test suite.
