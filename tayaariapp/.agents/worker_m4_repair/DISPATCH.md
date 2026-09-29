## 2026-09-06T17:10:00Z
You are worker_m4_repair.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\worker_m4_repair\

Read authoritative requirements and context:
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_5\PROJECT.md
- c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\challenger_m4_1\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Task:
Implement the 5 targeted adversarial fixes identified by challenger_m4_1 in `v13_discovery/question_synthesizer.py`:

1. Enforce Gate Filtering in `synthesize()` and `synthesize_from_corpus()`:
   - In `QuestionSynthesizer.synthesize()`: When `DistractorVerificationGate.verify_all()` returns `is_valid=False`, attempt targeted entity de-identification on the stem. If violations persist, do NOT silently emit leaking/defective questions. Provide a `valid: bool = True` field or attribute on `CandidateQuestion` and set `valid = is_valid` (or return None / raise if strictly required).
   - In `synthesize_from_corpus()`: Strictly discard/filter questions that fail the 5-point verification gate. Continue extracting and synthesizing from candidate nodes until `min_questions` (100) strictly valid, gate-passing questions are generated. Ensure 0% stem leakage across the 100 generated questions!
2. Harden Stem-Terminal Indefinite Article Detection:
   - In `DistractorVerificationGate.check_grammatical_fit()`: Replace `r'\b(?:is|as|called|termed)\s+(?:a|an)$'` with `r'\b(?:a|an)$'` so any stem ending in an indefinite article is rejected regardless of preceding verb.
3. Close Short-Entity Stem Leakage Blind Spot:
   - In `DistractorVerificationGate.check_absence_of_clueing()`: Change `len(correct_text) > 3` to `len(correct_text) >= 3` with regex word-boundary matching `r'\b' + re.escape(correct_text) + r'\b'`, ensuring 3-letter concepts ("Fog", "Ice", "Sun", "Ore") are caught if leaking in stem.
4. Expand Placeholder Regex:
   - In `DistractorVerificationGate.check_semantic_plausibility()`: Update placeholder regex to match:
     `r'^(?:Alternative\s+[0-9A-Za-z]+|Option\s+[0-9A-Za-z]+|Choice\s+[0-9A-Za-z]+|None\b|TBD|Placeholder|Unknown|N/A|NA|All of the above|None of the above)\b'`
5. Deduplicate `OntologyRegistry` Category Memberships:
   - Remove `Hadley cell` from `climatic_phenomena` (retaining it in `circulation_cells`). Clean cross-category member collisions so each entity maps to its primary taxonomic domain.

Verification Commands:
- `python -m unittest tests/test_v13_distractor_engine.py`
- `python .agents/challenger_m4_1/test_adversarial_m4.py`
- `python -m unittest discover -s tests -p "test_*.py"`
- `python run_e2e_tests.py`
- Test corpus generation and verify 0% stem leakage: run a test script generating 100 questions from `source-material/geography_extracted.txt` and verifying all 100 pass `DistractorVerificationGate.verify_all()`.

Write your full handoff report to `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\worker_m4_repair\handoff.md` and send a message when complete.
