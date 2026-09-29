# Task Assignment: M2 Layout & Table Normalizer Explorer

You are teamwork_preview_explorer_m2_2.
Working directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2
Workspace root: c:\Users\harsh\Downloads\tayaari\tayaariapp
Authoritative request: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
Project plan: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_1\PROJECT.md
Corpus files: `source-material/geography_extracted.txt`, `source-material/geography_extracted_2.txt`, `source-material/consolidated_grounding.md`

Objective:
Investigate and design the document normalizer and table extractor (`v13_discovery/normalizer.py`):
1. Address the severe structural ingestion failures documented in Phase 0:
   - In V12, 100% of tables were discarded (`if "|" in line -> TABLE_OR_META`).
   - Multi-column reading order in `geography_extracted_2.txt` caused line-chopped vertical phrases.
   - Watermarks (`PARMAR SSC`, `ISBN...`, `www.ssccglpinnacle.com`) polluted entity recognition.
2. Design `v13_discovery/normalizer.py`:
   - Table parser: extract rows and columns from Markdown tables and structured comparative lists into structured knowledge propositions instead of discarding them.
   - Layout desegmenter: stitch broken line wraps ending in conjunctions or prepositions.
   - Watermark & OCR cleaner: strip running headers, page numbers, and copyright lines cleanly.
   - Output: `NormalizedBlock` and clean sentences mapped to source provenance.
3. Write your design specifications and handoff report to:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2\handoff.md
4. Send a completion message back to parent orchestrator.

## 2026-09-03T14:45:32Z
You are teamwork_preview_explorer_m2_2.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_2
Read DISPATCH.md, ORIGINAL_REQUEST.md, PROJECT.md, and corpus files.
Investigate and design the document normalizer and table extractor (v13_discovery/normalizer.py) to ingest markdown tables, stitch multi-column reading order, and clean watermarks/OCR.
Write handoff.md and send a completion message back to parent orchestrator.

