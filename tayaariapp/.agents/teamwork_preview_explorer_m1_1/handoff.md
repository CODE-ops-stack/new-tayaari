# Golden Evaluation Dataset Investigation & Design Report (M1)

**Agent**: `teamwork_preview_explorer_m1_1`  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1`  
**Milestone**: M1 (Forensic Baseline & Golden Eval Set)  
**Deliverable Artifact**: `data/golden_eval_set.json` (and mirror at `.agents/teamwork_preview_explorer_m1_1/golden_eval_set.json`)

---

## 1. Observation

### 1.1 Forensic Analysis of Corpus and Legacy Extraction Failures
1. **Corpus Assets Profiled**:
   - `source-material/geography_extracted.txt`: 2,625 lines, 93,106 bytes. Standard NCERT Class VI Geography ("The Earth Our Habitat") containing prose definitions, conceptual narratives, figure captions (e.g. line 89 `Figure 1.1 : Saptarishi and the North Star`), publisher metadata (line 6 `ISBN 81-7450-491-5`), and activity instructions (lines 49-58 `Let's Do... Place the torch...`).
   - `source-material/geography_extracted_2.txt`: 2,921 lines, 61,708 bytes. Competitive examination study notes (Parmar SSC) exhibiting severe multi-column layout collisions (lines 3-12 `Cosmology Big Bang Theory Galaxy Steady State Theory Study of Universe`), merged section headers (lines 48-52 `UniverseGalaxySolar System`), and recurring branding watermarks (line 60 `PARMAR SSC`).
   - `source-material/question_extracted.txt`: 15,329 lines, 586,049 bytes. 925 SSC Stenographer/CGL PYQ question blocks with comprehensive pedagogical solutions containing rich scientific facts, but heavily contaminated by option markers (lines 10-11 `(a) Sunspots (b) Solar wind`), shift timestamps (line 9 `SSC Stenographer 6/08/2025 (Shift 2)`), and solution prefixes (line 12 `Sol.1.(b) Solar wind.`).
   - `source-material/consolidated_grounding.md`: 18,429 lines, 570,204 bytes. Markdown question database containing UPSC Prelims and SSC PYQ records wrapped in fenced code blocks and metadata keys (e.g., `- **Topic**: 1. The Earth in the Solar System`, `Correct answer: option d`).
   - `source-material/supplementary_corpus.txt`: 5 lines, 781 bytes. High-density prose covering biomes, mineral economics, and demographic concentrations.
   - `corpus_data.json`: 325 lines, 19,384 bytes. Verified NCERT Class 11 physical geography concepts with distractor rationales and exam targets.

2. **Root Cause of V12 High False Rejection Rate (99.4%)**:
   - Inspection of `v12_discovery_pipeline.py` (lines 83-158) reveals that extraction relied on exactly five brittle regexes (`COMPARISON`, `DEFINITION`, `CAUSE_EFFECT_INVERTED`, `CAUSE_EFFECT`, `SPATIAL`).
   - Every single regex required `^([A-Z][a-zA-Z\s]+)` at the start of the sentence.
   - Consequently, any valid factual sentence beginning with:
     - Numerical measurements or dates (`"In 1927, George Lemaitre proposed..."`, `"More than 97% of Earth's water..."`)
     - Prepositional phrases or subordinate clauses (`"According to NCERT..."`, `"Under high pressure..."`, `"When water vapor cools..."`)
     - Pronouns or complex noun phrases (`"The life cycle of a star..."`)
     was summarily rejected at line 156 with `"Did not match strict structural semantic forms"`.
   - Furthermore, `v12_discovery_pipeline.py` line 44 rejected all lines containing `|`, `http`, or `www` as `TABLE_OR_META`, completely ignoring legitimate table knowledge.

3. **Legacy Test Regressions**:
   - In `test_hardening_regression.py` lines 21-28 (`test_reject_plateaus_malformed`), the test verified:
     `blocks = [{"sourceId": "test", "text": "Plateaus can be formed due to volcanic activity."}]`
     `claims, rejected = extractor.extract(blocks)`
     `self.assertEqual(len(claims), 0) # Our strict rules don't match "can be formed due to"`
   - This proves that legitimate geological knowledge was intentionally suppressed to prevent bad distractor generation under the old regex architecture.

---

## 2. Logic Chain

### 2.1 Bridging from Corpus Failure Modes to Golden Evaluation Dataset
- **Step 1: Grounding Requirement R2**: Requirement R2 mandates mapping source blocks to 14 explicit semantic intents:
  `definition`, `attribute`, `cause/effect`, `comparison`, `spatial`, `distribution`, `classification`, `quantity`, `sequence`, `condition`, `exception`, `process`, `part-of`, `member-of`.
- **Step 2: Representation Coverage**: To evaluate any prospective extractor (whether Regex, SpaCy Dependency Parsing, or LLM-based parsing), the evaluation dataset must contain balanced, verified positive exemplars for every single intent. Selecting 4 distinct real corpus sentences per intent produces $14 \times 4 = 56$ positive examples, satisfying and exceeding the $\ge 50$ requirement.
- **Step 3: Negative Category Profiling**: Ingestion pipelines fail not randomly, but along specific syntactic and document-level failure modes. Directly examining `geography_extracted.txt`, `geography_extracted_2.txt`, and `question_extracted.txt` revealed six concrete failure categories:
  1. `mcq_leakage`: Option markers (`(a)`, `(b)`), answer indices (`Sol.1.(b)`), and exam answer pointers (`Correct answer: option d`).
  2. `watermark_header`: Publisher watermarks (`PARMAR SSC`), document metadata (`ISBN 81-7450-491-5`), and shift tags.
  3. `syntactic_fragment`: Sentences cut off mid-thought (`The Nile basin is huge and`, `Out of total water resources...`, `In Rural, Himachal Pradesh...`).
  4. `broken_reading_order`: Naïve horizontal scanning across vertical columns (`Cosmology Big Bang Theory Galaxy Steady State Theory...`, `UniverseGalaxySolar System`).
  5. `table_formatting_artifact`: Raw markdown table pipes (`| Topic | Tier |`), alignment delimiters (`|---|---|`), and craft activity lists (`1 torch, 1 sheet of plain paper...`).
  6. `anaphoric_unresolved`: Pronouns and demonstratives detached from antecedents (`They are made up of gases.`, `It makes up for about 99.86%...`, `These are called constellations.`).
- **Step 4: Balanced Distribution**: Allocating 9 to 10 real examples to each of the 6 rejection categories yields $10 + 9 + 9 + 9 + 9 + 9 = 55$ negative examples, satisfying and exceeding the $\ge 50$ requirement. Total dataset size is 111 examples.
- **Step 5: Unbreakable Provenance & Rigorous Schema**: Every entry includes explicit lineage: `source_file`, `line_or_page`, `raw_context`, structured `semantic_entities` (`primary_entity`, `predicate`, `secondary_entities`), and educational rationale.

---

## 3. Dataset Specification & Schema

### 3.1 Dataset Metadata Summary
| Metric | Value | Requirement | Status |
|---|---|---|---|
| **Total Evaluation Units** | 111 | $\ge 100$ | **EXCEEDED** |
| **Total Positive Units** | 56 | $\ge 50$ | **EXCEEDED** |
| **Semantic Intents Covered** | 14 of 14 | All 14 R2 intents | **100% COVERAGE** |
| **Units per Positive Intent** | Exactly 4 | $\ge 1$ | **BALANCED** |
| **Total Negative Units** | 55 | $\ge 50$ | **EXCEEDED** |
| **Rejection Categories Covered** | 6 of 6 | All 6 corpus error types | **100% COVERAGE** |
| **Units per Rejection Category** | 9 to 10 | $\ge 5$ | **BALANCED** |
| **Provenance Integrity** | 100% (111/111) | All entries have source & line/page | **VERIFIED** |

### 3.2 Breakdown by Semantic Intent (Positive Examples: 56)
| # | Intent | Count | Example Primary Entity | Representative Source |
|---|---|---|---|---|
| 1 | `definition` | 4 | Celestial bodies, Solar wind, Galaxy, Epicenter | `geography_extracted.txt:36`, `question_extracted.txt:12` |
| 2 | `attribute` | 4 | Stars, P-waves, Saturn, Tropical rainforest | `geography_extracted.txt:38`, `corpus_data.json:p.27` |
| 3 | `cause/effect` | 4 | Solar storms, Subduction, Precipitation, Denudation | `question_extracted.txt:34`, `test_discovery_regression.py:9` |
| 4 | `comparison` | 4 | P-waves vs S-waves, Latitude vs Longitude, Biomes | `corpus_data.json:p.27`, `geography_extracted.txt:658` |
| 5 | `spatial` | 4 | Andromeda Galaxy, Narmada River, Chota Nagpur, Tropic of Cancer | `geography_extracted_2.txt:44`, `geography_extracted.txt:540` |
| 6 | `distribution` | 4 | Global water, Gangetic population, Deciduous forests, Coal/iron | `geography_extracted.txt:1472`, `supplementary_corpus.txt:3` |
| 7 | `classification` | 4 | Rocks (3 types), Planets (inner/outer), Plate margins, Motions | `geography_extracted.txt:1720`, `question_extracted.txt:638` |
| 8 | `quantity` | 4 | Solar system mass (99.86%), Moon distance (384,400 km), Age (13.8B yr) | `geography_extracted_2.txt:95`, `geography_extracted.txt:296` |
| 9 | `sequence` | 4 | Star life cycle, Solar system origin, Rock cycle, Seismic arrival | `question_extracted.txt:75`, `corpus_data.json:p.27` |
| 10 | `condition` | 4 | Solar eclipse, Lunar eclipse, Cloud condensation, Cyclogenesis | `question_extracted.txt:45`, `question_extracted.txt:58` |
| 11 | `exception` | 4 | Venus/Uranus rotation, Moonless planets, Westward rivers, S-wave liquid stop | `geography_extracted.txt:470`, `geography_extracted_2.txt:266` |
| 12 | `process` | 4 | Seafloor spreading, Soil erosion, Convectional rain, Island arc orogeny | `corpus_data.json:p.33`, `geography_extracted.txt:1698` |
| 13 | `part-of` | 4 | Solar corona, Earth concentric layers, Solar system in Orion Arm, Troposphere | `question_extracted.txt:14`, `geography_extracted.txt:1400` |
| 14 | `member-of` | 4 | Ursa Major, Sun (yellow dwarf), Aravalli Range, Jawaharlal Nehru Port | `geography_extracted.txt:98`, `consolidated_grounding.md:Q617` |

### 3.3 Breakdown by Rejection Category (Negative Examples: 55)
| # | Rejection Category | Count | Primary Failure Mechanism | Representative Sample |
|---|---|---|---|---|
| 1 | `mcq_leakage` | 10 | Option tokens `(a)`-`(d)`, solution prefixes `Sol.1.(b)`, answer strings | `(a) Sunspots (b) Solar wind`, `Sol.2.(d) 1, 2, 3, and 4` |
| 2 | `watermark_header` | 9 | Publisher names, ISBNs, chapter titles, shift tags, website URLs | `PARMAR SSC`, `ISBN 81-7450-491-5`, `www.ssccglpinnacle.com` |
| 3 | `syntactic_fragment` | 9 | Dangling conjunctions, cut-off prepositions, hanging adverbial clauses | `The Nile basin is huge and`, `Out of total water resources...` |
| 4 | `broken_reading_order` | 9 | Parallel column collision, duplicated headers, interleaved running text | `Cosmology Big Bang Theory Galaxy Steady State...`, `UniverseGalaxySolar System` |
| 5 | `table_formatting_artifact` | 9 | Markdown pipes, delimiters, craft instructions, DB metadata keys | `\| Topic \| Tier \| Format \|`, `- **PDF-Sequence-Number**: 617` |
| 6 | `anaphoric_unresolved` | 9 | Unresolved pronouns (`They`, `It`) and demonstratives (`These`) | `They are made up of gases.`, `It makes up for about 99.86%...` |

### 3.4 Formal JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GoldenEvaluationDataset",
  "type": "object",
  "required": ["version", "metadata", "examples"],
  "properties": {
    "version": {"type": "string"},
    "name": {"type": "string"},
    "description": {"type": "string"},
    "metadata": {
      "type": "object",
      "required": ["total_examples", "positive_count", "negative_count", "intent_distribution", "negative_distribution"],
      "properties": {
        "total_examples": {"type": "integer"},
        "positive_count": {"type": "integer"},
        "negative_count": {"type": "integer"},
        "intent_distribution": {"type": "object"},
        "negative_distribution": {"type": "object"}
      }
    },
    "examples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "text", "expected_label", "intent", "provenance"],
        "properties": {
          "id": {"type": "string", "pattern": "^(POS|NEG)-[0-9]{3}$"},
          "text": {"type": "string", "minLength": 1},
          "expected_label": {"type": "string", "enum": ["positive", "negative"]},
          "intent": {
            "type": "string",
            "enum": [
              "definition", "attribute", "cause/effect", "comparison",
              "spatial", "distribution", "classification", "quantity",
              "sequence", "condition", "exception", "process",
              "part-of", "member-of", "none"
            ]
          },
          "rejection_category": {
            "type": ["string", "null"],
            "enum": [
              "mcq_leakage", "watermark_header", "syntactic_fragment",
              "broken_reading_order", "table_formatting_artifact",
              "anaphoric_unresolved", null
            ]
          },
          "rejection_reason": {"type": ["string", "null"]},
          "provenance": {
            "type": "object",
            "required": ["source_file", "line_or_page"],
            "properties": {
              "source_file": {"type": "string"},
              "line_or_page": {"type": "string"},
              "raw_context": {"type": "string"}
            }
          },
          "semantic_entities": {
            "type": ["object", "null"],
            "properties": {
              "primary_entity": {"type": "string"},
              "predicate": {"type": "string"},
              "secondary_entities": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          },
          "rationale": {"type": "string"}
        }
      }
    }
  }
}
```

---

## 4. Caveats

1. **OCR Noise in Real Corpus**: Certain PDF extractions in `geography_extracted_2.txt` exhibit severe vertical letter spacing (e.g. `EARTHE A R T H`). Downstream normalizers in M2 must implement horizontal whitespace normalization and letter de-spacing before semantic sentence segmentation.
2. **Coreference Context Horizon**: Anaphoric statements (e.g. `They are made up of gases.`) are rejected in this evaluation dataset when presented as isolated single sentences. However, if the M2 Normalizer implements coreference resolution over preceding sentences, such statements can be rehabilitated into positive knowledge units (e.g. `Stars are made up of gases.`).
3. **No Code Implementation in M1**: In accordance with the explorer archetype rules, this deliverable establishes the benchmark dataset and schema without modifying production extraction engines.

---

## 5. Conclusion & Actionable Recommendations

1. **Dataset Successfully Built & Mirrored**:
   - Primary target file: `data/golden_eval_set.json` (created and populated).
   - Agent working directory mirror: `.agents/teamwork_preview_explorer_m1_1/golden_eval_set.json`.
   - Automated validator: `.agents/teamwork_preview_explorer_m1_1/validate_golden_eval_set.py` passing 100% of assertions.
2. **Immediate Recommendations for Downstream Engineers**:
   - **For M2 (14-Intent Semantic Extractor)**: Abandon single-regex matching in favor of NLP dependency trees (spaCy/stanza) or structured LLM schema prompts. Target the 14 intents with explicit semantic slot filling (`primary_entity`, `predicate`, `secondary_entities`).
   - **For M2 Normalizer**: Implement a pre-extraction cleaning filter that runs before sentence splitting:
     - Strip MCQ option markers (`^\([a-e]\)`, `\b[A-E]\)`)
     - Strip watermarks using regex blacklist (`PARMAR SSC`, `ISBN \d+`, `www\.\S+`)
     - Filter out markdown table delimiters (`\|`, `---`)
     - Detect and stitch broken line wraps ending in prepositions or coordinate conjunctions (`and$`, `in$`, `of$`)
   - **For M3 Benchmark Runner**: Use `data/golden_eval_set.json` to compute Precision, Recall, False Acceptance Rate (FAR), and False Rejection Rate (FRR) across the three competing extraction approaches.

---

## 6. Verification Method

To independently verify this evaluation dataset and its schema compliance, execute the following commands from the workspace root (`c:\Users\harsh\Downloads\tayaari\tayaariapp`):

```powershell
# 1. Run the automated golden dataset test suite
python .agents/teamwork_preview_explorer_m1_1/validate_golden_eval_set.py

# 2. Inspect the dataset counts and integrity via inline Python
python -c "import json; d=json.load(open('data/golden_eval_set.json', encoding='utf-8')); print('Total:', len(d['examples']), 'Positives:', sum(1 for x in d['examples'] if x['expected_label']=='positive'), 'Negatives:', sum(1 for x in d['examples'] if x['expected_label']=='negative'))"
```

**Expected Results**:
- `Ran 4 tests in 0.001s: OK`
- Output: `Total: 111 Positives: 56 Negatives: 55`
- Intent breakdown: Exactly 4 instances for each of the 14 semantic intents.
- Rejection breakdown: 10 MCQ leakage, 9 Watermark, 9 Syntactic fragment, 9 Broken reading order, 9 Table formatting artifact, 9 Anaphoric unresolved.
