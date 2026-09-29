# Task Assignment: Explorer 3 — Milestone 4 Provenance Integration & Scale Synthesis

## Identity
- Agent: explorer_m4_3
- Type: teamwork_preview_explorer
- Working Directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_3
- Parent: teamwork_preview_orchestrator_4 (Conv ID: 870ebe31-b7b8-4990-b9a6-83148369f1f4)

## Documents to Read (in order)
1. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md (§R3, §R5, §Acceptance Criteria)
2. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md
3. c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\provenance.py (ProvenanceTracker, ProvenanceRecord, LinkHashes, verify_provenance_chain)
4. c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\semantic_extractor.py
5. c:\Users\harsh\Downloads\tayaari\tayaariapp\tests\e2e\test_helpers.py (CandidateQuestion, verify_provenance_chain)
6. c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt

## Objectives & Scope
1. **Unbreakable Provenance Binding**:
   - Design the exact workflow for binding synthesized questions to their 6-link provenance chain:
     `Question ID (bound stem) -> Intent -> Knowledge Unit -> Evidence -> Source -> Location`.
   - Ensure compatibility with `ProvenanceTracker.bind_candidate_question()` and `ProvenanceRecord.from_knowledge_node()`.
   - Ensure tamper-evident SHA-256 Merklized hashing passes `verify_provenance_chain`.
2. **Scale Synthesis Workflow (>=100 Opportunities)**:
   - Design the batch generator capable of extracting `KnowledgeNode`s from real corpus (`source-material/geography_extracted.txt`, etc.) and synthesizing >=100 diverse, high-quality candidate questions across the 14 intents.
   - Design deduplication and quality filters (rejecting malformed nodes, ensuring unique question stems, balanced option shuffling).
3. **Unit Test Suite Architecture (`tests/test_v13_distractor_engine.py`)**:
   - Design comprehensive unit tests covering:
     * Question stem naturalness (zero quotation marks, zero lazy template phrases).
     * Ontological category adherence (distractors share category with answer).
     * Distractor dissection validity (all 8 trap types valid, rationales present).
     * Grammatical alignment (POS, casing, number).
     * Unbreakable provenance integrity (all links verified, tamper detection).
     * Scale synthesis verification (>=100 questions produced from corpus).
   - Provide concrete test prototypes.

## Deliverables
Write your comprehensive architectural report, integration workflows, and unit test prototypes to:
`c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_3\handoff.md`

Send a message back to parent orchestrator (870ebe31-b7b8-4990-b9a6-83148369f1f4) when complete.
