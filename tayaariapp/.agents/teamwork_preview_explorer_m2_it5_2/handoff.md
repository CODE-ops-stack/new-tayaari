# Handoff Report: Explorer 2 (Milestone 2 Iteration 5)

**Author Agent**: `teamwork_preview_explorer_m2_it5_2`  
**Role**: Explorer, Synthesizer, Specialist  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2`  
**Target Files Analyzed**:
- `v13_discovery/semantic_extractor.py` (Lines 544–578: `NoiseFilterGate`)
- `v13_discovery/normalizer.py` (Lines 193–207: `LayoutDesegmenter.split_merged_headers`)
- `data/golden_eval_set.json` (Items `NEG-021`, `NEG-029`, `NEG-030`, `NEG-031`, `NEG-032`, `NEG-033`)
- `tests/test_v13_challenger_it4_stress.py` (Line 496: `test_boundary_capitalized_words_noise_gate`)  
**Parent Orchestrator**: `teamwork_preview_orchestrator_3` (Conversation ID: `f2a26050-100d-4ce0-9c9c-ad53fd921d9e`)  
**Handoff Type**: **Hard** (Investigation and Formulation Complete)  

---

## 1. Observation

### 1.1 Verbatim Hardcoded String in NoiseFilterGate (`semantic_extractor.py:550`)
- **Direct File Observation**:
  `v13_discovery/semantic_extractor.py:544-556`:
  ```python
  544:         "syntactic_fragment": [
  545:             r'\b(?:and|or|but|with|that|which|whose|because|while|whereas|although|in|to|along|into|including|such as|since|between|among|due to|as well as|under|without)\s*[\.\!\?]?\s*$',
  546:             r'(?<!made\s)\bof\s*[\.\!\?]?\s*$',
  547:             r'(?<!protects\s)(?<!protect\s)(?<!us\s)(?<!them\s)(?<!differ\s)(?<!originates\s)\bfrom\s*[\.\!\?]?\s*$',
  548:             r'\.\.\.\s*$',
  549:             r'\.{2,}\s*$',
  550:             r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$',
  551:             r'^\s*Because\s+(?:despite|although|though|if|when|while)\b',
  552:             r'^\s*(?:While|When|Because|Although)\s+[a-z]+ing\b.*[\.\!\?]?\s*$',
  553:             r'^\s*(?:In|At|On|From)\s+(?:Rural|Urban|Total|General|Primary|Secondary),\s+',
  554:             r'^\s*And\s+(?:for\s+this\s+reason\s+also|therefore|so|hence)\s*[\.\!\?]?\s*$',
  555:             r'\b(?:the|a|an|their|its|our|your|this|that)\s*[\.\!\?]?\s*$',
  556:         ],
  ```
- **Golden Set Reference**:
  `data/golden_eval_set.json:1749-1762`:
  ```json
  {
    "id": "NEG-021",
    "text": "Out of total water resources...",
    "expected_label": "negative",
    "intent": "none",
    "rejection_category": "syntactic_fragment"
  }
  ```
- **Empirical Generalization Failure**:
  Running empirical counter-examples revealed that replacing `"water"` with unseen domain resources (`forest`, `mineral`, `land`) causes noise gating to fail:
  ```powershell
  python -c "from v13_discovery.semantic_extractor import NoiseFilterGate; print('forest:', NoiseFilterGate.audit('Out of total forest resources')); print('mineral:', NoiseFilterGate.audit('Out of total mineral resources')); print('land:', NoiseFilterGate.audit('Out of total land resources'))"
  ```
  Output:
  ```
  forest: None
  mineral: None
  land: None
  ```
  The gate returned `None` instead of `"syntactic_fragment"` because `"Out of total water resources"` was hardcoded literally.

---

### 1.2 Unanchored 5-Word Reading Order Bug in NoiseFilterGate (`semantic_extractor.py:569`)
- **Direct File Observation**:
  `v13_discovery/semantic_extractor.py:565-578`:
  ```python
  565:         "broken_reading_order": [
  566:             r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z][a-z]+',
  567:             r'[a-z]+[A-Z][a-z]+[A-Z][a-z]+',
  568:             r'^(?:[A-Z][a-zA-Z\s]{2,20}\s+){4,}[A-Z][a-zA-Z\s]{2,20}$',
  569:             r'\b(?:[A-Z][a-z]+\s+){5,}',
  570:             r'\b(?:Given|Written|Authored|Published|Proposed)\s+by\s+[A-Z]',
  571:             r'^\w[\w\s]*\s*:\s*$',
  572:             r'^\s*[A-Z\s]{25,}\s*$',
  573:             r'^[A-Z0-9\s]{20,}$',
  574:             r'\b[A-Z]\s+[A-Z]\s+[A-Z]\b',
  575:             r':\s*(?:Occurs|Is|Are|Was|Were|Has|Have)\b',
  576:             r'^(.{10,})\1$',
  577:         ]
  ```
- **Empirical False Rejection**:
  Line 569 `r'\b(?:[A-Z][a-z]+\s+){5,}'` is unanchored and contains no verb guards. Any legitimate sentence whose subject is a 5-token TitleCase proper noun matches this regex:
  ```powershell
  python -c "from v13_discovery.semantic_extractor import NoiseFilterGate; print(NoiseFilterGate.audit('The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point.'))"
  ```
  Output:
  ```
  broken_reading_order
  ```
  Other dropped educational entities:
  - `"The Indian Space Research Organisation is based in Bengaluru."` $\to$ `"broken_reading_order"`
  - `"The Great Barrier Reef Marine Park constitutes a protected zone."` $\to$ `"broken_reading_order"`
- **Diagnostic in Test Suite**:
  In `tests/test_v13_challenger_it4_stress.py:495-496`, the challenger previously recorded this limitation as an assertion of failure:
  ```python
  s_5_caps = "The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."
  self.assertEqual(NoiseFilterGate.audit(s_5_caps), "broken_reading_order")
  ```

---

### 1.3 Verbatim Hardcoded Headers in Normalizer (`normalizer.py:197-202`)
- **Direct File Observation**:
  `v13_discovery/normalizer.py:193-207`:
  ```python
  193:     @classmethod
  194:     def split_merged_headers(cls, line: str) -> str:
  195:         """Splits multi-column horizontal concatenations caused by multi-column PDF bounding boxes."""
  196:         s = line.strip()
  197:         s = re.sub(r'UniverseGalaxySolar System', 'Universe. Galaxy. Solar System.', s)
  198:         s = re.sub(r'Planetesimal TheoryNebular HypothesisCopernicus Theory', 'Planetesimal Theory. Nebular Hypothesis. Copernicus Theory.', s)
  199:         s = re.sub(r'MeteoroidMeteorMeteorite', 'Meteoroid. Meteor. Meteorite.', s)
  200:         s = re.sub(r'PhotosphereChromosphereCorona', 'Photosphere. Chromosphere. Corona.', s)
  201:         s = re.sub(r'Terrestrial PlanetsJovian Planets', 'Terrestrial Planets vs Jovian Planets.', s)
  202:         s = re.sub(r'Three Types of Plate BoundariesThree Types of Plate Boundaries', 'Three Types of Plate Boundaries:', s)
  203:         s = re.sub(r'(\d+\s*days?)(\d+\s*spin)', r'\1. \2', s)
  204:         s = re.sub(r'(\d+\s*days?)([A-Z][a-z]+)', r'\1. \2', s)
  205:         s = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', s)  # general camelCase splitting
  206:         return s
  ```
- **Root Cause of Hardcoding**:
  Line 205 attempted to split camelCase with `r'([a-z])([A-Z][a-z]+)'`. Because this regex consumes characters into Group 2 (`[A-Z][a-z]+`), overlapping boundaries in consecutive PascalCase words (e.g., `...eGalaxySolar...` where `Galaxy` is consumed) fail to match subsequently.
  Empirical proof:
  ```powershell
  python -c "import re; s = 'UniverseGalaxySolar System'; print(re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', s))"
  # Output: Universe GalaxySolar System (Galaxy and Solar did not split!)
  ```
  Because line 205 failed on consecutive words, the previous author hardcoded lines 197–202.

---

## 2. Logic Chain

### 2.1 Remediation of Prepositional Fragment Gate
1. **Premise 1**: Grammatical prepositional fragments lacking a main clause and verb (`"In addition to"`, `"As well as"`, `"Due to which"`, `"Out of total [domain] resources"`) represent OCR truncation artifacts (such as `NEG-021`).
2. **Premise 2**: Hardcoding `"Out of total water resources"` violates Check 1 (Anti-Overfitting) and fails on unseen domain variants (`forest resources`, `mineral resources`, `land resources`, `agricultural land`).
3. **Deductive Step**: Replacing the literal string with the generalized pattern:
   ```python
   r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$'
   ```
   recognizes any prepositional phrase starting with `"Out of"`, with optional `"the"` or `"total"`, followed by noun phrase tokens, bounded by line start and optional punctuation.
4. **Empirical Verification**:
   - `Out of total water resources` $\to$ `syntactic_fragment`
   - `Out of total forest resources` $\to$ `syntactic_fragment`
   - `Out of total mineral resources` $\to$ `syntactic_fragment`
   - `Out of total land resources` $\to$ `syntactic_fragment`
   - `Out of the total agricultural land` $\to$ `syntactic_fragment`
   - Full sentences containing verbs (e.g., `"Out of total water resources, only 3 percent is fresh."`) do NOT match because of the intermediate comma and digits.

---

### 2.2 Remediation of 5-Token Reading Order Gate
1. **Premise 1**: The noise category `"broken_reading_order"` is intended to reject unparsed multi-column header collisions and OCR artifacts where text is read horizontally across vertical columns without sentential grammar.
2. **Premise 2**: Proper noun entities in educational discourse frequently consist of 5 or more capitalized tokens (e.g. `"The James Webb Space Telescope"`, `"The Indian Space Research Organisation"`).
3. **Premise 3**: The unanchored pattern `r'\b(?:[A-Z][a-z]+\s+){5,}'` matches anywhere in a line, ignoring finite verbs and predicates that follow.
4. **Deductive Step**: Guarding the pattern with a negative lookahead for finite verbs (`is`, `are`, `was`, `were`, `has`, `have`, `had`, `orbits`, `contains`, `features`, `forms`, `emits`, `reaches`, `consists`, `includes`, `moves`) and anchoring to lines/clauses of capitalized tokens:
   ```python
   r'^(?![^.\n]*\b(?:is|are|was|were|has|have|had|orbits?|contains?|features?|forms?|emits?|reaches?|consists?|includes?|moves?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$'
   ```
   ensures that:
   - Valid sentences with 5-token subjects and standard predicates pass cleanly (`audit` returns `None`).
   - Smashed column headers consisting solely of TitleCase words without finite verbs (e.g., `"Cosmology Big Bang Theory Galaxy Steady State Theory"`) are accurately rejected as `"broken_reading_order"`.
5. **Empirical Verification**:
   - `JWST` sentence $\to$ `audit` returns `None` $\to$ extracts 1 `member_of` KnowledgeNode.
   - `ISRO` sentence $\to$ `audit` returns `None` $\to$ extracts 1 KnowledgeNode.
   - All 55 negative items in `data/golden_eval_set.json` remain 100% rejected (0 false acceptances).

---

### 2.3 Remediation of Merged Headers via Lookahead & Deduplication
1. **Premise 1**: Lines 197–202 in `v13_discovery/normalizer.py` hardcode 6 specific strings:
   - `UniverseGalaxySolar System` (NEG-030)
   - `Planetesimal TheoryNebular HypothesisCopernicus Theory` (NEG-031)
   - `MeteoroidMeteorMeteorite`
   - `PhotosphereChromosphereCorona`
   - `Terrestrial PlanetsJovian Planets`
   - `Three Types of Plate BoundariesThree Types of Plate Boundaries` (NEG-033)
2. **Premise 2**: Word collisions between camelCase/PascalCase tokens occur when a lowercase letter is immediately followed by an uppercase letter (`[a-z]` followed by `[A-Z]`).
3. **Premise 3**: Using a zero-width positive lookahead `([a-z])(?=[A-Z])` allows matching every single boundary without consuming the uppercase letter, splitting arbitrarily chained PascalCase words in a single pass:
   ```python
   re.sub(r'([a-z])(?=[A-Z])', r'\1 ', s)
   ```
4. **Premise 4**: Duplicated banners (e.g. `NEG-033`: `"Three Types of Plate BoundariesThree Types of Plate Boundaries"`) represent repeated multi-word strings. A generalized deduplication regex matches any repeated phrase of 6+ characters:
   ```python
   s = re.sub(r'^(.{6,}?)\s*\1\s*$', r'\1:', s)
   s = re.sub(r'\b([A-Z][a-zA-Z\s]{5,}?)\s+\1\b', r'\1', s)
   ```
5. **Deductive Step**: Replacing lines 197–205 with the zero-width lookahead boundary splitter and repeated phrase deduplicator completely eliminates all 6 hardcoded phrases while supporting unseen domains (`ContinentalDriftTheory`, `PlateTectonicsHypothesis`, `AtmosphericCirculationModel`).

---

## 3. Caveats

1. **Test Assertion Alignment (`test_v13_challenger_it4_stress.py`)**:
   In `tests/test_v13_challenger_it4_stress.py`, line 496 (`test_boundary_capitalized_words_noise_gate`) was written by the challenger to assert the presence of the 5-word reading order defect (`self.assertEqual(NoiseFilterGate.audit(s_5_caps), "broken_reading_order")`). Once the defect is fixed, `NoiseFilterGate.audit(s_5_caps)` correctly returns `None`. The worker must update this test line to `self.assertIsNone(NoiseFilterGate.audit(s_5_caps))` so that 405/405 tests pass.
2. **Ellipsis in Golden Set NEG-021**:
   In `data/golden_eval_set.json`, `NEG-021` contains trailing dots (`"Out of total water resources..."`). Even without the prepositional fragment pattern, lines 548–549 (`r'\.\.\.\s*$'`) match trailing ellipsis. The generalized prepositional fragment pattern guarantees rejection even when punctuation/ellipsis is omitted.
3. **Explorer Read-Only Boundary**:
   As an Explorer agent, no source files outside `.agents/teamwork_preview_explorer_m2_it5_2/` were modified. The complete machine-applicable patch is saved in `.agents/teamwork_preview_explorer_m2_it5_2/remediation.patch`.

---

## 4. Conclusion

All hardcoded phrases in `NoiseFilterGate` and `normalizer.py:split_merged_headers` have been identified, diagnosed, and replaced with mathematically sound, generalized linguistic patterns:

1. **NoiseFilterGate Prepositional Fragments**:
   - Purged: `"Out of total water resources"`
   - Replaced with: `r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$'`
2. **NoiseFilterGate Reading Order**:
   - Fixed unanchored `\b(?:[A-Z][a-z]+\s+){5,}`
   - Replaced with: `r'^(?![^.\n]*\b(?:is|are|was|were|has|have|had|orbits?|contains?|features?|forms?|emits?|reaches?|consists?|includes?|moves?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$'`
3. **Normalizer Header Splitting**:
   - Purged 6 verbatim strings: `UniverseGalaxySolar System`, `Planetesimal TheoryNebular HypothesisCopernicus Theory`, `MeteoroidMeteorMeteorite`, `PhotosphereChromosphereCorona`, `Terrestrial PlanetsJovian Planets`, `Three Types of Plate BoundariesThree Types of Plate Boundaries`.
   - Replaced with zero-width lookahead camelCase boundary splitter `r'([a-z])(?=[A-Z])'` and repeated phrase deduplication.

### Code Diff Specifications for Worker

#### Diff 1: `v13_discovery/semantic_extractor.py`
```diff
--- a/v13_discovery/semantic_extractor.py
+++ b/v13_discovery/semantic_extractor.py
@@ -547,7 +547,7 @@ class NoiseFilterGate:
             r'(?<!protects\s)(?<!protect\s)(?<!us\s)(?<!them\s)(?<!differ\s)(?<!originates\s)\bfrom\s*[\.\!\?]?\s*$',
             r'\.\.\.\s*$',
             r'\.{2,}\s*$',
-            r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$',
+            r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$',
             r'^\s*Because\s+(?:despite|although|though|if|when|while)\b',
             r'^\s*(?:While|When|Because|Although)\s+[a-z]+ing\b.*[\.\!\?]?\s*$',
             r'^\s*(?:In|At|On|From)\s+(?:Rural|Urban|Total|General|Primary|Secondary),\s+',
@@ -566,7 +566,7 @@ class NoiseFilterGate:
             r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z][a-z]+',
             r'[a-z]+[A-Z][a-z]+[A-Z][a-z]+',
             r'^(?:[A-Z][a-zA-Z\s]{2,20}\s+){4,}[A-Z][a-zA-Z\s]{2,20}$',
-            r'\b(?:[A-Z][a-z]+\s+){5,}',
+            r'^(?![^.\n]*\b(?:is|are|was|were|has|have|had|orbits?|contains?|features?|forms?|emits?|reaches?|consists?|includes?|moves?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$',
             r'\b(?:Given|Written|Authored|Published|Proposed)\s+by\s+[A-Z]',
             r'^\w[\w\s]*\s*:\s*$',
             r'^\s*[A-Z\s]{25,}\s*$',
```

#### Diff 2: `v13_discovery/normalizer.py`
```diff
--- a/v13_discovery/normalizer.py
+++ b/v13_discovery/normalizer.py
@@ -194,13 +194,14 @@ class LayoutDesegmenter:
     @classmethod
     def split_merged_headers(cls, line: str) -> str:
         """Splits multi-column horizontal concatenations caused by multi-column PDF bounding boxes."""
         s = line.strip()
-        s = re.sub(r'UniverseGalaxySolar System', 'Universe. Galaxy. Solar System.', s)
-        s = re.sub(r'Planetesimal TheoryNebular HypothesisCopernicus Theory', 'Planetesimal Theory. Nebular Hypothesis. Copernicus Theory.', s)
-        s = re.sub(r'MeteoroidMeteorMeteorite', 'Meteoroid. Meteor. Meteorite.', s)
-        s = re.sub(r'PhotosphereChromosphereCorona', 'Photosphere. Chromosphere. Corona.', s)
-        s = re.sub(r'Terrestrial PlanetsJovian Planets', 'Terrestrial Planets vs Jovian Planets.', s)
-        s = re.sub(r'Three Types of Plate BoundariesThree Types of Plate Boundaries', 'Three Types of Plate Boundaries:', s)
-        s = re.sub(r'(\d+\s*days?)(\d+\s*spin)', r'\1. \2', s)
-        s = re.sub(r'(\d+\s*days?)([A-Z][a-z]+)', r'\1. \2', s)
-        s = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1 \2', s)  # general camelCase splitting
+        # 1. Deduplicate immediately repeated verbatim phrases
+        s = re.sub(r'^(.{6,}?)\s*\1\s*$', r'\1:', s)
+        s = re.sub(r'\b([A-Z][a-zA-Z\s]{5,}?)\s+\1\b', r'\1', s)
+        # 2. Split concatenated numeric units and subsequent headers/values
+        s = re.sub(r'(\d+\s*[a-zA-Z]+)(?=\d+\s*[a-zA-Z])', r'\1. ', s)
+        s = re.sub(r'(\d+\s*[a-zA-Z]+)(?=[A-Z][a-z]+)', r'\1. ', s)
+        # 3. Generalized PascalCase / camelCase word boundary splitting using zero-width lookahead
+        s = re.sub(r'([a-z])(?=[A-Z])', r'\1 ', s)
+        # 4. Clean up any trailing repeated phrases after spacing
+        s = re.sub(r'^(.{6,}?)\s*:\s*\1\s*$', r'\1:', s)
+        s = re.sub(r'^(.{6,}?)\s+\1\s*$', r'\1:', s)
         return s
```

---

## 5. Verification Method

### 5.1 Verification Commands
To independently verify the generalizations and absence of hardcoded strings:

```powershell
# 1. Verify zero banned domain strings and zero hardcoded golden strings
python -c "
with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f:
    se = f.read()
with open('v13_discovery/normalizer.py', encoding='utf-8') as f:
    norm = f.read()

banned = [
    'Out of total water resources',
    'UniverseGalaxySolar System',
    'Planetesimal TheoryNebular HypothesisCopernicus Theory',
    'MeteoroidMeteorMeteorite',
    'PhotosphereChromosphereCorona',
    'Terrestrial PlanetsJovian Planets',
    'Three Types of Plate BoundariesThree Types of Plate Boundaries'
]

for b in banned:
    assert b not in se, f'Found {b} in semantic_extractor.py'
    assert b not in norm, f'Found {b} in normalizer.py'
print('ALL HARDCODED STRINGS 100% PURGED!')
"

# 2. Verify Syntactic Fragment Generalization (Forensic Auditor Experiment 3)
python -c "
from v13_discovery.semantic_extractor import NoiseFilterGate
variants = [
    'Out of total water resources',
    'Out of total forest resources',
    'Out of total mineral resources',
    'Out of total land resources',
    'Out of the total agricultural land'
]
for v in variants:
    audit = NoiseFilterGate.audit(v)
    assert audit == 'syntactic_fragment', f'Expected syntactic_fragment for {v}, got {audit}'
print('SYNTACTIC FRAGMENT GENERALIZATION PASSED!')
"

# 3. Verify 5-Token Educational Entity Recognition
python -c "
from v13_discovery.semantic_extractor import SemanticExtractor, NoiseFilterGate
s = 'The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point.'
assert NoiseFilterGate.audit(s) is None, f'NoiseFilterGate falsely rejected JWST: {NoiseFilterGate.audit(s)}'
nodes = SemanticExtractor().extract(s)
assert len(nodes) >= 1, 'Failed to extract JWST node'
print('5-TOKEN EDUCATIONAL ENTITY RECOGNITION PASSED! Node:', nodes[0].primary_entity)
"

# 4. Verify Merged Header Generalized Splitting
python -c "
from v13_discovery.normalizer import LayoutDesegmenter
cases = [
    ('UniverseGalaxySolar System', ['Universe', 'Galaxy', 'Solar System']),
    ('Planetesimal TheoryNebular HypothesisCopernicus Theory', ['Planetesimal Theory', 'Nebular Hypothesis', 'Copernicus Theory']),
    ('MeteoroidMeteorMeteorite', ['Meteoroid', 'Meteor', 'Meteorite']),
    ('PhotosphereChromosphereCorona', ['Photosphere', 'Chromosphere', 'Corona']),
    ('Terrestrial PlanetsJovian Planets', ['Terrestrial Planets', 'Jovian Planets']),
    ('Three Types of Plate BoundariesThree Types of Plate Boundaries', ['Three Types of Plate Boundaries:']),
    ('ContinentalDriftTheory', ['Continental', 'Drift', 'Theory']),
]
for raw, expected_parts in cases:
    split = LayoutDesegmenter.split_merged_headers(raw)
    for part in expected_parts:
        assert part in split, f'Expected {part} in {split}'
print('MERGED HEADERS GENERALIZATION PASSED!')
"

# 5. Full Unittest Suite Execution
python -m unittest discover -s tests -p "test_*.py"
```

### 5.2 Invalidation Conditions
- If any of the 7 banned strings are found in `v13_discovery/semantic_extractor.py` or `v13_discovery/normalizer.py`.
- If unseen domain variants (`Out of total forest resources`, `Out of total mineral resources`) return `None` instead of `syntactic_fragment`.
- If valid sentences with 5+ capitalized words in their subject (e.g. `"The James Webb Space Telescope is an optical space observatory..."`) return `"broken_reading_order"`.
- If `split_merged_headers` fails on concatenated PascalCase words.
