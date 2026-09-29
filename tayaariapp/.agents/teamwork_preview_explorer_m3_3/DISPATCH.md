# Dispatch: Explorer 3 Milestone 3 (explorer_m3_3)

**Working Directory**: `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3`
**Parent Conversation ID**: `870ebe31-b7b8-4990-b9a6-83148369f1f4`
**Parent Orchestrator**: `teamwork_preview_orchestrator_4`

## Mandatory Reference Documents
1. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md` (Read first)
2. `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md`
3. `v13_discovery/semantic_extractor.py` and `v13_discovery/normalizer.py`

## Tasks
1. Design the Unbreakable Provenance Registry architecture (`v13_discovery/provenance.py`):
   - Strict 6-link chain: `Question ID -> Intent -> Knowledge Unit -> Evidence -> Source -> Location`.
   - Immutable data model (dataclass with frozen attributes or cryptographic verification).
   - Tamper-evident hashing (`provenance_hash` via SHA-256) verifying that changes to question stem, intent, evidence, source, or line/page invalidate the hash.
2. Design provenance verification functions:
   - `verify_provenance_chain(record: ProvenanceRecord, source_corpus: dict) -> bool`
   - `audit_provenance_integrity(records: list[ProvenanceRecord]) -> dict`
3. Define integration points with `KnowledgeNode` and downstream `CandidateQuestion` (Milestone 4).
4. Provide drop-in class skeleton and unit test design (`tests/test_v13_provenance.py`).
5. Write complete exploration report to `handoff.md` and send message to parent orchestrator.

## 2026-09-06T07:11:12Z
You are explorer_m3_3 (Explorer 3 for Milestone 3: Unbreakable Provenance Architecture).
Your working directory is:
c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3
Your parent orchestrator is teamwork_preview_orchestrator_4 (Conversation ID: 870ebe31-b7b8-4990-b9a6-83148369f1f4).

Read in order:
1. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
2. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md
3. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3\DISPATCH.md
4. v13_discovery/semantic_extractor.py

Tasks:
1. Design the Unbreakable Provenance Registry architecture (v13_discovery/provenance.py):
   - Strict 6-link chain: Question ID -> Intent -> Knowledge Unit -> Evidence -> Source -> Location.
   - Immutable data model with SHA-256 tamper-evident hashing.
2. Design verification functions (verify_provenance_chain, audit_provenance_integrity).
3. Define integration points with KnowledgeNode and downstream CandidateQuestion.
4. Provide drop-in class skeleton and unit test design (tests/test_v13_provenance.py).
Write your complete exploration report to:
c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m3_3\handoff.md
Send a message back to parent orchestrator (870ebe31-b7b8-4990-b9a6-83148369f1f4).

