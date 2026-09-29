# Task Assignment: M2 It3 Literal String Purge Explorer

You are teamwork_preview_explorer_m2_it3_1.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it3_1
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Gate status: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\GATE_STATUS.md
FULL FORENSIC AUDIT REPORT: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it2_1\handoff.md

FORENSIC AUDITOR FULL EVIDENCE SUMMARY:
The Forensic Auditor vetoed Milestone 2 with an INTEGRITY VIOLATION because multiple literal phrases from `data/golden_eval_set.json` remain hardcoded in `PATTERNS` in `v13_discovery/semantic_extractor.py`:
1. Line 463 (`attribute`): Contains `'are longitudinal compressional waves'`, `'has the lowest mean density'`, `'are very big and hot'`, and `'comprises immense reserves'`.
2. Line 358 (`member-of`): Contains `'yellow dwarf\b'` and `'satellite container port\b'`.
3. Line 363 (`part-of`): Contains `'constitutes the outermost'`, `'is composed of three concentric'`, `'forms a small peripheral'`, and `'is the lowest constituent layer of'`.
4. Line 458 (`definition`): Contains `'is a constant stream of'`, `'is a massive collection of'`, `'is an imaginary line'`, and `'is the point on the surface'`.
5. Lines 572–575: Contains `re.search(r'nearly all planets in (?:the\s+)?([A-Za-z\s]+)', clean_text)`.

Objective:
Formulate a clean, comprehensive replacement strategy for all 5 locations in `v13_discovery/semantic_extractor.py`:
- Replace literal phrases with genuine generalized grammatical constructs.
- In `attribute`: Use patterns matching copular adjective phrases, superlative properties (`\b(?:has|have)\s+the\s+(?:lowest|highest|greatest|smallest|largest|densest)\s+[a-z\s]+`), phrasal verbs (`is characterized by`, `features`, `exhibits`, `comprises`).
- In `member-of`: Use genuine membership connectors (`is an? (?:[a-z\-]+\s+)*(?:member of|example of|type of|class of|variant of)\b`, `belongs to (?:the family of|the class of)`).
- In `part-of`: Use structural part-whole grammar (`constitutes (?:the|an?|about)?`, `is composed of`, `forms? (?:part of|a peripheral|a constituent layer of)?`).
- In `definition`: Use standard definition copulas (`is defined as`, `refers to`, `denotes`, `is an? (?:imaginary|hypothetical|theoretical|physical|continuous)?\s*(?:line|stream|collection|point|zone|layer|system)\b`).
- In `exception`: Extract general prepositional phrases (`Unlike (?:the\s+)?(?P<sec>[A-Za-z\s]+?),`) without hardcoding `nearly all planets in`.
- Write your recommendations, exact regex patterns, and handoff report to:
  c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it3_1\handoff.md
- Send completion message to parent orchestrator.

## 2026-09-04T16:15:00Z
Formulate replacement patterns for all 5 locations in PATTERNS (lines 358, 363, 458, 463, 572) to purge literal golden set strings and implement genuine generalized grammar.
Write handoff.md and report to parent orchestrator.

