# Task Assignment: M1 Golden Eval Set Explorer

You are teamwork_preview_explorer_m1_1.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md

Objective:
Investigate and design the Golden Evaluation Dataset (`data/golden_eval_set.json`) containing:
1. At least 50 high-quality positive examples from the real corpus (`consolidated_grounding.md`, `geography_extracted.txt`, `geography_extracted_2.txt`, NCERT texts) spanning all 14 semantic intents required by R2:
   - definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of.
2. At least 50 realistic negative examples from the corpus that must be rejected:
   - MCQ option markers/leakage (e.g. `(a)`, `(b)`, `Sol.123`)
   - Watermarks / headers (`www.ssccglpinnacle.com`, `PARMAR SSC`, `ISBN...`)
   - Syntactic fragments & dangling conjunctions (`The Nile basin is huge and`, `Out of total water resources...`)
   - Multi-column reading order broken lines
   - Pure table formatting artifacts
   - Vague/anaphoric statements without referents (`They are made of...`)
3. Define the exact JSON schema for the evaluation set, with provenance fields (`source_file`, `line_or_page`, `intent`, `expected_label`: positive/negative).
4. Write your recommendations and report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1\handoff.md
5. Send a message to parent orchestrator upon completion.

## 2026-09-03T10:47:29Z
You are teamwork_preview_explorer_m1_1.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1
Read your instructions in: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1\DISPATCH.md
Also read ORIGINAL_REQUEST.md and PROJECT.md.
Investigate and design the Golden Evaluation Dataset (data/golden_eval_set.json) containing at least 50 positive real corpus examples spanning all 14 semantic intents and at least 50 negative real corpus examples.
Write your recommendations and report to: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m1_1\handoff.md
Send a completion message back to parent orchestrator.
