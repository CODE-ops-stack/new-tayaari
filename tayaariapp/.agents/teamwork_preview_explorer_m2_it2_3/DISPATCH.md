# Task Assignment: M2 It2 Normalizer Boundary & Noise Gate Explorer

You are teamwork_preview_explorer_m2_it2_3.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_3
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Gate status: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\GATE_STATUS.md
Challenger 2 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_2_rep\handoff.md
Reviewer 1 handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m2_1_rep\handoff.md

Objective:
Investigate and design fixes for `NoiseFilterGate` in `v13_discovery/semantic_extractor.py` and boundary conditions in `v13_discovery/normalizer.py`:
1. `NoiseFilterGate` refinement:
   - Allow valid concise factual sentences with >= 3 words (e.g., `"Lava is molten rock."`, `"Basalt is volcanic rock."`).
   - Fix false rejection of valid sentences ending in phrasal prepositions (e.g. `"...what continents are made of."`).
   - Reject bracketed MCQ markers (e.g. `[A]`, `(i)`, `(ii)`) cleanly so they do not leak into `KnowledgeNode.primary_entity`.
2. `TableParser` & `LayoutDesegmenter` refinement:
   - Handle Pandoc alignment rows containing `:::` (`| ::: | ::: |`).
   - In `should_stitch_lines`, handle abbreviations (`Dr.`, `Prof.`, `e.g.`) followed by uppercase names so sentences are not fractured.
   - In `stitch_lines`, preserve numerical ranges (`5000-\n6000` -> `5000-6000`) and insert spaces on punctuation dash joins (`two groups-\nterrestrial` -> `two groups - terrestrial`).
3. Write your recommendations and handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_3\handoff.md
4. Send completion message back to parent orchestrator.

## 2026-09-04T15:42:35Z
You are teamwork_preview_explorer_m2_it2_3.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it2_3
Read DISPATCH.md, GATE_STATUS.md, Challenger 2 handoff, and Reviewer 1 handoff.
Design NoiseFilterGate refinements (concise facts, phrasal prepositions, MCQ brackets) and normalizer boundary repairs (Pandoc tables, abbreviation line wraps, dash joins).
Write handoff.md and send completion message to parent orchestrator.
