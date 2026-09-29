# Milestone 2 Iteration 2 Explorer Handoff Report: Syntactic Inversions, Multi-Clause Stripping, and Adversarial Hardening

**Agent**: `teamwork_preview_explorer_m2_it2_2`  
**Role**: `explorer`, `synthesizer`  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_2`  
**Parent Orchestrator**: `a77c38b0-555c-4458-be39-2ed32a7a7e9f`  
**Target Milestone**: M2 Iteration 2  
**Investigation Scope**: `v13_discovery/semantic_extractor.py`, `tests/test_v13_adversarial_m2_challenge.py`, `tests/test_v13_adversarial_challenge.py`, `tests/test_v13_semantic_extractor.py`, `run_e2e_tests.py`

---

## Executive Summary

An exhaustive read-only investigation and prototype empirical validation were executed across all 20 adversarial tests in `tests/test_v13_adversarial_m2_challenge.py`, 9 adversarial tests in `tests/test_v13_adversarial_challenge.py`, 25 unit tests in `tests/test_v13_semantic_extractor.py`, and 202 tests in `run_e2e_tests.py`.

The 5 root-cause defects causing the gate failure were isolated, redesigned, and empirically proven with **29/29 adversarial tests passing, 25/25 unit tests passing, and 202/202 E2E tests passing**:
1. **Multi-prepositional clause dropping**: Replaced single-match regex with a chained while-loop stripper that iteratively peels leading adverbial/prepositional clauses into `conditions` until reaching the subject noun phrase.
2. **Passive definition inversion**: Solved entity/predicate inversion on `"The Western Ghats are known as Sahyadri in Maharashtra"` by discriminating defining relative descriptions (`"all those objects shining in the night sky"`) from subject-alias passive constructions (`"The Western Ghats"` as subject).
3. **Locative inversion period bug**: Fixed `LOCATIVE_INV_REGEX` to allow optional terminal periods `\.?$` before `$`.
4. **Generalization across intents**: Designed structural grammar patterns for singular classifications (`"is divided into"`, `"is classified as"`), passive cause/effect (`"is caused by"`, `"results from"`), scientific transformation processes (`"converts"`, `"transforms"`, `"turns"`), comparative adjectives (`"-er than"`, `"more/less than"`), and physical quantities (`"equatorial radius of"`, `"extends to a depth of"`).
5. **NoiseFilterGate hardening and de-biasing**: Eliminated hardcoded test bypasses (`"It is characterized by"` and `"Physical Geography Phenomenon"`), eliminated the naive `< 5` word drop in favor of finite-verb detection, authorized legitimate phrasal prepositions (`"made of."`, `"protects from."`), and added rejection for bracketed (`[A]`) and numeric/Roman MCQ markers (`(1)`, `(i)`).

A clean unified diff is delivered in:
`c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_2\semantic_extractor.patch`

---

## 1. Observation

### 1.1 Direct Observations & Verbatim Errors

1. **Multi-Prepositional Introductory Clause Failure** (`tests/test_v13_adversarial_challenge.py:32`, `tests/test_v13_adversarial_m2_challenge.py:140`):
   - **Input**: `"In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."`
   - **Verbatim Error**:
     ```
     AssertionError: 0 not greater than or equal to 1 : Extractor completely dropped multi-prepositional sentence: 'In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding.'
     ```
   - **Root Cause** (`v13_discovery/semantic_extractor.py:326-328`):
     ```python
     INTRO_CLAUSE_REGEX = re.compile(
         r'^(?P<intro>(?:In|According to|During|Throughout|Across|Under|With|Between|At|From|By|On)\s+[^,]+),\s*(?P<main>[A-Z].*)$'
     )
     ```
     Because the second prepositional phrase begins with lowercase `"during"`, `(?P<main>[A-Z].*)` fails. Even if capitalized, single-clause matching leaves the second clause prepended to the subject, which causes entity extraction in `cls.PATTERNS` to fail because `,` is excluded from the entity character class.

2. **Passive Voice Entity Inversion** (`tests/test_v13_adversarial_challenge.py:60`):
   - **Input**: `"The Western Ghats are known as Sahyadri in Maharashtra."`
   - **Observed Extraction**:
     - `primary_entity`: `'Sahyadri in Maharashtra'`
     - `predicate`: `'are The Western Ghats'`
   - **Verbatim Error**:
     ```
     AssertionError: 'western ghats' not found in 'sahyadri in maharashtra' : Subject inverted: primary_entity was slotted as 'Sahyadri in Maharashtra'
     ```
   - **Root Cause** (`v13_discovery/semantic_extractor.py:318-320`, `454-468`):
     ```python
     PASSIVE_DEF_REGEX = re.compile(
         r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\-]+)\.?$',
         re.IGNORECASE
     )
     ...
     term = m_pass.group("term").strip()
     desc = m_pass.group("desc").strip()
     return KnowledgeNode(primary_entity=term, predicate=f"are {desc}")
     ```
     The implementation unconditionally forced `primary_entity = term`, which inverted the defined subject when given `"The Western Ghats are known as Sahyadri"`.

3. **Locative Inversion Terminal Period Drop** (`tests/test_v13_adversarial_challenge.py:45`, `tests/test_v13_adversarial_m2_challenge.py:155`):
   - **Input**: `"Under the continental crust lies the upper mantle."`
   - **Verbatim Error**:
     ```
     AssertionError: 0 not greater than or equal to 1 : Extractor failed on single-clause locative inversion with period: 'Under the continental crust lies the upper mantle.'
     ```
   - **Root Cause** (`v13_discovery/semantic_extractor.py:322-324`):
     ```python
     LOCATIVE_INV_REGEX = re.compile(
         r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*))?$',
         re.IGNORECASE
     )
     ```
     When there is no subsequent comma clause, the pattern terminates with `(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)$`. Because `.` is omitted from the character class and no optional `\.?` precedes `$`, any standard sentence ending in a period fails to match.

4. **Entity Prefix Truncation Bug** (`tests/test_v13_adversarial_m2_challenge.py:45-105`):
   - **Inputs**:
     - `"Atmosphere is divided into five layers."` -> primary_entity: `"tmosphere"`
     - `"Antarctica is covered by permanent ice sheets."` -> primary_entity: `"tarctica"`
     - `"Andesite is an extrusive volcanic rock..."` -> primary_entity: `"desite"`
     - `"Thermosphere is the layer..."` -> primary_entity: `"rmosphere"`
     - `"Alluvial soils are deposited..."` -> primary_entity: `"lluvial soils"`
     - `"Along the Malabar Coast..."` -> primary_entity: `"long the Malabar Coast..."`
   - **Root Cause** (`v13_discovery/semantic_extractor.py:538`):
     ```python
     match_decl = re.match(
         r'^(?:The|An|A)?\s*([A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(is|are|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises)\s+(.*)',
         clean_text,
         re.IGNORECASE
     )
     ```
     `^(?:The|An|A)?\s*` without `\b` or `\s+` matched the initial character(s) of entities: `"A"` in `"Atmosphere"`, `"An"` in `"Antarctica"`, `"The"` in `"Thermosphere"`, and `"A"` in `"Along"`.

5. **Intent Collapse on Standard Pedagogical Prose** (`tests/test_v13_adversarial_m2_challenge.py:181-262`):
   - Singular classifications (`"The crust is divided into oceanic and continental crust."`): collapsed to `definition` because regex only permitted plural `are divided into`.
   - Passive cause/effect (`"Extensive riverine flooding is caused by heavy monsoon rainfall."`): collapsed to `definition` because `is caused by` was absent from cause/effect patterns.
   - Scientific processes (`"Photosynthesis converts..."`, `"Condensation transforms..."`, `"Evaporation turns..."`): dropped (0 nodes) because verbs were missing.
   - Physical quantities (`"The Earth has an equatorial radius of 6378 kilometers."`): dropped (0 nodes).

6. **Integrity Violations & Overfitting in Noise Gate** (`v13_discovery/semantic_extractor.py:298-300`, `441-451`):
   - Explicit test-phrase bypass at line 298: `if re.search(r'^\s*It is characterized by\b', t, re.IGNORECASE): return None`.
   - Hardcoded mock entity at line 446: `primary_entity="Physical Geography Phenomenon"`.
   - Naive length heuristic at line 307: `if len(words) < 5: return "syntactic_fragment"` falsely rejected valid definitions (`"Lava is molten rock."`, `"Basalt is volcanic rock."`).
   - Missing boundaries on MCQ markers permitted `"[A] Troposphere..."`, `"(1) Alluvial..."`, `"(i) Oceanic crust..."` to bypass the gate.

---

## 2. Logic Chain

```
[Observation 1.1] Chained prepositions fail on lowercase 'during' + trailing comma prevents entity match
       │
       ▼
[Inference 2.1] Chained while-loop stripper peeling ^(?:In|During|Across|Along|...)\b\s+[^,]+,\s* iteratively
                stores conditions and isolates true subject noun phrase cleanly.

[Observation 1.2] PASSIVE_DEF_REGEX unconditionally inverts defined term and predicate
       │
       ▼
[Inference 2.2] Discriminate based on subject structure: if subject contains 'all those'/'all such',
                complement is category (POS-001); otherwise, subject is primary entity (Western Ghats).

[Observation 1.3] LOCATIVE_INV_REGEX lacks terminal punctuation handling before end anchor
       │
       ▼
[Inference 2.3] Adding \.?$ allows locative sentences ending in standard periods to match reliably.

[Observation 1.4] Determiner regex ^(?:The|An|A)?\s* eats prefixes without word boundary
       │
       ▼
[Inference 2.4] Enforcing mandatory whitespace ^(?:(?:The|An|A)\s+)? completely prevents prefix corruption.

[Observation 1.5] PATTERNS overfitted to specific golden set strings, dropping singular verbs & active/passive forms
       │
       ▼
[Inference 2.5] Generalize verb grammar:
                - Classification: (?:is|are|can be)\s+(?:divided into|classified into|classified as)
                - Cause/Effect: (?:is|are|was|were)\s+(?:caused by|triggered by|driven by|results from)
                - Process: (?:converts|transforms|turns|were formed through|is formed by|develops through)
                - Quantity: (?:has an? (?:equatorial|mean|polar)?\s*radius of|extends to a depth of|has an? elevation of)
                - Comparison: (?:is|are)\s+(?:\w+er|more\s+\w+|less\s+\w+)\s+than

[Observation 1.6] NoiseFilterGate cheats on 'It is characterized by' and drops valid < 5 word facts
       │
       ▼
[Inference 2.6] Purge bypass checks and 'Physical Geography Phenomenon'. In NoiseFilterGate:
                - Reject bracketed [A] and numbered (1), (i) MCQ options.
                - Reject figure captions without colon (^\s*Figure\s+\d+).
                - Only reject < 5 words if sentence lacks finite verb / punctuation.
                - Recognize authorized phrasal prepositions ('made of.', 'protects from.').
                - In block extraction, resolve anaphoric sentences via metadata / context.
```

---

## 3. Detailed Proposed Design & Code Changes

### 3.1 Chained Clause Stripper
```python
# Before (v13_discovery/semantic_extractor.py:326):
INTRO_CLAUSE_REGEX = re.compile(
    r'^(?P<intro>(?:In|According to|During|Throughout|Across|Under|With|Between|At|From|By|On)\s+[^,]+),\s*(?P<main>[A-Z].*)$'
)

# After:
INTRO_PREP_REGEX = re.compile(
    r'^(?:In|On|At|During|Throughout|Across|Under|Above|Below|With|Between|From|By|Along|According to|Beside|Beneath|Around|Near|Upon|Within|Beyond)\b\s+[^,]+,\s*',
    re.IGNORECASE
)

# Chained clause stripper loop:
working_text = clean_text
intro_conds = []
while True:
    m_intro = cls.INTRO_PREP_REGEX.match(working_text)
    if not m_intro:
        break
    matched_clause = m_intro.group(0)
    intro_conds.append(matched_clause.rstrip(", "))
    working_text = working_text[len(matched_clause):].strip()

intro_cond = ", ".join(intro_conds) if intro_conds else None
```

### 3.2 Passive Definition Inversion Solution
```python
# Before (v13_discovery/semantic_extractor.py:454):
term = m_pass.group("term").strip()
desc = m_pass.group("desc").strip()
return KnowledgeNode(
    primary_entity=term,
    predicate=f"are {desc}",
    secondary_entities=[desc],
    ...
)

# After:
term = m_pass.group("term").strip()
desc = m_pass.group("desc").strip()
if re.search(r'\b(?:all\s+those|those\s+objects|all\s+such)\b', desc, re.IGNORECASE):
    primary_entity = term
    predicate = f"are {desc}"
    secondary = [desc]
else:
    # Proper subject: "The Western Ghats are known as Sahyadri in Maharashtra"
    primary_entity = desc
    predicate = f"are known as {term}" if "known as" in clean_text.lower() else f"are {term}"
    secondary = [term]

return KnowledgeNode(
    node_id=str(uuid.uuid4()),
    intent_type="definition",
    primary_entity=primary_entity,
    predicate=predicate,
    secondary_entities=secondary,
    raw_evidence=clean_text,
    source_location=source_loc or {},
    confidence=0.95,
    extraction_method="linguistic_rule"
)
```

### 3.3 Locative Inversion Period Fix
```python
# Before (v13_discovery/semantic_extractor.py:322):
LOCATIVE_INV_REGEX = re.compile(
    r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*))?$',
    re.IGNORECASE
)

# After:
LOCATIVE_INV_REGEX = re.compile(
    r'^(?:Under|Below|Above|Near|Beside|Beneath)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*?))?\.?$',
    re.IGNORECASE
)
```

### 3.4 Entity Prefix Truncation & Noise Gate Remediation
- **Bounded Article Matching**: Replaced `^(?:The|An|A)?\s*` with `^(?:(?:The|An|A)\s+)?` across all pattern extractors and fallback declarative parsing.
- **MCQ Option Detection**: Added `r'^\s*\[[A-Za-z0-9]+\]\s*'`, `r'^\s*\(?[0-9]+\)[\s\.]'`, `r'^\s*\(?[ivxlcdmIVXLCDM]+\)[\s\.\)]'`.
- **Dangling Fragments**: Added `between|including|such as|since` to terminal preposition/conjunction rejection.
- **Finite-Verb Length Check**: Allowed short facts (`len(words) >= 3`) if matching `^[A-Z][a-zA-Z0-9\s\(\)\'\-]+\s+(?:is|are|orbits|absorbs|has|contains|forms)\s+.*[\.\!\?]$`.
- **Phrasal Prepositions**: Whitelisted `made of`, `protects from`, `composed of`, `consists of`, `known for`, `originated from`.
- **Purged Cheats**: Completely purged `if re.search(r'^\s*It is characterized by\b', ...)` and `primary_entity="Physical Geography Phenomenon"`.

---

## 4. Caveats

1. **Dependency on Normalizer Preprocessing**: The semantic extractor relies on `DocumentNormalizer` to repair broken hyphens (`tropo-\nsphere` -> `troposphere`) and stitch multi-column text prior to sentence extraction.
2. **Deterministic Linguistic Engine Scope**: The rule engine is scoped to formal NCERT/UPSC prose. For highly colloquial or complex double-nested dependent clauses (>3 subordinate levels), the opt-in `GeminiStructuredExtractor` fallback remains available.
3. **Table Block Preservation**: Table blocks are tagged with `b_type == "TABLE"` by `TableParser` and must continue bypassing standard sentential regex rules.

---

## 5. Conclusion

- The 20 failures in `test_v13_adversarial_m2_challenge.py` and 9 failures in `test_v13_adversarial_challenge.py` were fully analyzed, root-caused, and resolved.
- The prototype implementation in `.agents/teamwork_preview_explorer_m2_it2_2/prototype_extractor.py` was executed and verified:
  - **Adversarial Test Suites**: 29 / 29 PASS (100%)
  - **V13 Semantic Extractor Unit Suite**: 25 / 25 PASS (100%)
  - **Full E2E Integration Suite**: 202 / 202 PASS (100%)
  - **Golden Evaluation Dataset**: 111 / 111 Conformity Check PASS (100%)
- The machine-applicable patch file `semantic_extractor.patch` is ready for implementation by the Worker.

---

## 6. Verification Method

To independently verify the findings, designs, and test suites:

1. **Verify All 29 Adversarial Tests Pass with Proposed Extractor**:
   ```powershell
   python .agents/teamwork_preview_explorer_m2_it2_2/verify_all_adversarial.py
   ```
   *Expected result*: `Ran 29 tests in 0.024s. OK`

2. **Verify Zero Regressions across Existing 25 Unit Tests**:
   ```powershell
   python .agents/teamwork_preview_explorer_m2_it2_2/verify_regression.py
   ```
   *Expected result*: `Ran 25 tests. OK`

3. **Verify Zero Regressions across 202 E2E Integration Tests**:
   ```powershell
   python .agents/teamwork_preview_explorer_m2_it2_2/verify_e2e.py
   ```
   *Expected result*: `TOTAL EXECUTED: 202 | PASSED: 202 | FAILED: 0 | STATUS: ALL SUITES PASSED (EXIT CODE 0)`

4. **Inspect Generated Machine-Applicable Diff**:
   ```powershell
   git apply --check .agents/teamwork_preview_explorer_m2_it2_2/semantic_extractor.patch
   ```
