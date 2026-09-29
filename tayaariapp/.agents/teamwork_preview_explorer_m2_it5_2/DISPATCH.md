# Dispatch: Explorer 2 Milestone 2 Iteration 5 (explorer_m2_it5_2)

**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2`
**Parent Conversation ID**: `f2a26050-100d-4ce0-9c9c-ad53fd921d9e`
**Parent Orchestrator**: `teamwork_preview_orchestrator_3`

## Mandatory Reference Documents
1. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md` (Read first)
2. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_3\PROJECT.md`
3. Forensic Auditor Full Evidence Report: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it4_1\handoff.md` (READ IN FULL)
4. Reviewer 2 Handoff Report: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m2_it4_2\handoff.md`

## Full Forensic Audit Evidence (Do Not Omit or Circumvent)
The Forensic Auditor reported INTEGRITY VIOLATION with the following evidence:
- `v13_discovery/semantic_extractor.py:550`: Verbatim fragment `"Out of total water resources"` from `NEG-021` is hardcoded in `NoiseFilterGate`. Unseen variants (`Out of total forest resources`) bypass noise gating.
- `v13_discovery/normalizer.py:197-202`: Verbatim strings `"UniverseGalaxySolar System"` (from `NEG-030`), `"Planetesimal TheoryNebular HypothesisCopernicus Theory"` (from `NEG-031`), and `"Three Types of Plate BoundariesThree Types of Plate Boundaries"` (from `NEG-033`) are hardcoded in `split_merged_headers`.
- Reviewer 2 Finding: `NoiseFilterGate.NOISE_PATTERNS["broken_reading_order"]` contains `\b(?:[A-Z][a-z]+\s+){5,}` which causes false-rejection of 5-token educational entities (e.g. "The James Webb Space Telescope", "The Indian Space Research Organisation").

## Tasks
1. Read the full Forensic Auditor report in `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it4_1\handoff.md`.
2. Formulate generalized, drop-in replacement patterns in `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py`:
   - Purge `"Out of total water resources"` from `NoiseFilterGate`. Replace with generalized leading prepositional fragment pattern:
     `r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$'`
     Verify that NEG-021 and unseen domain variants (`Out of total forest resources`, `Out of total mineral resources`, `Out of total land resources`) are all rejected as `syntactic_fragment`.
   - Fix `NoiseFilterGate.NOISE_PATTERNS["broken_reading_order"]` so it does NOT match entities in valid sentences containing lowercase verbs and predicates. (e.g., ensure `"The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."` is NOT rejected as broken reading order).
   - Purge all hardcoded string replacements from `normalizer.py:split_merged_headers` (`UniverseGalaxySolar System`, `Planetesimal TheoryNebular HypothesisCopernicus Theory`, `MeteoroidMeteorMeteorite`, `PhotosphereChromosphereCorona`, `Terrestrial PlanetsJovian Planets`, `Three Types of Plate BoundariesThree Types of Plate Boundaries`). Replace with generalized PascalCase / camelCase word boundary splitters and deduplication of repeated phrases.
3. Provide exact drop-in code diffs, verification commands, and proof that no golden set phrases remain.
4. Write your handoff report to `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2\handoff.md` and call `send_message` to parent orchestrator.

## 2026-09-05T11:23:35Z
You are explorer_m2_it5_2 (Explorer 2 for Milestone 2 Iteration 5).
Your working directory is c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2.
Your task and instructions are detailed in:
c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2\DISPATCH.md

Read DISPATCH.md, ORIGINAL_REQUEST.md, PROJECT.md, and especially the Forensic Auditor Full Evidence Report at c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it4_1\handoff.md and Reviewer 2 handoff at c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_reviewer_m2_it4_2\handoff.md.

Formulate generalized replacement patterns to purge hardcoded phrases from NoiseFilterGate ('Out of total water resources') and normalizer.py split_merged_headers, and fix the 5-word reading order bug.
Write your handoff report to c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it5_2\handoff.md and call send_message back to parent orchestrator.
