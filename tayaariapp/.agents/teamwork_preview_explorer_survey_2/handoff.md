# Corpus & Knowledge Profiling Handoff Report

**Agent**: `teamwork_preview_explorer_survey_2`  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_survey_2`  
**Target Milestone**: V13 Content Discovery & Knowledge Representation Architecture  
**Date**: 2026-09-03  

---

## 1. Observation

### 1.1 Complete Educational Corpus Inventory
An exhaustive scan of the repository (`c:\Users\harsh\Downloads\tayaari` and `c:\Users\harsh\Downloads\tayaari\tayaariapp`) identified three tiers of educational source material totaling **930,902 words**:

#### Tier A: PDF Textbooks, Compendiums & Reference Notes (26 Files, 2,115 Pages, 723,381 Words)
| Category / Source Type | Files | Pages | Words (PyMuPDF) | Extractability Status | Key Titles |
|---|---|---|---|---|---|
| **NCERT Textbooks** | 9 | 978 | 486,974 | 9/9 Fully Extractable | `Fundamental of Physical Geography (Class XI)`, `Fundamentals of Human Geography (Class XII)`, `India People and Economy (Class XII)`, `India Physical Environment (Class XI)`, `NCERT-Class-10-Geography`, `NCERT-Class-9-Geography`, `Copy of our environmemnt class 7`, `social science class 8`, `Practical Work Part 1 & 2` |
| **Exam PYQ Compendiums** | 3 | 285 | 109,593 | 3/3 Fully Extractable | `question.pdf` (67,245 words, 84 pp.), `VisionIAS Research & Analysis Geography 10-Yr PYQ` (33,062 words, 148 pp.), `geography_questions_in_UPSC_Prelims` (9,286 words, 53 pp.) |
| **Coaching & Reference Notes** | 13 | 852 | 126,814 | 7 Extractable, 6 Image/OCR Scanned | Extractable: `Environment (Apr-Nov 2025)` (37,018 words), `newGeography.pdf` (27,390 words), `Geogrophy.pdf` (16,411 words), `GEOGRAPHY 4.0 ENGLISH` (10,136 words), `Earth's Magnetic Field PMF IAS` (1,311 words), `Geomagnetism LotusArise` (1,574 words). Scanned/Image: `ccab2-geography.pdf` (206 pp.), `fatman Geography Parts 1-5` (93 pp.) |
| **Atlases & Cartography** | 1 | 0 (index only) | 0 | Unextractable image scan | `oxford-student-atlas-35-edition...pdf` (Corrupted/image scan; indexed separately in `oxford_atlas_spatial_index.json`) |

#### Tier B: Synthesized Grounding & Extracted Text Material (14 Files, 43,640 Lines, 207,521 Words)
1. `source-material/consolidated_grounding.md` (556.8 KB, 18,428 lines, 80,787 words): Complete curriculum grounding file containing 925+ structured exam questions with answers, topic mappings, tier, and format metadata.
2. `source-material/consolidated_grounding_merged.md` (104.3 KB, 3,964 lines, 16,465 words): Secondary merged topic grounding map.
3. `source-material/question_extracted.txt` (573.7 KB, 15,329 lines, 80,518 words): Pinnacle Geography PYQ compendium with full questions, options (a–d), answers, and detailed pedagogical explanations for hundreds of SSC Stenographer/CGL items.
4. `source-material/geography_extracted.txt` (91.3 KB, 2,625 lines, 16,086 words): NCERT Class VI Geography ("The Earth Our Habitat").
5. `source-material/geography_extracted_2.txt` (60.5 KB, 2,921 lines, 10,041 words): Parmar SSC notes on Cosmology, Solar System, and Physical Geography.
6. `source-material/supplementary_corpus.txt` (0.8 KB, 5 lines, 108 words): Short supplementary prose excerpts.
7. **Syllabi & Specification Profiles** (8 files, 22.5 KB, 3,496 words): `geography-syllabus.md` (Drishti IAS full syllabus), `geography-syllabus-gs.md`, `pyq-analysis-prelims.md`, `examiner-pattern-guide.md`, `file-categories.md`, `exam-complexity-profiles.md`, `design-system.md`, `exam_question_design_profiles.md`.

#### Tier C: Structured JSON Knowledge Registries & Question Banks (12 Files, ~1,100 Structured Items)
1. `source-material/extracted_ssc_qs.json` (285.2 KB): **910 verified questions** with schema `{questionText, options: {a, b, c, d}, correctAnswer}`.
2. `source_registry.json` (29.6 KB): 65 registered sources across UPSC and SSC with readability status, provenance, and priorities.
3. `syllabus_knowledge_map.json` (9.9 KB): Comprehensive curriculum ontology mapping UPSC/SSC modules (`GEOMORPHOLOGY`, `CLIMATOLOGY`, `OCEANOGRAPHY`, `INDIAN_GEOGRAPHY`, `COSMOLOGY`) down to subtopics and concepts.
4. `derived_opportunities.json` (55.6 KB): 30 synthesized candidate question opportunities.
5. `staging_batch_1.json` (88.5 KB): 50 candidate questions.
6. `staging_batch_2.json` (32.6 KB): 29 candidate questions.
7. `staging_production_v1.json` (21.5 KB): 21 candidate questions.
8. `corpus_data.json` (18.9 KB): 17 questions with detailed metadata (UTF-8 BOM encoded).
9. `theory_nodes.json` (4.4 KB) & `generic_theory_nodes.json` (7.8 KB): 11 structured theory nodes (UTF-8 BOM encoded).
10. `oxford_atlas_spatial_index.json` (3.5 KB) & `pyq_index.json` (1.1 KB): Spatial features and exam index.

---

### 1.2 Subject & Module Distribution
Across the 930,902 words in the corpus, the subject distribution is mapped as follows:
- **General & Foundational Geography** (NCERT 6–10, Coaching summaries): 396,163 words (42.6%)
- **Physical Geography & Geophysics** (Geomorphology, Climatology, Oceanography, Geomagnetism): 56,063 words (6.0%)
- **Human & Economic Geography** (Demography, Agriculture, Transport, Ports, Minerals): 73,765 words (7.9%)
- **Environment & Ecology** (Ecosystems, Protected Areas, Climate Change 2025): 66,724 words (7.2%)
- **Geography Exam PYQs & Solutions** (UPSC Prelims, SSC Stenographer, CGL): 109,593 words (11.8%)
- **General Studies & Social Science** (NCERT 8, Interdisciplinary): 21,073 words (2.3%)
- **Grounding Synthesis & Syllabi** (`consolidated_grounding.md`, syllabus maps): 207,521 words (22.3%)

---

### 1.3 Verbatim Structural Challenges
Direct examination of corpus text files revealed severe real-world structural challenges:

#### 1. Watermark & Running Header Noise
In `source-material/question_extracted.txt`:
- **Line 185, Line 380, Line 564**:
  ```
  www.ssccglpinnacle.com                                                 Download Pinnacle Exam Preparation App    Pinnacle  Geography
  ```
- **Consequence**: In `v12_discovery_pipeline.py` (line 59), developers added an ad-hoc blacklist (`BAD_ENTITIES = {..., "app", "download", "pinnacle"}`) instead of proper structural layout filtering.

#### 2. Multi-Column Reading Order Corruption
In `source-material/geography_extracted_2.txt` (lines 3–17):
- **Raw File Content**:
  ```
  Cosmology
  Big Bang
  Theory
  Galaxy
  Steady State
  Theory
  Study of Universe.
  Given by George
  Lemaitre in 1927 and
  published in 1931.
  It was an explosion of
  concentrated matter in
  the universe that
  occurred 13.8 billion
  years ago.
  ```
- **Consequence**: Two-column PDF tables were extracted vertically down column boundaries. Entities like `"Big Bang Theory"` and `"Steady State Theory"` are broken across multiple lines, and the sentence `"Given by George Lemaitre in 1927 and published in 1931"` has no subject.

#### 3. Tables Blindly Discarded
In `source-material/consolidated_grounding.md`:
- **Lines 616, 1653, 3353, 6923, 9726**:
  ```markdown
  - **Format Type**: Direct Fact | **Tier**: Basic | **Exam-Relevance**: General-Competitive | **Source**: Real-PYQ | **Specific-Exam**: SSC-Stenographer
  ```
- **Consequence**: In `v12_discovery_pipeline.py` (lines 40–44):
  ```python
  if "|" in line or line.startswith("http") or line.startswith("www"):
      blocks.append({"sourceId": fn, "type": "TABLE_OR_META", "text": line})
  ```
  And in `KnowledgeExtractor` (lines 66–68):
  ```python
  if block["type"] != "PROSE":
      rejected.append({"sentence": block["text"][:50], "reason": f"Block type is {block['type']}"})
      continue
  ```
  **100% of tabular facts, metadata, and structured pairs were discarded.**

#### 4. Multi-Word Complex Entities Truncated or Misparsed
In `source-material/question_extracted.txt` (lines 10249–10250):
- **Raw File Content**:
  ```
  (d) Jawaharlal Nehru Port
  Sol.617.(d) Jawaharlal Nehru Port
  ```
- In `docs/v12_discovery_report.json` (lines 14–20):
  The pipeline matched:
  `"The average density of oceanic crust"` as `subj_x`, and `"continental crust"` as `subj_y`.
- In `docs/v12_discovery_report.json` (line 44):
  The pipeline matched:
  `"The example of open channel flow"` as a single concept entity, generating the absurd question:
  `"Which of the following best describes the geographic concept of 'The example of open channel flow'?"`

#### 5. Complex Sentences & Non-SVO Relational Forms
In `source-material/geography_extracted.txt` (NCERT Class 6):
- **Line 28**: `"You can see the full moon only once in about a month’s time. It is Full moon night or Poornima."` (Temporal frequency and nomenclature).
- **Line 31**: `"On this day, you can watch the night sky best, provided it is a clear night."` (Conditionality: `provided it is...`).
- **Line 37**: `"The sun, the moon and all those objects shining in the night sky are called celestial bodies."` (Passive definition: `are called`).
- **Line 38–41**: `"Some celestial bodies are very big and hot. They are made up of gases. They have their own heat and light, which they emit in large amounts. These celestial bodies are called stars. The sun is a star."` (Compositional attributes, anaphora with "They", taxonomic membership: "The sun is a star").

---

### 1.4 Empirical Simulation of V12 SVO Regex Recall
We executed the exact V12 SVO regex extractor against **46,121 candidate sentences** extracted from the real corpus (`consolidated_grounding.md`, `geography_extracted.txt`, `geography_extracted_2.txt`, and `question_extracted.txt`).

#### Quantitative Results
- **Sentences Evaluated**: 46,121
- **SVO Matched**: 21
- **SVO Rejected**: 46,100
- **Extraction Recall**: **0.045% (~0.05%)**
- **Rejection Rate**: **99.95%**

#### Rejection Cause Breakdown
1. **Failed Strict SVO Regex Syntax**: 23,984 sentences (52.0%)
2. **Length Out of Bounds (<20 or >300 chars)**: 18,820 sentences (40.8%) — triggered by OCR line fragmentation and multi-clause compound sentences.
3. **MCQ Option Marker Artifact Detected**: 3,296 sentences (7.1%) — triggered by `(a)`, `(b)`, `A)` in text.

#### Pattern Matches of the 21 Accepted Sentences
- `SPATIAL` (`X is located in / borders / lies in Y`): 12
- `DEFINITION` (`X is known as / refers to / comprises Y`): 8
- `COMPARISON` (`X is Y while Z is W`): 1
- `CAUSE_EFFECT` (`X causes / leads to Y`): 0
- `CAUSE_EFFECT_INVERTED` (`X is due to Y`): 0

#### Quantified Lost Knowledge Types
Among the 23,984 sentences rejected due to regex mismatch, targeted semantic scanning proved that hundreds of essential educational facts were discarded:
- **Process & Sequence** (`formed by`, `cycle`, `step`, `gradually`, `transforms into`, `cooling and solidification`): **1,250 lost units**
- **Quantitative & Numerical Relations** (percentages, km², densities, latitudes, depths): **174 lost units**
- **Conditionality** (`if`, `when`, `provided that`, `under high pressure`, `unless`): **155 lost units**
- **Cause & Effect (Flexible syntax)** (`as a result of`, `giving rise to`, `driven by`, `owing to`): **82 lost units**
- **Classification & Taxonomy** (`classified into`, `types of`, `divided into`): **48 lost units**
- **Attribute & Composition** (`characterized by`, `composed of`, `rich in`): **32 lost units**
- **Flexible Comparison** (`in contrast`, `unlike`, `differs from`, `higher than`): **23 lost units**
- **Flexible Spatial / Topological Relations** (`flanked by`, `stretches from`, `draining into`): **7 lost units**

#### Catastrophic Distractor Cross-Polling
In `v12_discovery_pipeline.py` (lines 167–200), distractors were chosen by random choice from global predicate pools. Because V12 ignored semantic category boundaries, generated questions in `docs/v12_discovery_report.json` contained nonsensical options:
- **Stem**: `"Which of the following statements accurately compares The average density of oceanic crust and continental crust?"`
- **Generated Distractor**: `"The average density of oceanic crust has the highest share of out-migrants, whereas continental crust has an average of 2.7 g/cm 3."` (Oceanic crust paired with human demographic out-migration).
- **Generated Distractor**: `"Which of the following best describes the geographic concept of 'The example of open channel flow'?"` -> `"It includes immense reserves of metallic minerals."`

---

## 2. Logic Chain

1. **Premise 1 (Corpus Breadth)**: The workspace contains over 930,900 words across 26 PDFs, 14 Markdown/Text grounding files, and 12 JSON assets, covering NCERT 6–12, UPSC 10-year trend analyses, and 910+ verified SSC questions.
2. **Premise 2 (Pipeline Tunnel Vision)**: The V12 discovery pipeline (`v12_discovery_pipeline.py`, line 311) only globbed `source-material/*.txt` (5 files, 107,000 words), completely bypassing all 26 PDFs, the 556 KB `consolidated_grounding.md`, and `extracted_ssc_qs.json`.
3. **Premise 3 (Parser Self-Blindness)**: In `SourceParser` (lines 29–48), any line containing `Q.` or `(a)` was skipped, any line containing `|` was flagged as `TABLE_OR_META`, and in `KnowledgeExtractor` all non-PROSE was discarded. This threw away all 925+ structured question-answer pairs and all tabular comparisons.
4. **Premise 4 (Regex Inflexibility)**: The 5 hardcoded regex patterns only match if a sentence strictly begins with an isolated capitalized subject followed immediately by a specific auxiliary verb. Real educational prose uses passive voice, introductory prepositional phrases ("In the northern hemisphere..."), conditional clauses ("When magma cools slowly..."), and compound multi-word entities.
5. **Premise 5 (Empirical Failure)**: In testing against 46,121 candidate sentences, the V12 SVO regex achieved a recall of only **0.045%** (21 matches). Over **1,250 processes**, **174 quantitative facts**, **155 conditional rules**, and **82 causal mechanisms** were lost.
6. **Premise 6 (Distractor Invalidity)**: Global pooling of predicates without domain ontology verification resulted in cross-domain pollution (ocean crust paired with human migration).
7. **Conclusion**: The V12 discovery pipeline is architecturally bankrupt on both ends:
   - **Ingestion Failure**: Rejects 99.95% of legitimate educational knowledge.
   - **Generation Failure**: Produces ungrammatical, formulaic, and semantically absurd distractors due to lack of an ontological category constraint.

---

## 3. Caveats

1. **Scanned PDFs**: Six PDFs (`fatman Geography 2nd Edition_Part1` through `Part5`, and `ccab2-geography.pdf`) are image-based scans and do not contain embedded digital text streams. Ingesting their content requires an external OCR pre-processing step (via `tesseract` or vision-capable LLMs). However, digital replacements and text compendiums (`question_extracted.txt`, `consolidated_grounding.md`) already cover much of this material.
2. **Corrupted Atlas Archive**: `oxford-student-atlas-35-edition-freeupscmaterials.org__compressed.pdf` is corrupted and contains 0 extractable pages. Spatial questions must rely on `oxford_atlas_spatial_index.json` and NCERT cartography chapters.
3. **UTF-8 BOM in JSON Files**: `corpus_data.json`, `theory_nodes.json`, and `generic_theory_nodes.json` contain UTF-8 Byte Order Marks (`\xef\xbb\xbf`). Any Python pipeline reading them must use `encoding="utf-8-sig"` to prevent `json.decoder.JSONDecodeError`.

---

## 4. Conclusion

1. **Sufficient High-Quality Corpus Exists**: The repository does not suffer from a lack of source material. It contains **930,902 words** of rich educational text, 9 NCERT textbooks, 910 solved exam questions in `extracted_ssc_qs.json`, and 925 mapped questions in `consolidated_grounding.md`.
2. **SVO Regex Must Be Completely Abandoned**: A regex-only extraction approach is demonstrably incapable of educational question discovery. Its 0.05% recall discards processes, classifications, conditions, and causal loops, while creating severe false-positive entity artifacts ("The example of open channel flow").
3. **V13 Architecture Requirements**:
   - **Semantic Parser**: Replace regex with an NLP dependency parser / local LLM semantic parser capable of extracting the 14 explicit semantic intents specified in R2 (`definition`, `attribute`, `cause/effect`, `comparison`, `spatial`, `distribution`, `classification`, `quantity`, `sequence`, `condition`, `exception`, `process`, `part-of`, `member-of`).
   - **Ontology-Constrained Distractor Engine**: Distractor pooling must be restricted to items sharing the exact ontological category (e.g., if target is an `Oceanic Trench`, distractors must be `Submarine Ridges` or `Abyssal Plains`, never `Demographic Migration Rates`).
   - **Provenance Chain**: Every generated item must maintain unbreakable lineage:
     $$\text{Question} \rightarrow \text{Intent} \rightarrow \text{Knowledge Unit} \rightarrow \text{Evidence Excerpt} \rightarrow \text{Source File} \rightarrow \text{Line/Page}$$

---

## 5. Verification Method

To independently verify all findings in this report, run the following verification commands from `c:\Users\harsh\Downloads\tayaari\tayaariapp`:

### 1. Verify Deep Corpus Metrics and Word Counts
```powershell
python .agents/teamwork_preview_explorer_survey_2/corpus_profiler_deep.py
```
**Expected Output**:
- Total PDFs: 26 (2,115 pages, 723,381 words)
- Total Text/MD files: 14 (207,521 words)
- Grand Total Words: 930,902
- SVO Evaluated: 46,121, Matched: 21 (0.05%), Rejected: 46,100

### 2. Verify Exact Structural Challenges & Evidence Line Numbers
```powershell
python .agents/teamwork_preview_explorer_survey_2/extract_evidence.py
```
**Expected Output**:
- Watermark noise at lines 185, 380, 564 of `question_extracted.txt`.
- Multi-column wraps at lines 3–17 of `geography_extracted_2.txt`.
- Markdown table rows at lines 616, 1653, 3353 of `consolidated_grounding.md`.
- Non-SVO educational sentences at lines 28, 31, 37, 39, 41 of `geography_extracted.txt`.

### 3. Verify V12 Pipeline Self-Audit Data
Inspect lines 1–12 of `docs/v12_discovery_report.json`:
```json
{
  "SOURCES PROCESSED": 5,
  "SOURCE UNITS": 1204,
  "VALID NODES": 23,
  "REJECTED NODES": 3785,
  "ACCEPTED": 17
}
```

### 4. Verify Project Unit Tests
Run standard project test command:
```powershell
.\gradlew.bat clean testDebugUnitTest
```
*(Android unit tests pass independently of the Python discovery scripts).*
