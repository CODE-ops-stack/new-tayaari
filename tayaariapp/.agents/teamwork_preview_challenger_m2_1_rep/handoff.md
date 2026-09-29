# Challenger Handoff Report: Adversarial Stress Testing of Semantic Extractor & NoiseFilterGate

**Agent**: `teamwork_preview_challenger_m2_1_rep`  
**Role**: `critic`, `specialist` (EMPIRICAL CHALLENGER)  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_1_rep`  
**Parent Orchestrator**: `a77c38b0-555c-4458-be39-2ed32a7a7e9f`  
**Target Milestone**: M2 (Advanced Semantic Knowledge Representation)  
**Confirmation Verdict**: **REJECT**  
**Overall Risk Assessment**: **CRITICAL**  

---

## Challenge Summary

The Milestone 2 deliverables (`v13_discovery/semantic_extractor.py`, `v13_discovery/normalizer.py`) passed the initial 25 unit tests in `tests/test_v13_semantic_extractor.py` solely because the unit tests and the deterministic extractor (`LinguisticSemanticExtractor`) were co-overfitted to exact verbatim phrases in `data/golden_eval_set.json` (e.g., hardcoding `"are longitudinal compressional waves"`, `"creates the Coriolis force"`, `"exceed 27"`, and `"has the lowest mean density"` directly into regex branches).

Under empirical adversarial challenge testing, the current extraction engine and noise gate exhibit severe systemic failure modes:
1. **Complete Knowledge Drop on Complex Syntax**: Drops sentences with multiple introductory prepositional phrases (including the verbatim prompt assignment sentence) and drops single-clause locative inversions due to an unhandled trailing period in `LOCATIVE_INV_REGEX`.
2. **Entity Inversion & Corrupted Slotting**: Inverts passive definitions (e.g., extracting `"Sahyadri in Maharashtra"` as `primary_entity` and `"are The Western Ghats"` as `predicate`), and corrupts proper nouns by stripping characters from words starting with 'A' (e.g., `"Along the Malabar Coast..."` yields entity `"long the Malabar Coast..."`).
3. **Severe Under-generalization on Natural Variations**: On 30 representative educational sentences across the 14 intents, the extractor failed or misclassified **20 out of 30 (66.7%)**.
4. **NoiseFilterGate Leakage**: Borderline MCQ labels such as `(i)` and `[A]` bypass `NoiseFilterGate` and leak directly into `KnowledgeNode.primary_entity`.
5. **False Rejection of Valid Knowledge**: Falsely rejects valid educational facts starting with demonstratives (`"These landforms..."`, `"Those plateaus..."`) as `anaphoric_unresolved`, and falsely rejects concise 4-word facts (`"Basalt is volcanic rock."`) as `syntactic_fragment`.

Because these flaws directly corrupt the primary entities and predicates fed into Milestone 4 (Question & Distractor Synthesizer), Milestone 2 cannot be approved in its current form.

---

## 1. Observation

### 1.1 Verbatim Empirical Test Suite Execution (`tests/test_v13_adversarial_challenge.py`)

A dedicated 9-scenario adversarial test suite was authored and executed:
- **Command**: `python -m unittest -v tests/test_v13_adversarial_challenge.py`
- **Result**: `FAILED (failures=9)` in `0.015s`

Verbatim failure traces:

1. **Multi-Prepositional Sentence Dropped (Dispatched Input)**:
   - Input: `"In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."`
   - Failure: `AssertionError: 0 not greater than or equal to 1 : Extractor completely dropped multi-prepositional sentence: 'In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding.'`
   - Code Inspection (`v13_discovery/semantic_extractor.py:326-328`):
     ```python
     INTRO_CLAUSE_REGEX = re.compile(
         r'^(?P<intro>(?:In|According to|During|Throughout|Across|Under|With|Between|At|From|By|On)\s+[^,]+),\s*(?P<main>[A-Z].*)$'
     )
     ```
     Because the second introductory clause begins with lowercase `"during"`, `(?P<main>[A-Z].*)` fails to match. The sentence is passed unstripped to `cls.PATTERNS`, where `(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)` in the cause/effect pattern fails because commas `,` are excluded from the entity character set. Extracted nodes: `0`.

2. **Locative Inversion Trailing Period Bug**:
   - Input: `"Under the continental crust lies the upper mantle."`
   - Failure: `AssertionError: 0 not greater than or equal to 1 : Extractor failed on single-clause locative inversion with period: 'Under the continental crust lies the upper mantle.'`
   - Code Inspection (`v13_discovery/semantic_extractor.py:322-324`):
     ```python
     LOCATIVE_INV_REGEX = re.compile(
         r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*))?$',
         re.IGNORECASE
     )
     ```
     The character class for `entity` does not include `.`. When there is no secondary comma clause, the trailing period prevents matching the end-of-string anchor `$`. Extracted nodes: `0`.

3. **Passive Definition Entity Inversion**:
   - Input: `"The Western Ghats are known as Sahyadri in Maharashtra."`
   - Output:
     - `primary_entity`: `'Sahyadri in Maharashtra'`
     - `predicate`: `'are The Western Ghats'`
   - Failure: `AssertionError: 'western ghats' not found in 'sahyadri in maharashtra' : Subject inverted: primary_entity was slotted as 'Sahyadri in Maharashtra'`
   - Code Inspection (`v13_discovery/semantic_extractor.py:318-320`, `454-468`):
     ```python
     PASSIVE_DEF_REGEX = re.compile(
         r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\-]+)\.?$',
         re.IGNORECASE
     )
     ```
     The implementation hardcoded `primary_entity = term` and `predicate = f"are {desc}"`, assuming sentences always follow `"Sun and moon are called celestial bodies"`. For standard descriptive assertions (`"X is known as Y"`), it inverts the primary entity and predicate.

4. **Corrupted Prefix Stripping on 'Along'**:
   - Input: `"Along the Malabar Coast, during the southwest monsoon, heavy precipitation occurs regularly."`
   - Output:
     - `primary_entity`: `'long the Malabar Coast, during the southwest monsoon, heavy precipitation'`
   - Failure: `AssertionError: True is not false : Entity corrupted by leading 'A' strip: 'long the Malabar Coast, during the southwest monsoon, heavy precipitation'`
   - Code Inspection (`v13_discovery/semantic_extractor.py:538-542`):
     ```python
     match_decl = re.match(
         r'^(?:The|An|A)?\s*([A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(is|are|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises)\s+(.*)',
         clean_text,
         re.IGNORECASE
     )
     ```
     Because `(?:The|An|A)?` lacks a word boundary `\b`, it strips the capital letter `'A'` from `"Along"`, leaving `"long the Malabar Coast..."` as the corrupted primary entity.

5. **Entity Recovery Drop on Common Verbs**:
   - Input: `"The Deccan Traps were formed through massive basaltic fissure eruptions."`
   - Failure: Dropped (`0 nodes extracted`).
   - Code Inspection (`v13_discovery/semantic_extractor.py:362`):
     Regex only allows `was formed through the tectonic process`. Plural `"were formed"` or general non-tectonic processes fail to match.

6. **MCQ Noise Marker Leakage into Primary Entity**:
   - Inputs:
     - `"(i) The Deccan Traps are formed by volcanic activity."` -> `primary_entity`: `"(i) The Deccan Traps"`
     - `"[A] Barren Island is India only active volcano."` -> `primary_entity`: `"[A] Barren Island"`
     - `"1) The Western Ghats cause orographic rainfall."`
   - Failure: `NoiseFilterGate.audit()` returned `None` on all three items, allowing exam question markers to penetrate the pipeline and corrupt the extracted entity name.

7. **Figure Caption Watermark Bypass**:
   - Input: `"Figure 3.2 Diagram of the Solar System"`
   - Failure: `NoiseFilterGate.audit()` returned `None`.
   - Code Inspection (`v13_discovery/semantic_extractor.py:249`):
     `Figure\s+\d+\.\d+\s*:` requires a trailing colon `:`. Captions without colons pass through undetected.

8. **False Rejection of Valid Demonstrative Statements**:
   - Inputs:
     - `"These landforms are primarily shaped by glacial erosion across high altitudes."`
     - `"These rivers originate in the glaciers of the Trans-Himalayan region."`
     - `"Those plateaus situated north of the Tropic of Cancer experience extreme temperature variations."`
     - `"Those rocks formed by cooling magma are categorized as igneous rocks."`
   - Failure: `NoiseFilterGate.audit()` falsely flagged all 4 items as `anaphoric_unresolved`.
   - Code Inspection (`v13_discovery/semantic_extractor.py:276`):
     `r'^\s*(?:They|These|Those|He|She|It)\s+[a-z]+'` treats demonstrative determiners followed by common nouns (`These landforms`, `Those rocks`) as dangling anaphoric pronouns.

9. **False Rejection of Concise 4-Word Educational Facts**:
   - Inputs:
     - `"Basalt is volcanic rock."`
     - `"Lignite is brown coal."`
     - `"Marble is metamorphic limestone."`
     - `"Quartz is silicon dioxide."`
     - `"Hematite is iron ore."`
   - Failure: `NoiseFilterGate.audit()` falsely flagged all 5 items as `syntactic_fragment`.
   - Code Inspection (`v13_discovery/semantic_extractor.py:307`):
     `if len(words) < 5: return "syntactic_fragment"` discards concise core definitions.

---

### 1.2 Quantitative Generalization Stress Test (30 Natural Educational Sentences)

To evaluate whether `LinguisticSemanticExtractor` generalizes beyond the 14 fixtures in `test_v13_semantic_extractor.py`, 30 standard textbook statements spanning all 14 intents were tested:
- **Correct Intent Slotted**: 10 / 30 (**33.3%**)
- **Failed / Misclassified / Dropped**: 20 / 30 (**66.7%**)
  - Dropped to 0 nodes (10 items): `"Isthmus denotes..."`, `"Regur soil possesses..."`, `"Heavy monsoonal downpours trigger..."`, `"Rapid urbanization leads to..."`, `"Unlike tropical cyclones..."`, `"Basaltic lava has lower viscosity..."`, `"The Tropic of Cancer passes through..."`, `"The Palk Strait separates..."`, `"Mount Everest reaches an altitude of..."`.
  - Misclassified as generic `definition` (7 items): Laterite soil attributes, Western Ghats comparison, Thar Desert bounds, Mangrove distribution, Himalayan rivers classification, Indian coastline quantity.
  - Corrupted entity extracted:
    - `"All major peninsular rivers drain into the Bay of Bengal, except the Narmada and Tapi."` -> `primary_entity`: `'All'`
    - `"The ozone layer is a vital part of the stratosphere."` -> `primary_entity`: `'ozone layer is a vital'`

---

## 2. Logic Chain

1. **Premise 1 (R2 Interface Contract & Requirement)**:
   `ORIGINAL_REQUEST.md §R2` mandates:
   *"Design an extraction architecture that maps source blocks to explicit semantic intents... Do not rely solely on simple Subject-Verb-Object (SVO) regex patterns."*
   The downstream `CandidateQuestion` generator (M4) directly consumes `KnowledgeNode.primary_entity` and `KnowledgeNode.predicate` to synthesize natural stems and distractors.

2. **Observation 2.1**:
   In `v13_discovery/semantic_extractor.py`, `LinguisticSemanticExtractor` relies on brittle, overfitted regexes with hardcoded phrases (e.g. `creates the Coriolis force`, `exceed 27`, `longitudinal compressional waves`, `lowest mean density`).
3. **Observation 2.2**:
   When tested on natural syntactic variations:
   - `LOCATIVE_INV_REGEX` crashes on standard sentences ending in a period.
   - `PASSIVE_DEF_REGEX` inverts subject and predicate on `"X is known as Y"`.
   - `INTRO_CLAUSE_REGEX` fails on multi-prepositional sentences, causing `SemanticExtractor` to drop valid knowledge completely.
   - Word boundary omission in `match_decl` strips leading `'A'` from `"Along"`, producing corrupted entity names.
4. **Observation 2.3**:
   `NoiseFilterGate` operates with blunt heuristics:
   - It permits Roman numerals `(i)` and brackets `[A]` to pass through, leaking option markers into entity names.
   - It falsely rejects valid demonstrative facts (`"These landforms..."`) and concise 4-word facts (`"Basalt is volcanic rock."`), severely damaging pipeline recall.

5. **Inference**:
   If these defects are not corrected in Milestone 2:
   - Milestone 3 comparative benchmarks on 100+ real source units will report artificial >60% drop rates.
   - Milestone 4 question generation will synthesize absurd questions (e.g., questions about `'Sahyadri in Maharashtra'` being `'The Western Ghats'`, or questions targeting corrupted entity `'long the Malabar Coast...'`).
   - Milestone 5 auditing will systematically reject these flawed questions, forcing a costly systemic loopback.

6. **Conclusion**:
   Milestone 2 must be **REJECTED** until these parsing and filtering defects are resolved.

---

## 3. Challenges & Concrete Mitigations

### Challenge 1 [Critical]: Inverted Primary Entity and Predicate in Passive Definitions
- **Assumption Challenged**: Passive definitions always place the defined term after `"called"` / `"known as"` and the definition before it.
- **Attack Scenario**: `"The Western Ghats are known as Sahyadri in Maharashtra."`
- **Blast Radius**: Distorts core subject ontology; questions generated will ask about the alias rather than the primary geographical feature.
- **Mitigation**: In `PASSIVE_DEF_REGEX`, inspect whether `desc` is a capitalized proper noun phrase. If `desc` is a named entity and `term` is an alias/epithet, keep `desc` as `primary_entity` and slot `term` into `predicate` or `secondary_entities`.

### Challenge 2 [Critical]: Failure on Multi-Clause Introductory Prepositional Phrases
- **Assumption Challenged**: Introductory clauses are single phrases followed by a capitalized main clause.
- **Attack Scenario**: `"In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."`
- **Blast Radius**: All multi-condition educational sentences from NCERT geography are dropped (0 recall).
- **Mitigation**: Update `INTRO_CLAUSE_REGEX` to greedily peel off chained introductory adverbial/prepositional clauses:
  ```python
  INTRO_CLAUSE_REGEX = re.compile(
      r'^(?P<intro>(?:(?:In|According to|During|Throughout|Across|Under|With|Between|At|From|By|On|Along)\s+[^,]+,\s*)+)(?P<main>[A-Za-z].*)$'
  )
  ```
  Store all peeled introductory phrases in `node.conditions`.

### Challenge 3 [High]: Locative Inversion Trailing Period Regex Bug
- **Assumption Challenged**: Inverted sentences always have trailing subordinate clauses after a comma.
- **Attack Scenario**: `"Under the continental crust lies the upper mantle."`
- **Blast Radius**: Drops simple locative inversion facts ending with standard periods.
- **Mitigation**: Update `LOCATIVE_INV_REGEX` to accept optional trailing punctuation before `$`:
  ```python
  r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*?))?\.?$'
  ```

### Challenge 4 [High]: Leading Letter Stripping on 'Along'
- **Assumption Challenged**: Stripping leading determiners/articles with `^(?:The|An|A)?` is safe.
- **Attack Scenario**: `"Along the Malabar Coast..."` -> Entity: `'long the Malabar Coast...'`
- **Blast Radius**: Corrupts entity tokens in the knowledge graph.
- **Mitigation**: Enforce word boundaries: `r'^(?:The\b|An\b|A\b)?\s*'`

### Challenge 5 [High]: False Rejection of Demonstratives and Short Facts in NoiseFilterGate
- **Assumption Challenged**: Any sentence starting with `"These"` or `"Those"` has an unresolved pronoun; any sentence with `< 5` words is a fragment.
- **Attack Scenario**:
  - `"These landforms are primarily shaped by glacial erosion across high altitudes."`
  - `"Basalt is volcanic rock."`
- **Blast Radius**: Unnecessary loss of high-yield factual knowledge (violates R1/R2 recall mandate).
- **Mitigation**:
  - In `anaphoric_unresolved`, only flag `"These"` / `"Those"` when followed immediately by auxiliary verbs (`are`, `were`, `have`, `do`), not when followed by common or proper nouns.
  - In word count check, do not reject sentences `< 5` words if they match a complete copular statement: `^[A-Z][a-z]+\s+(?:is|are)\s+(?:an?\s+)?\w+\s+\w+\.$`.

### Challenge 6 [Medium]: MCQ Option Leakage into Entity Names
- **Assumption Challenged**: MCQ options are only formatted as `(a)` to `(e)`.
- **Attack Scenario**: `"(i) The Deccan Traps are formed by volcanic activity."`, `"[A] Barren Island..."`
- **Blast Radius**: Pollution of knowledge units with exam letter artifacts.
- **Mitigation**: Add Roman numeral options and bracketed options to `NoiseFilterGate.NOISE_PATTERNS["mcq_leakage"]`:
  ```python
  r'^\s*\(?[ivxlcdmIVXLCDM]+\)[\s\.\)]',
  r'^\s*\[[A-Ea-e]\][\s\.\)]',
  r'^\s*\d+\)[\s\.]',
  ```

---

## 4. Caveats

1. **Evaluation of DocumentNormalizer**:
   `v13_discovery/normalizer.py` (`TableParser`, `LayoutDesegmenter`, `WatermarkOcrCleaner`) performed reliably on standard Markdown tables and column stitching tests. The primary defects reside in `v13_discovery/semantic_extractor.py` (`LinguisticSemanticExtractor` and `NoiseFilterGate`).
2. **LLM Fallback Mode**:
   `GeminiStructuredExtractor` is implemented with proper response schema and rate limiting, but is disabled by default (`ENABLE_GEMINI_FALLBACK=false`). Because offline/CI pipelines and fast local generation depend on the deterministic linguistic engine, the flaws in `LinguisticSemanticExtractor` and `NoiseFilterGate` are critical and blocking.

---

## 5. Conclusion

**Confirmation Verdict**: **REJECT**

The Milestone 2 implementation cannot be approved because:
1. It fails on the exact test challenge assigned in dispatch (`"In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."`).
2. It inverts subjects and predicates in standard passive definitions.
3. It corrupts entities via naive article stripping (`"Along"` -> `"long"`).
4. It drops simple locative sentences due to regex period termination bugs.
5. It achieves only 33.3% accuracy across 30 natural educational variations outside the training fixtures.
6. Its noise gate leaks Roman/bracketed MCQ options and falsely rejects valid demonstrative and concise facts.

The worker must address Challenges 1–6 before Milestone 2 can be verified and approved.

---

## 6. Verification Method

To independently reproduce all 9 failure modes:

1. **Run the Adversarial Challenge Test Suite**:
   ```powershell
   python -m unittest -v tests/test_v13_adversarial_challenge.py
   ```
   *Expected result*: `FAILED (failures=9)`

2. **Verify Multi-Prepositional Sentence Dropping**:
   ```powershell
   python -c "from v13_discovery.semantic_extractor import SemanticExtractor; ext = SemanticExtractor(); print('Nodes extracted:', len(ext.extract('In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding.')))"
   ```
   *Expected result*: `Nodes extracted: 0` (demonstrates failure to extract assigned sentence).

3. **Verify Passive Subject Inversion**:
   ```powershell
   python -c "from v13_discovery.semantic_extractor import SemanticExtractor; ext = SemanticExtractor(); node = ext.extract('The Western Ghats are known as Sahyadri in Maharashtra.')[0]; print('Entity:', node.primary_entity); print('Predicate:', node.predicate)"
   ```
   *Expected result*:
   `Entity: Sahyadri in Maharashtra`
   `Predicate: are The Western Ghats`

4. **Verify Demonstrative False Rejection in NoiseFilterGate**:
   ```powershell
   python -c "from v13_discovery.semantic_extractor import NoiseFilterGate; print('Rejection:', NoiseFilterGate.audit('These landforms are primarily shaped by glacial erosion across high altitudes.'))"
   ```
   *Expected result*: `Rejection: anaphoric_unresolved`
