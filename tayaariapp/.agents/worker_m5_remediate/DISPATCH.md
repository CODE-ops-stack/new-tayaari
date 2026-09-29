## 2026-09-08T15:14:07Z

You are worker_m5_remediate.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\worker_m5_remediate\

Read authoritative requirements and context:
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md (§R4, Acceptance 3, 4)
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_5\PROJECT.md
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\reviewer_m5_1\handoff.md
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\reviewer_m5_2\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Tasks:
Remediate the integrity violations and adversarial vulnerabilities identified by Reviewer 1 and Reviewer 2 in `v13_discovery/auditors.py`:

1. COMPLETE REMOVAL OF HARDCODED STRINGS (INTEGRITY FIX):
   - In `v13_discovery/auditors.py` lines 588-625: Remove ALL hardcoded entity-specific checks and canned sentences (e.g. `if "granite" in correct_val.lower(): ...`, `elif "oxbow" in correct_val.lower(): ...`, `elif "earth" in repaired_stem.lower(): ...`).
   - Replace with 100% generalized algorithmic repair using the entity's resolved category `cat_name`, de-identification, and evidence context. For example:
     - For trivial stems or leakage: elevate using the resolved category hypernym and evidence, e.g.:
       `repaired_stem = f"With reference to {cat_name.lower()}, which of the following is characterized by the described physical properties and formation processes?"`
       or extract key descriptive phrases from `cq.explanation` / `cq.provenance.get("evidenceText")`.
     - Ensure NO specific entity names (like "granite", "oxbow", "basalt", "earth") are hardcoded anywhere in the repair logic.

2. HARDEN `AdversarialAuditor`:
   - Empty/Whitespace Options: Ensure that any option with `not text.strip()` or `len(text.strip()) < 2` triggers a FATAL violation (`"Option '{letter}' is empty or whitespace"`).
   - Short Entity Leakage: Check leakage for entities with `len(correct_val) >= 3` using regex word boundaries `r'\b' + re.escape(correct_val.lower()) + r'\b'`.
   - Distractor Alias Collisions: Check if any two distinct distractor options are aliases of each other or share the same canonical entity in `OntologyRegistry`, triggering a FATAL violation if found.

3. HARDEN `QuestionRepairEngine`:
   - Option deduplication: When drawing siblings for option repair, ensure that options are strictly unique. If a category has fewer than 3 siblings, draw from fallback domain physical entities without duplicating any existing option.
   - Quotation frame stripping: ensure stripping quotation templates does not leave double punctuation like `??` or trailing colons/whitespace.

4. Run all verification commands:
   - `python -m unittest tests/test_v13_multi_agent_auditor.py`
   - `python -m unittest tests/test_v13_distractor_engine.py`
   - `python -m unittest discover -s tests -p "test_*.py"`
   - `python run_e2e_tests.py`
   - Verify that `test_scale_generation_and_regeneration_cycle` executes cleanly with 100% generalized repairs and zero hardcoded strings!

Document all changes and test outputs in `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\worker_m5_remediate\handoff.md`. Send completion message when finished.
