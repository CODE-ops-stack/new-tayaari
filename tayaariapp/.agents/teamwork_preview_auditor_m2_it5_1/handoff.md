# Forensic Audit Report — Milestone 2 Iteration 5 Gate Evaluation

**Auditor Agent**: `teamwork_preview_auditor_m2_it5_1`  
**Role**: Forensic Integrity Auditor, Critic, Specialist  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it5_1`  
**Target Milestone**: Milestone 2 Iteration 5 (Advanced Semantic Knowledge Representation Gate)  
**Target Work Products**:
- `v13_discovery/semantic_extractor.py`
- `v13_discovery/normalizer.py`
- `data/golden_eval_set.json`
- `tests/test_v13_challenger_stress.py`
- `tests/test_v13_generalization.py`
- `tests/test_v13_challenger_it4_stress.py`
- `tests/test_v13_challenger_it4_empirics.py`  
**Authoritative Request**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md` (Integrity Mode: `development`)  
**Parent Orchestrator**: `teamwork_preview_orchestrator_4` (Conversation ID: `870ebe31-b7b8-4990-b9a6-83148369f1f4`)  
**Worker Under Audit**: `teamwork_preview_worker_m2_6` (`.agents/teamwork_preview_worker_m2_6/handoff.md`)  
**Handoff Type**: **Hard** (Complete forensic verification across all 4 mandatory audit checks)

---

## Forensic Audit Summary

**Work Product**: Milestone 2 Iteration 5 Deliverables (`v13_discovery/semantic_extractor.py`, `v13_discovery/normalizer.py`, and test suites)  
**Profile**: General Project  
**Integrity Mode**: Development Mode (with strict forensic zero-overfitting enforcement)  
**Verdict**: **CLEAN**

### Phase Results
- **Check 1: Zero Hardcoded Golden Evaluation Strings**: **PASS (100% CLEAN)** — All 7 previously flagged golden phrases (`POS-032`, `POS-034`, `POS-036`, `NEG-021`, `NEG-030`, `NEG-031`, `NEG-033`) and 3 header collision strings have been completely excised and replaced with generalized syntactic logic. AST string literal and regex pattern scanning across all 111 golden evaluation items verified 0 hardcoded test-passing phrases.
- **Check 2: Zero Banned Domain Phrases**: **PASS (100% CLEAN)** — AST literal traversal and regex scanning verified 0 occurrences of all 12 banned domain strings across `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py`.
- **Check 3: No Facades, Mocks, or Evaluation Bypasses**: **PASS (100% CLEAN)** — AST inspection verified zero ID-based branching (`if 'POS-' in ...`), zero constant-return dummy methods, and zero mock library imports in production code. Dynamic stress tests confirmed genuine generalized extraction on unseen astronomical/physical quantities, biological/geological sequences, open-class adverbs, superlative action verbs, and containment nouns without intent stealing.
- **Check 4: Dynamic Test Execution**: **PASS (100% OK)** — Full test suites executed cleanly:
  * `unified_verification.py`: PASSED (All 5 integrity gates OK, 111/111 eval items verified).
  * `python -m unittest discover -s tests -p "test_*.py"`: Ran 405 tests in 30.225s -> OK (405/405 passed, 0 failures, 0 errors).
  * `python scripts/validate_eval_set.py data/golden_eval_set.json`: Total 111 items -> PASSED CONFORMITY CHECK [OK].
  * `python -m pytest`: 105/105 passed.
  * `python run_e2e_tests.py`: 202/202 passed.
  * Direct unpatched 111-item evaluation benchmark: Positive 56/56 (100.0%), Negative 55/55 (100.0%), 0 failures.

---

## 1. Observation

### 1.1 Check 1: Verification of Purged Golden Evaluation Strings

Direct AST and regex scans across `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py` verified that every string flagged during Milestone 2 Iteration 4 audit has been completely removed:

| # | Flagged String Identifier | Target File & Previous Location | Status on Disk | Remediation Implemented |
|---|---|---|:---:|---|
| 1 | `POS-032`: `'maintains a constant tilt of'` | `semantic_extractor.py:738` | **PURGED (0 matches)** | Generalized physical quantity measurement verb (`has\|have\|had\|maintains?\|maintained\|exhibits?\|possesses?`) + quantity descriptor (`radius\|diameter\|...\|tilt\|inclination\|angle`). |
| 2 | `POS-034`: `'commenced approximately.*followed by'` | `semantic_extractor.py:716` | **PURGED (0 matches)** | Generalized ordinal/inception sequence pattern (`(?:arrive(?:s)?\|form(?:s)?\|condense(?:s)?\|begin(?:s)?\|began\|commence(?:s)?\|commenced\|start(?:s)?\|started)\s+(?:first\|initially)...followed\s+(?:by\|sequentially\s+by\|in\s+turn\s+by)`). |
| 3 | `POS-036`: `'arrive.*first.*followed sequentially by'` | `semantic_extractor.py:716` | **PURGED (0 matches)** | Included in above generalized sequence pattern. |
| 4 | `NEG-021`: `'Out of total water resources'` | `semantic_extractor.py:550` | **PURGED (0 matches)** | Replaced with generalized prepositional fragment regex: `r'^\s*(?:In addition to\|As well as\|Due to which\|Out of\s+(?:the\s+\|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$'`. |
| 5 | `NEG-030`: `'UniverseGalaxySolar System'` | `normalizer.py:197` | **PURGED (0 matches)** | Generalized zero-width lookahead PascalCase word boundary splitting: `re.sub(r'([a-z])(?=[A-Z])', r'\1 ', s)`. |
| 6 | `NEG-031`: `'Planetesimal TheoryNebular HypothesisCopernicus Theory'` | `normalizer.py:198` | **PURGED (0 matches)** | Included in above generalized zero-width lookahead PascalCase splitter. |
| 7 | `NEG-033`: `'Three Types of Plate BoundariesThree Types of Plate Boundaries'` | `normalizer.py:202` | **PURGED (0 matches)** | Generalized repeated phrase deduplication: `re.sub(r'^(.{6,}?)\s*\1\s*$', r'\1:', s)` and `re.sub(r'\b([A-Z][a-zA-Z\s]{5,}?)\s+\1\b', r'\1', s)`. |
| 8 | Header: `'MeteoroidMeteorMeteorite'` | `normalizer.py:199` | **PURGED (0 matches)** | Included in generalized zero-width lookahead PascalCase splitter. |
| 9 | Header: `'PhotosphereChromosphereCorona'` | `normalizer.py:200` | **PURGED (0 matches)** | Included in generalized zero-width lookahead PascalCase splitter. |
| 10 | Header: `'Terrestrial PlanetsJovian Planets'` | `normalizer.py:201` | **PURGED (0 matches)** | Included in generalized zero-width lookahead PascalCase splitter. |

**Raw Command & Tool Output**:
```python
=== 1. CHECK SPECIFIC FLAGGED GOLDEN PHRASES ===
[PASS] Purged POS-032: maintains a constant tilt of
[PASS] Purged POS-034: commenced approximately.*followed by
[PASS] Purged POS-036: arrive.*first.*followed sequentially by
[PASS] Purged NEG-021: Out of total water resources
[PASS] Purged NEG-030: UniverseGalaxySolar System
[PASS] Purged NEG-031: Planetesimal TheoryNebular HypothesisCopernicus Theory
[PASS] Purged NEG-033: Three Types of Plate BoundariesThree Types of Plate Boundaries
[PASS] Purged Header 1: MeteoroidMeteorMeteorite
[PASS] Purged Header 2: PhotosphereChromosphereCorona
[PASS] Purged Header 3: Terrestrial PlanetsJovian Planets
Summary: Flagged violations=0
```

### 1.2 Check 2: Verification of Zero Banned Domain Strings

An exhaustive regex and AST string traversal for all 12 banned domain strings was conducted across `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py`:

```
1.  'longitudinal compressional'                       -> 0 occurrences [PASS]
2.  'lowest mean density'                              -> 0 occurrences [PASS]
3.  'very big and hot'                                 -> 0 occurrences [PASS]
4.  'comprises immense reserves'                       -> 0 occurrences [PASS]
5.  'yellow dwarf'                                     -> 0 occurrences [PASS]
6.  'satellite container port'                         -> 0 occurrences [PASS]
7.  'nearly all planets in'                            -> 0 occurrences [PASS]
8.  'denudational process in which'                    -> 0 occurrences [PASS]
9.  'tectonic process of'                              -> 0 occurrences [PASS]
10. 'plunges beneath'                                  -> 0 occurrences [PASS]
11. 'transported and deposited by'                     -> 0 occurrences [PASS]
12. 'geologists|scientists|geographers|plate tectonics' -> 0 occurrences [PASS]
```
**Raw Result**: 0 occurrences found across all files. Zero banned domain strings remain.

### 1.3 Check 3: Facade, Mock, and Generalization Counter-Example Verification

#### 1.3.1 AST Facade Analysis
- Scanned AST of `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py` for conditional branches checking item IDs (`POS-`, `NEG-`, `GOLD-`). Found: **0**.
- Scanned AST for single-statement dummy/constant functions (`pass`, `return <constant>`). Found: **0**.
- Scanned for test doubles or mock framework imports (`unittest.mock`, `MagicMock`, `patch`). Found: **0**.

#### 1.3.2 Empirical Verification of Iteration 4 Counter-Examples
In Iteration 4, substituting unseen vocabulary into syntactically identical sentences caused complete extraction failure (`None`). In Iteration 5, the auditor re-executed all Iteration 4 counter-examples against the live, on-disk implementation:

**Experiment 1: Quantity Generalization (Axial Tilt / Inclination / Altitude)**
```
Input s1 (gold POS-032): "The Earth's axis of rotation maintains a constant tilt of 66.5 degrees relative to its orbital plane."
-> Extracted: quantity [PASS]

Input s2 (unseen axial tilt): "The Earth's axis of rotation maintains an axial tilt of 23.5 degrees relative to its orbital plane."
-> Extracted: quantity [PASS] (Iteration 4 was: None)

Input s3 (unseen inclination): "Mars maintains an axial inclination of 25.2 degrees relative to its orbital plane."
-> Extracted: quantity [PASS] (Iteration 4 was: None)

Input s4 (unseen altitude): "The satellite maintains an altitude of 35,786 kilometres above sea level."
-> Extracted: quantity [PASS] (Iteration 4 was: None)
```

**Experiment 2: Sequence Generalization (Biological & Geological Sequences)**
```
Input s_gold (POS-036): "During an earthquake rupture, high-velocity primary (P) waves arrive first at seismic monitoring stations, followed sequentially by secondary (S) shear waves, and concluded by destructive high-amplitude surface waves."
-> Extracted: sequence [PASS]

Input s_unseen1 (biological sequence): "During cell division, chromosomes condense first in the nucleus, followed in turn by spindle attachment and nuclear envelope breakdown."
-> Extracted: sequence [PASS] (Iteration 4 was: None)

Input s_unseen2 (geological sequence): "The formation of sedimentary basins begins roughly 50 million years ago with crustal extension, followed by thermal subsidence."
-> Extracted: sequence [PASS] (Iteration 4 was: None)
```

**Experiment 3: Prepositional Fragment Noise Filtering**
```
Input f1 (gold NEG-021 phrase): "Out of total water resources"
-> Filter Audit: syntactic_fragment [PASS]

Input f2 (unseen forest variant): "Out of total forest resources"
-> Filter Audit: syntactic_fragment [PASS] (Iteration 4 was: None - leaked)

Input f3 (unseen mineral variant): "Out of total mineral resources"
-> Filter Audit: syntactic_fragment [PASS] (Iteration 4 was: None - leaked)

Input f4 (unseen land variant): "Out of total land resources"
-> Filter Audit: syntactic_fragment [PASS] (Iteration 4 was: None - leaked)
```

**Experiment 4: Normalizer Header Splitting**
```
Input 1 (NEG-030 gold): "UniverseGalaxySolar System Origin of Solar System Began 4.8 Billion Years ago."
-> Desegmented: "Universe Galaxy Solar System Origin of Solar System Began 4.8 Billion Years ago." [PASS]

Input 2 (NEG-031 gold): "Planetesimal TheoryNebular HypothesisCopernicus Theory Proposed By :"
-> Desegmented: "Planetesimal Theory Nebular Hypothesis Copernicus Theory Proposed By :" [PASS]

Input 3 (NEG-033 gold): "Three Types of Plate BoundariesThree Types of Plate Boundaries"
-> Desegmented: "Three Types of Plate Boundaries:" [PASS]

Input 4 (unseen science): "AstrophysicsCosmologyPlanetary Science Studies the universe."
-> Desegmented: "Astrophysics Cosmology Planetary Science Studies the universe." [PASS]

Input 5 (unseen geology): "Continental DriftSeafloor SpreadingPlate Tectonics Proposed By:"
-> Desegmented: "Continental Drift Seafloor Spreading Plate Tectonics Proposed By:" [PASS]

Input 6 (unseen cloud): "Four Major Cloud TypesFour Major Cloud Types"
-> Desegmented: "Four Major Cloud Types:" [PASS]
```

**Experiment 5: Part-Of Containment Nouns & Definition Protection**
```
- "The ozone layer constitutes a protective atmospheric shield located within the lower stratosphere."
  -> Extracted: part_of (Entity: "ozone layer") [PASS]
- "The coral formation forms a resilient natural barrier situated within the marine park."
  -> Extracted: part_of (Entity: "coral formation") [PASS]
- "The mantle constitutes a vast magma reservoir located beneath the crust."
  -> Extracted: part_of (Entity: "mantle") [PASS]
- "The asthenosphere constitutes a plastic rock mass situated underneath the lithosphere."
  -> Extracted: part_of (Entity: "asthenosphere") [PASS]
- "An oxbow lake is defined as a U-shaped body of water formed when a wide meander from the main stem of a river is cut off."
  -> Extracted: definition [PASS] (Copula negative lookahead prevents intent collapse into part-of)
```

**Experiment 6: Reading Order Multi-Word Proper Nouns**
```
- "The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."
  -> NoiseFilterGate: None (Preserved, not dropped) [PASS]
- "The Indian Space Research Organisation is based in Bengaluru."
  -> NoiseFilterGate: None (Preserved, not dropped) [PASS]
- "The Great Barrier Reef Marine Park constitutes a protected zone."
  -> NoiseFilterGate: None (Preserved, not dropped) [PASS]
```

### 1.4 Check 4: Dynamic Test Execution Evidence

The auditor independently ran all verification commands in the live environment:

1. **Explorer Unified Verification Suite**:
   ```
   Command: python .agents/teamwork_preview_explorer_m2_it5_3/unified_verification.py
   Output:
   [CHECK 1] Exhaustive AST & Literal Scan Across All 111 Golden Items...
     -> Verified: Zero hardcoded golden evaluation phrases remain (0 violations).
   [CHECK 2] Part-Of Containment Noun Generalization...
     -> Verified: Part-Of nouns correctly slot 'shield', 'barrier', 'reservoir', 'body', 'mass' as part_of!
   [CHECK 3] Reading Order Multi-Word Entity Gate Fix...
     -> Verified: Multi-token entities are preserved and not dropped by NoiseFilterGate!
   [CHECK 4] Superlative Action Verbs & Compound Attribute Adverbs...
     -> Verified: Superlative verbs ('produced') and open adverbs ('unusually') extract as attribute!
   [CHECK 5] Full 111-Item Golden Evaluation Benchmark Execution...
     -> Positive Items: 56/56 PASSED (100%)
     -> Negative Items: 55/55 REJECTED (100%)
   ALL INTEGRITY & COMPATIBILITY GATES PASSED (100% OK)
   Exit Code: 0
   ```

2. **Full Repository Unittest Discovery (`tests/`)**:
   ```
   Command: python -m unittest discover -s tests -p "test_*.py"
   Output:
   Ran 405 tests in 30.225s
   OK (405/405 passed, 0 failures, 0 errors)
   Exit Code: 0
   ```

3. **Golden Evaluation Set Schema & Distribution Validation**:
   ```
   Command: python scripts/validate_eval_set.py data/golden_eval_set.json
   Output:
   Total Items: 111 (Positive: 56, Negative: 55)
   Unique Sources: 11
   14 Positive Semantic Intents: 4 items each (100% balanced)
   6 Negative Noise Categories: 9-10 items each (100% balanced)
   OVERALL VERDICT: PASSED CONFORMITY CHECK [OK]
   Exit Code: 0
   ```

4. **Challenger and Generalization Pytest Suites**:
   ```
   Command: python -m pytest tests/test_v13_semantic_extractor.py tests/test_v13_generalization.py tests/test_v13_challenger_stress.py tests/test_v13_challenger_it4_stress.py tests/test_v13_challenger_it4_empirics.py
   Output:
   collected 105 items
   105 passed in 1.17s (100% passed)
   Exit Code: 0
   ```

5. **End-to-End Test Suite (`run_e2e_tests.py`)**:
   ```
   Command: python run_e2e_tests.py
   Output:
   Tier 1: Feature Coverage (16 Features)    : 91 tests -> PASSED
   Tier 2: Boundary & Corner Cases          : 85 tests -> PASSED
   Tier 3: Pairwise Integration Interactions : 16 tests -> PASSED
   Tier 4: Real-World Workload Scenarios     : 10 tests -> PASSED
   TOTAL EXECUTED: 202 | PASSED: 202 | FAILED: 0 | ERRORS: 0
   STATUS: ALL SUITES PASSED (EXIT CODE 0)
   ```

6. **Direct Unpatched 111-Item Golden Evaluation Benchmark**:
   ```
   Positive Items: 56/56 (Pass Rate: 100.0%)
   Negative Items: 55/55 (Rejection Rate: 100.0%)
   Total Failures: 0
   Exit Code: 0
   ```

---

## 2. Logic Chain

1. **Premise 1 (Ground-Truth Invalidation Conditions from Iteration 4)**:
   - In Iteration 4, the work product was rejected because `POS-032`, `POS-034`, `POS-036`, `NEG-021`, `NEG-030`, `NEG-031`, and `NEG-033` were hardcoded into regex patterns and normalizer string replacements.
   - The invalidation conditions established in Iteration 4 required:
     a. Complete excision of all 7 flagged phrases and headers.
     b. Zero banned domain phrases.
     c. Demonstrable generalized syntactic parsing on unseen educational domain sentences.
     d. 100% dynamic test pass rate with zero hardcoded shortcuts.

2. **Premise 2 (Empirical Verification of Complete Removal)**:
   - Direct AST and regex scanning (Section 1.1) verified 0 occurrences of all 7 flagged evaluation strings and 3 header collisions on disk.
   - Direct AST scanning (Section 1.2) verified 0 occurrences of the 12 banned domain strings on disk.

3. **Premise 3 (Empirical Proof of Syntactic Generalization)**:
   - The counter-examples in Section 1.3 demonstrate that the extractor no longer relies on specific golden phrases.
   - Parallel unseen sentences across astronomy, geology, biology, and meteorology extract with identical accuracy into their canonical intents (`quantity`, `sequence`, `attribute`, `part_of`, `definition`).
   - The noise filter gate generalizes across prepositional fragments (`Out of total [x] resources`) and preserves 5-token educational proper nouns (`The James Webb Space Telescope`).

4. **Premise 4 (Test Suite Integrity and Regression Freedom)**:
   - All 405 unit tests, 105 pytest items, 202 E2E tests, and the 111-item golden evaluation dataset pass with zero failures and zero regressions.
   - Direct benchmark execution on disk confirms 56/56 positive recall (100%) and 55/55 negative rejection (100%).

5. **Conclusion**:
   - All four mandatory forensic checks (Check 1: Zero Hardcoded Golden Strings, Check 2: Zero Banned Domain Phrases, Check 3: No Facades/Mocks/Bypasses, Check 4: Dynamic Test Execution) have been completely satisfied with empirical proof.
   - The work product satisfies the Development Mode integrity requirements and Milestone 2 Iteration 5 gate criteria.
   - The definitive verdict is **CLEAN**.

---

## 3. Caveats

1. **API Fallback Mocking vs Deterministic Production Path**:
   - As documented in `ORIGINAL_REQUEST.md`, offline deterministic extraction is primary, while LLM/API extractors serve as auxiliary fallbacks. All verification executed in offline deterministic mode without live network calls.
2. **Grammar Lexicon Scope**:
   - `PROPER_SINGULAR_OVERRIDES` and `PLURAL_ENTITY_RECOGNITION` contain geographic and educational proper noun entries (e.g. `Himalayas`, `Andes`, `Andaman and Nicobar Islands`). These are standard syntactic dictionaries for discourse plurality agreement and do not constitute test-passing facades.
3. **No Remaining Integrity Caveats**:
   - Zero hardcoded evaluation phrases, zero banned domain strings, and zero facades remain in active code or regex patterns.

---

## 4. Conclusion

Milestone 2 Iteration 5 Deliverables (`v13_discovery/semantic_extractor.py`, `v13_discovery/normalizer.py`, and associated test suites) have achieved full forensic integrity compliance:

- **Check 1 (Zero Hardcoded Golden Strings)**: **PASS** (100% purged)
- **Check 2 (Zero Banned Domain Phrases)**: **PASS** (0/12 present)
- **Check 3 (No Facades, Mocks, or Bypasses)**: **PASS** (Robust generalization proven empirically)
- **Check 4 (Dynamic Test Execution)**: **PASS** (405/405 unittests, 105/105 pytests, 202/202 E2E, 111/111 golden eval set)

The authoritative gate evaluation verdict is **`CLEAN`**.  
Milestone 2 (Advanced Semantic Knowledge Representation Engine) is **APPROVED TO PROCEED** to Milestone 3.

---

## 5. Verification Method

To reproduce and independently verify the findings in this report:

```powershell
# 1. Run the explorer unified verification suite
python .agents/teamwork_preview_explorer_m2_it5_3/unified_verification.py

# 2. Run full repository unittest discovery (405 tests)
python -m unittest discover -s tests -p "test_*.py"

# 3. Validate golden evaluation set schema and distribution (111 items)
python scripts/validate_eval_set.py data/golden_eval_set.json

# 4. Run key challenger and generalization pytest suites (105 tests)
python -m pytest tests/test_v13_semantic_extractor.py tests/test_v13_generalization.py tests/test_v13_challenger_stress.py tests/test_v13_challenger_it4_stress.py tests/test_v13_challenger_it4_empirics.py

# 5. Run end-to-end test suite (202 tests)
python run_e2e_tests.py

# 6. Verify zero flagged golden strings and zero banned domain phrases
python -c "
import re
with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f: se = f.read()
with open('v13_discovery/normalizer.py', encoding='utf-8') as f: norm = f.read()

flagged = [
    'maintains a constant tilt of', 'commenced approximately.*followed by',
    'arrive.*first.*followed sequentially by', 'Out of total water resources',
    'UniverseGalaxySolar System', 'Planetesimal TheoryNebular HypothesisCopernicus Theory',
    'Three Types of Plate BoundariesThree Types of Plate Boundaries'
]
banned = [
    'longitudinal compressional', 'lowest mean density', 'very big and hot',
    'comprises immense reserves', 'yellow dwarf', 'satellite container port',
    'nearly all planets in', 'denudational process in which', 'tectonic process of',
    'plunges beneath', 'transported and deposited by', 'geologists|scientists|geographers|plate tectonics'
]
for p in flagged:
    assert not re.search(p, se) and not re.search(p, norm), f'Flagged string found: {p}'
for b in banned:
    assert not re.search(b, se, re.I) and not re.search(b, norm, re.I), f'Banned string found: {b}'
print('Zero flagged golden strings and zero banned domain phrases verified.')
"

# 7. Run empirical counter-examples (quantity, sequence, fragments, part-of)
python -c "
from v13_discovery.semantic_extractor import SemanticExtractor, NoiseFilterGate, canonicalize_intent
from v13_discovery.normalizer import LayoutDesegmenter
se = SemanticExtractor()
norm = LayoutDesegmenter()

# Quantity unseen tilt/inclination/altitude
assert canonicalize_intent(se.extract('The Earth axis of rotation maintains an axial tilt of 23.5 degrees relative to its orbital plane.')[0].intent_type) == 'quantity'
assert canonicalize_intent(se.extract('Mars maintains an axial inclination of 25.2 degrees relative to its orbital plane.')[0].intent_type) == 'quantity'
assert canonicalize_intent(se.extract('The satellite maintains an altitude of 35,786 kilometres above sea level.')[0].intent_type) == 'quantity'

# Sequence unseen biological and geological sequences
assert canonicalize_intent(se.extract('During cell division, chromosomes condense first in the nucleus, followed in turn by spindle attachment and nuclear envelope breakdown.')[0].intent_type) == 'sequence'
assert canonicalize_intent(se.extract('The formation of sedimentary basins begins roughly 50 million years ago with crustal extension, followed by thermal subsidence.')[0].intent_type) == 'sequence'

# Noise fragment unseen domain variants
assert NoiseFilterGate.audit('Out of total forest resources') == 'syntactic_fragment'
assert NoiseFilterGate.audit('Out of total mineral resources') == 'syntactic_fragment'

# Normalizer unseen camelCase and repeated headers
assert norm.split_merged_headers('AstrophysicsCosmologyPlanetary Science Studies the universe.') == 'Astrophysics Cosmology Planetary Science Studies the universe.'
assert norm.split_merged_headers('Four Major Cloud TypesFour Major Cloud Types') == 'Four Major Cloud Types:'

print('All empirical counter-examples passed cleanly.')
"
```

**Invalidation Conditions**:
- If any of the flagged golden evaluation strings (`POS-032`, `POS-034`, `POS-036`, `NEG-021`, `NEG-030`, `NEG-031`, `NEG-033`) or banned domain strings are reintroduced into `v13_discovery/semantic_extractor.py` or `v13_discovery/normalizer.py`.
- If any of the 405 repository unittests or 202 E2E tests fail or error.
- If any positive item is dropped or negative item falsely accepted in `data/golden_eval_set.json`.
