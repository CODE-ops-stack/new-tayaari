# Empirical Challenger Report — Milestone 2 Iteration 3

**Challenger Agent**: `teamwork_preview_challenger_m2_it3_1`  
**Roles**: Critic, Specialist  
**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_it3_1`  
**Parent Orchestrator**: `teamwork_preview_orchestrator_2` (Conv ID: `e2c78cf0-a08b-4813-9278-2794b22a4aa2`)  
**Target Work Product**: Milestone 2 Iteration 3 Extractor (`v13_discovery/semantic_extractor.py`, `v13_discovery/normalizer.py`, `tests/test_v13_generalization.py`)  
**Verdict**: **REQUEST_CHANGES**  

---

## Executive Summary

The Challenger conducted an independent, adversarial empirical evaluation of the Milestone 2 Iteration 3 deliverables. While the worker successfully purged literal golden strings and implemented an effective **Pronoun Shield** that prevents ungrounded anaphor leakage (returning 0 nodes for isolated pronouns and properly resolving grounded multi-sentence discourse), comprehensive stress-testing against novel, unseen sentences across all 14 intents revealed **eight (8) severe systemic defects and intent collapse failure modes**.

Crucially:
1. **Auditor Experiment B (Superlatives)** collapses into **0 nodes (`None`)** for any sentence using past-tense verbs (`had`, `exhibited`, `possessed`, `displayed`), because past-tense verbs were omitted from Pattern 14 (`attribute`) and declarative fallback.
2. **Auditor Experiment C (`member-of`)** only works for a hardcoded closed whitelist of 17 physical geography nouns (`star|port|satellite|planet|asteroid|comet|constellation|galaxy|volcano|mountain|range|island|river|sea|basin|plateau|glacier`). Any sentence with general educational category nouns (such as `moon`, `forest`, `mammal`, `desert`, `ocean`, `observatory`, `reef`) silently collapses into `definition`.
3. **Comparison intent** collapses into `definition` whenever a comparative sentence contains a trailing explanatory clause or participle set off by a comma (e.g., `, averaging...`, `, forming...`), due to a brittle `(?:\.|$)` regex termination.
4. **Attribute intent** collapses into `definition` on natural participial clauses (e.g., `, emitting...`), because post-comma clauses are hardcoded to require `(?:,\s*(?:are|is|have|has|possess))`.
5. **Quantity intent** truncates numbers with thousands commas (`40,075 kilometres` -> `40.0`).
6. **Sequence intent** with colons fails to extract `secondary_entities`, which remains empty `[]` because line 503 strips the colon before `pred`, causing `if ":" in pred:` at line 694 to always evaluate to `False`.
7. **Passive voice definition** contains a hardcoded shortcut specifically targeting `POS-001` (`if "all those" in desc`), causing all general passive definitions (`[desc] is called [term]`) to invert improperly, setting the entire multi-word description clause as `primary_entity` and generating an ungrammatical predicate (`are photosynthesis`).
8. **Part-of intent** collapses into `attribute` when spatial prepositions other than `of|within|in` (such as `located immediately beneath...`) are used.

Because these failure modes break generalization on expository educational text, the deliverable cannot be approved. The verdict is **REQUEST_CHANGES**.

---

## 1. Observation

### 1.1 Direct Empirical Defect Observations

#### Observation 1: Past-Tense Superlatives Collapse to `None` (0 nodes)
- **File**: `v13_discovery/semantic_extractor.py:563`
  ```python
  # Pattern 14: ATTRIBUTE
  r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:has|have|exhibits?|possesses?|displays?)\s+(?:the\s+)?(?:highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)\s+(?:[a-z\-]+\s+)*[a-z]+(?:\s+among|\s+in|\s+at|\s+of\b|\s*,).*)$'
  ```
- **File**: `v13_discovery/semantic_extractor.py:736`
  ```python
  match_decl = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|has|have|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises|falls)\s+(?P<rest>.*)', working_text, re.IGNORECASE)
  ```
- **Empirical Test**:
  ```python
  from v13_discovery.semantic_extractor import SemanticExtractor
  se = SemanticExtractor()
  print(se.extract("The Chelyabinsk meteor had the strongest recorded atmospheric shockwave among recent bolides."))
  # Result: [] (0 nodes)
  print(se.extract("The prehistoric Megalodon had the largest bite force among all known apex predators."))
  # Result: [] (0 nodes)
  ```
- **Error**: Both pattern 14 and declarative fallback omit `had`, `exhibited`, `possessed`, and `displayed`. Historical/prehistoric superlative statements fail extraction entirely.

#### Observation 2: Closed 17-Noun Whitelist in `member-of` Causing Intent Collapse to `definition`
- **File**: `v13_discovery/semantic_extractor.py:550-553`
  ```python
  ("member-of", re.compile(
      r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+is an?\s+(?:[a-z\-]+\s+)*(?:star|port|satellite|planet|asteroid|comet|constellation|galaxy|volcano|mountain|range|island|river|sea|basin|plateau|glacier)\s+(?P<pred>(?:situated|located|commissioned|established|operating|orbiting|found)\b.*)$',
      re.IGNORECASE
  )),
  ```
- **Empirical Test**:
  ```python
  s1 = "Titan is a massive icy moon orbiting Saturn within the outer Solar System."
  s2 = "The Sundarbans is an expansive tidal halophytic mangrove forest situated in the delta of the Ganga and Brahmaputra rivers."
  s3 = "The cheetah is a carnivorous feline mammal found in sub-Saharan Africa."
  s4 = "The Sahara is an expansive subtropical desert located in northern Africa."
  print(se.extract(s1)[0].intent_type) # Result: 'definition'
  print(se.extract(s2)[0].intent_type) # Result: 'definition'
  print(se.extract(s3)[0].intent_type) # Result: 'definition'
  print(se.extract(s4)[0].intent_type) # Result: 'definition'
  ```
- **Error**: While literal strings `'yellow dwarf'` and `'satellite container port'` were removed, they were replaced by a closed whitelist of 17 physical geography nouns (`star|port|satellite|planet...`). Educational sentences with nouns outside this whitelist (`moon`, `forest`, `mammal`, `desert`, `observatory`, `ocean`, `strait`, `canyon`, `reef`) fail Pattern 12 and collapse into generic `definition`.

#### Observation 3: Brittle Lookahead `(?:\.|$)` in `comparison` Collapsing to `definition` on Trailing Clauses
- **File**: `v13_discovery/semantic_extractor.py:473-480`
  ```python
  ("comparison", re.compile(
      r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?[a-z\-]+er(?:-[a-z]+)?\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:\.|$).*)$',
      re.IGNORECASE
  )),
  ```
- **Empirical Test**:
  ```python
  s1 = "Continental crust is much thicker than oceanic crust, averaging 35 kilometres compared to 7 kilometres beneath oceans."
  s2 = "Venus is much hotter than Mercury, despite being farther from the Sun."
  print(se.extract(s1)[0].intent_type) # Result: 'definition'
  print(se.extract(s2)[0].intent_type) # Result: 'definition'
  ```
- **Error**: The regex forces `(?:\.|$)` directly after `(?P<sec>...)`. A comma `, averaging...` or `, despite...` fails the pattern, falling through to declarative fallback where verb `is` assigns `definition`.

#### Observation 4: Compound Attribute Inflexibility Collapsing to `definition` on Participle Clauses
- **File**: `v13_discovery/semantic_extractor.py:579-581`
  ```python
  ("attribute", re.compile(
      r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:are|is)\s+(?:very|extremely|highly|mostly)?\s*[a-z\-]+\s+and\s+[a-z\-]+(?:,\s*(?:are|is|have|has|possess)\b.*)?)$',
      re.IGNORECASE
  )),
  ```
- **Empirical Test**:
  ```python
  s = "Stars in open clusters are extremely young and hot, emitting intense ultraviolet radiation into interstellar gas."
  print(se.extract(s)[0].intent_type) # Result: 'definition'
  ```
- **Error**: The pattern strictly requires post-comma verbs to be `are|is|have|has|possess`. Natural participial clauses (`, emitting...`, `, cooling...`, `, relying on...`) fail this pattern and fall through to declarative `definition`.

#### Observation 5: Number Formatting Truncation on Thousands Commas
- **File**: `v13_discovery/semantic_extractor.py:686-688`
  ```python
  m_num = re.search(r'(\d+(?:\.\d+)?)\s*(percent|%|degrees|kilometres|km|mb|meters|g/cm\^3|°C)?', pred or clean_text)
  ```
- **Empirical Test**:
  ```python
  s = "The equatorial circumference of the Earth measures approximately 40,075 kilometres."
  n = se.extract(s)[0]
  print(n.quantitative_data) # Result: {'value': 40.0, 'unit': ''}
  ```
- **Error**: `\d+(?:\.\d+)?` does not handle commas. `40,075 kilometres` is truncated to `40.0` with empty unit `""`.

#### Observation 6: Sequence Intent Secondary Entities Empty on Colons
- **File**: `v13_discovery/semantic_extractor.py:503` and `694`
  ```python
  # Line 503 (Regex strips colon before capturing pred):
  r'...progresses through\s+(?:a\s+)?(?:[a-z\-]+\s+)*(?:sequence|stages|phases|steps|cycle)...:\s*:?\s*(?P<pred>.*)$'
  # Line 694:
  if intent == "sequence" and ":" in pred:
      stages = [s.strip() for s in re.split(r'[,;]|\band\b', pred.split(":", 1)[1]) if s.strip()]
      sec.extend(stages)
  ```
- **Empirical Test**:
  ```python
  s = "Volcanic caldera formation progresses through a distinct sequence: rapid magma chamber evacuation, structural roof collapse, and secondary resurgent dome uplift."
  n = se.extract(s)[0]
  print("secondary_entities:", n.secondary_entities) # Result: []
  ```
- **Error**: Because line 503 consumes the colon before `(?P<pred>.*)`, `":" in pred` is always False. Sequence stages are never parsed into `secondary_entities`.

#### Observation 7: Passive Voice Definition Hack Targeting `POS-001`
- **File**: `v13_discovery/semantic_extractor.py:630-644`
  ```python
  m_pass = cls.PASSIVE_DEF_REGEX.match(clean_text)
  if m_pass:
      term = m_pass.group("term").strip().rstrip('.')
      desc = m_pass.group("desc").strip()
      if re.search(r'\b(?:all\s+those|those\s+objects|all\s+such)\b', desc, re.IGNORECASE):
          primary_entity = term
          predicate = f"are {desc}"
          secondary = [desc]
      else:
          m_proper = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)([A-Za-z0-9\s\-]+)$', desc)
          primary_entity = m_proper.group(1).strip() if m_proper else desc
          predicate = f"are known as {term}" if "known as" in clean_text.lower() else f"are {term}"
          secondary = [term]
  ```
- **Empirical Test**:
  ```python
  s = "The process by which plants convert light energy into chemical energy is called photosynthesis."
  n = se.extract(s)[0]
  print("Primary Entity:", n.primary_entity) # Result: 'process by which plants convert light energy into chemical energy'
  print("Predicate:", n.predicate)           # Result: 'are photosynthesis'
  ```
- **Error**: The inversion condition `re.search(r'\b(?:all\s+those|those\s+objects|all\s+such)\b', desc)` was tailored specifically to pass `POS-001` ("and all those objects shining in the night sky are called celestial bodies"). For standard passive definitions, it sets the descriptive relative clause as `primary_entity` and produces broken predicates like `"are photosynthesis"`.

#### Observation 8: Spatial Preposition Rigidity in `part-of`
- **File**: `v13_discovery/semantic_extractor.py:541`
  ```python
  (?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion)\s+(?:(?:located|situated|found)\s+)?(?:of|within|in)\b
  ```
- **Empirical Test**:
  ```python
  s = "The asthenosphere constitutes the ductile upper mantle portion located immediately beneath the rigid lithospheric plates."
  print(se.extract(s)[0].intent_type) # Result: 'attribute'
  ```
- **Error**: Requiring `of|within|in` causes statements with `located immediately beneath...` to fail `part-of` and fall back to `attribute` via verb `constitutes`.

---

### 1.2 Verbatim Challenger Test Suite Execution Log

The Challenger created and executed an empirical stress harness (`tests/test_v13_challenger_stress.py`) containing 23 tests:

```powershell
python -m unittest -v tests/test_v13_challenger_stress.py
```

**Execution Output**:
```
test_01_definition_defect_passive_inversion_hack (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_01_definition_defect_passive_inversion_hack)
Definition Defect: In passive definitions '[desc] is called [term]', line 635 only ... ok
test_02_attribute_defect_participle_collapse (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_02_attribute_defect_participle_collapse)
Attribute Defect: Sentences with compound adjectives followed by participle clauses ... ok
test_03_cause_effect_complex_clauses (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_03_cause_effect_complex_clauses) ... ok
test_04_comparison_defect_comma_qualifier_collapse (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_04_comparison_defect_comma_qualifier_collapse)
Comparison Defect: Comparative clauses followed by comma qualifiers collapse to ... ok
test_05_spatial_locative_inversion (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_05_spatial_locative_inversion) ... ok
test_06_distribution_percentages (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_06_distribution_percentages) ... ok
test_07_classification_subclasses (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_07_classification_subclasses) ... ok
test_08_quantity_defect_formatted_numbers_with_commas (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_08_quantity_defect_formatted_numbers_with_commas)
Quantity Defect: Numbers containing commas like '40,075 kilometres' truncate to '40' ... ok
test_09_sequence_defect_colon_secondary_entities_empty (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_09_sequence_defect_colon_secondary_entities_empty)
Sequence Defect: Line 503 strips the colon before pred, causing ':' in pred at line 694 ... ok
test_10_condition_physical_thresholds (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_10_condition_physical_thresholds) ... ok
test_11_exception_contrastive_clauses (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_11_exception_contrastive_clauses) ... ok
test_12_process_biogeochemical_conversions (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_12_process_biogeochemical_conversions) ... ok
test_13_part_of_defect_spatial_preposition_collapse (tests.test_v13_challenger_stress.TestChallenger14IntentsStress.test_13_part_of_defect_spatial_preposition_collapse)
Part-of Defect: Line 541 mandates of|within|in. Describing components with spatial prepositions ... ok
test_exp_a_novel_kinematic_wave_attributes (tests.test_v13_challenger_stress.TestChallengerAuditorExperiments.test_exp_a_novel_kinematic_wave_attributes)
Exp A: Kinematic wave/oscillation attribute sentences with novel vocabulary. ... ok
test_exp_b_defect_past_tense_superlative_collapses_to_none (tests.test_v13_challenger_stress.TestChallengerAuditorExperiments.test_exp_b_defect_past_tense_superlative_collapses_to_none)
Exp B Defect: Past-tense superlative assertions ('had', 'exhibited', 'possessed') ... ok
test_exp_b_present_tense_superlative_attributes (tests.test_v13_challenger_stress.TestChallengerAuditorExperiments.test_exp_b_present_tense_superlative_attributes)
Exp B: Present-tense superlative properties across multiple domains. ... ok
test_exp_c_defect_non_whitelisted_member_of_collapses_to_definition (tests.test_v13_challenger_stress.TestChallengerAuditorExperiments.test_exp_c_defect_non_whitelisted_member_of_collapses_to_definition)
Exp C Defect: Member-of statements with standard educational nouns outside the 17-word ... ok
test_exp_c_whitelisted_member_of (tests.test_v13_challenger_stress.TestChallengerAuditorExperiments.test_exp_c_whitelisted_member_of)
Exp C: Member-of classifications where noun is in the 17-word whitelist. ... ok
test_no_hardcoded_golden_strings_in_extractor (tests.test_v13_challenger_stress.TestChallengerIntegrityAntiOverfitting.test_no_hardcoded_golden_strings_in_extractor) ... ok
test_block_without_antecedent_starting_with_pronoun_returns_zero_nodes (tests.test_v13_challenger_stress.TestChallengerPronounAndAnaphora.test_block_without_antecedent_starting_with_pronoun_returns_zero_nodes) ... ok
test_demonstrative_determiner_vs_bare_pronoun (tests.test_v13_challenger_stress.TestChallengerPronounAndAnaphora.test_demonstrative_determiner_vs_bare_pronoun) ... ok
test_grounded_discourse_resolves_pronoun_correctly (tests.test_v13_challenger_stress.TestChallengerPronounAndAnaphora.test_grounded_discourse_resolves_pronoun_correctly) ... ok
test_ungrounded_isolated_bare_pronouns_return_zero_nodes (tests.test_v13_challenger_stress.TestChallengerPronounAndAnaphora.test_ungrounded_isolated_bare_pronouns_return_zero_nodes)
Personal and demonstrative bare pronouns MUST return 0 nodes in isolation. ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.045s

OK
```

---

## 2. Logic Chain

1. **Premise 1 (Generalization Mandate)**:
   - The original request (§R2) and dispatch explicitly mandate a robust semantic parser mapping text to 14 explicit semantic intents that generalizes beyond simple templates and does not collapse into definition or None when tested on novel educational vocabulary.
2. **Premise 2 (Empirical Defect Findings)**:
   - As demonstrated in Section 1.1 (Observations 1 & 2), Auditor Experiments B and C still exhibit failure modes on unseen sentences:
     * Past-tense superlative assertions return 0 nodes.
     * Category classifications outside the 17-word whitelist collapse into `definition`.
   - As demonstrated in Section 1.1 (Observations 3 through 8), six additional structural defects exist in `comparison`, `attribute`, `quantity`, `sequence`, `definition`, and `part-of`.
3. **Premise 3 (Integrity & Quality Standard)**:
   - Replacing hardcoded golden set phrases with closed noun whitelists (`star|port|satellite|...`) and brittle single-case hacks (`if 'all those' in desc`) violates true grammatical generalization.
4. **Conclusion**:
   - Because the extractor fails to generalize across general expository syntax on novel unseen sentences, the deliverable must be returned to the worker for systemic repair.
   - The authoritative verdict is **REQUEST_CHANGES**.

---

## 3. Caveats

1. **Successful Improvements Acknowledged**:
   - The worker successfully purged all verbatim golden set phrases flagged in M2 It2.
   - The **Pronoun Shield** and **DiscourseContext** coreference implementation is genuine and robust:
     * Bare pronouns (`It`, `They`, `These`, `Those`, `He`, `She`, `This`, `That`) return 0 nodes in isolation.
     * Possessive pronouns (`Its`, `Their`, `His`, `Her`) return 0 nodes in isolation.
     * Unresolved pronoun blocks return 0 nodes.
     * Multi-sentence discourse blocks correctly resolve anaphora to singular and plural antecedents.
   - Kinematic wave attributes (Exp A) generalize successfully for present-tense vibrations, oscillations, and radiations.
2. **Review-Only Constraint**:
   - In accordance with Challenger constraints, no implementation files (`v13_discovery/`) were modified by the Challenger. All evidence was generated through external dynamic test execution.

---

## 4. Conclusion & Required Remediations

The work product delivered for Milestone 2 Iteration 3 requires revision before Milestone 2 can be closed.

**Verdict**: **REQUEST_CHANGES**

### Actionable Remediations for Worker (Iteration 4)

1. **Fix Past-Tense Superlatives (Exp B)**:
   - In `v13_discovery/semantic_extractor.py:563` (Pattern 14) and line 736 (declarative fallback), add past-tense verbs:
     `r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed)\s+...'`
   - In line 736, add `had|was|were` to declarative verbs.

2. **Generalize `member-of` Beyond 17-Noun Whitelist (Exp C)**:
   - In line 551, replace the closed 17-noun whitelist with a generalized taxonomic noun phrase match:
     `r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+is an?\s+(?:[a-z\-]+\s+)*(?P<tax_class>[a-z\-]+)\s+(?P<pred>(?:situated|located|commissioned|established|operating|orbiting|found|inhabiting|dwelling|endemic)\b.*)$'`
   - Ensure categories like `moon`, `forest`, `mammal`, `desert`, `ocean`, `reef`, `observatory`, `organism` extract as `member_of`.

3. **Allow Trailing Clauses in `comparison`**:
   - In lines 473 and 477, change `(?:\.|$)` to allow comma-delimited explanatory clauses: `(?:[,;]|\.|$).*` so that `, averaging...` or `, despite...` does not break the match.

4. **Allow Participial Clauses in Compound Attributes**:
   - In line 579, update the post-comma pattern to accept participial modifiers:
     `(?:,\s*(?:(?:are|is|have|has|possess)\b|[a-z]+ing\b).*)*$`

5. **Fix Thousands Separator Parsing in Quantitative Extraction**:
   - In line 686, update regex:
     `r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(percent|%|degrees|kilometres|km|mb|meters|g/cm\^3|°C)?'`
   - Strip commas before casting to `float(clean_val.replace(',', ''))`.

6. **Fix Sequence Colon Secondary Entity Extraction**:
   - In line 694, check for colons in either `clean_text` or preserve colon in `pred` so that `sequence: step 1, step 2, step 3` populates `secondary_entities`.

7. **Fix Passive Voice Definition Inversion**:
   - In lines 630-644, generalize passive voice definitions so that for ANY sentence `[desc] is/are called|known as [term]`, if `term` is a short noun phrase (<= 4 words) and `desc` is a longer relative clause, `primary_entity = term` and `predicate = f"is/are {desc}"`.

8. **Broaden Spatial Prepositions in `part-of`**:
   - In line 541, expand prepositions: `(?:of|within|in|beneath|under|underneath|above|between)\b`.

---

## 5. Verification Method

To independently reproduce all findings and empirical defect logs:

```powershell
# 1. Run the Challenger Empirical Stress Harness (23 tests documenting all findings)
python -m unittest -v tests/test_v13_challenger_stress.py

# 2. Inspect zero banned golden set phrases in semantic_extractor.py (PASSED)
python -c "banned = ['longitudinal compressional', 'lowest mean density', 'very big and hot', 'comprises immense reserves', 'yellow dwarf', 'satellite container port', 'nearly all planets in', 'denudational process in which', 'tectonic process of', 'plunges beneath', 'transported and deposited by', 'geologists|scientists|geographers|plate tectonics']; src = open('v13_discovery/semantic_extractor.py', encoding='utf-8').read().lower(); violations = [b for b in banned if b in src]; print('Violations:', violations)"

# 3. Verify Pronoun Shielding (PASSED: 0 nodes for ungrounded pronouns)
python -c "from v13_discovery.semantic_extractor import SemanticExtractor; se = SemanticExtractor(); ungrounded = ['It is characterized by extreme aridity.', 'They are distributed across the taiga.', 'These are classified into three types.']; print('All 0 nodes:', all(len(se.extract(s)) == 0 for s in ungrounded))"
```

**Invalidation Conditions**:
- If a future iteration addresses Remediations 1 through 8 such that novel unseen sentences across all 14 intents (including past-tense superlatives, general taxonomies, trailing comparative clauses, participial attributes, comma-formatted numbers, and passive definitions) extract to their intended canonical intents without collapsing to `definition` or `None`.
