# Progress - worker_m5_remediate

- Last visited: 2026-09-08T15:21:05Z
- Status: Completed hardcoded string removal and hardened AdversarialAuditor and QuestionRepairEngine. Running test discovery suite across repository.
- Changes made:
  1. Complete removal of hardcoded entity-specific checks and canned strings in `QuestionRepairEngine.repair` (`v13_discovery/auditors.py`).
  2. Replaced with 100% generalized algorithmic repair using entity's resolved category `cat_name`, clause extraction, de-identification, and evidence context.
  3. Dynamic fallback for `correct_val` avoiding hardcoded "Basalt".
  4. Hardened `AdversarialAuditor.audit`:
     - Empty/Whitespace Options: flags `not text.strip()` or `len(text.strip()) < 2` as FATAL `OPTION_COUNT`.
     - Short Entity Leakage: checks leakage for entities with `len(correct_val) >= 3` using word boundaries.
     - Distractor Alias Collisions: flags pairs of distractors that share canonical entity or are aliases as FATAL `SEMANTIC_AMBIGUITY`.
  5. Hardened `QuestionRepairEngine.repair`:
     - Option deduplication: draws siblings with strict distinctness check; if <3 siblings, draws from fallback ontology categories or domain entities.
     - Quotation frame stripping: strips punctuation before formatting, post-cleans double punctuation (`??`, `:?`), guaranteeing clean single `?`.
  6. Added 6 new unit tests to `tests/test_v13_multi_agent_auditor.py` covering empty options, short entity leakage, distractor alias collisions, low-cardinality sibling deduplication, rock domain coherence preservation, and quotation template punctuation.
