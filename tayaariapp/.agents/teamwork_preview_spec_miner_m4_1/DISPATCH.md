# Task Assignment: Spec Miner 1 — Milestone 4 Question Specifications & Contracts

## Identity
- Agent: spec_miner_m4_1
- Type: teamwork_preview_spec_miner
- Working Directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_spec_miner_m4_1
- Parent: teamwork_preview_orchestrator_4 (Conv ID: 870ebe31-b7b8-4990-b9a6-83148369f1f4)

## Documents to Read (in order)
1. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md (Mandatory: read §R3, §R5, §Acceptance 5)
2. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md (§Interface Contracts, §Feature Inventory)
3. c:\Users\harsh\Downloads\tayaari\tayaariapp\tests\e2e\test_helpers.py (CandidateQuestion dataclass, DataImporterSimulator, VALID_ROOM_TRAP_TYPES)
4. c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\semantic_extractor.py (KnowledgeNode, 14 semantic intents)
5. c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\consolidated_grounding.md (Target Room DB markdown schema)

## Objectives & Scope
1. **Contract Mapping**: Extract and document the exact data structures and contracts required for `CandidateQuestion` and its serialization format for `source-material/consolidated_grounding.md`.
2. **Trap Taxonomy Specification**: Define the 8 Room DB distractor trap types (`ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`, `UNCLASSIFIED_TRAP`) and provide diagnostic rationale templates.
3. **No-Quotation Rule Specification**: Formulate strict syntactic and lexical rules to ensure generated question stems NEVER use quotation templates or lazy fragment embedding (e.g. ban "What is a direct consequence of '[fragment]'?", "Consider the statement '[fragment]'...", "According to the passage, '[quote]'...").
4. **Natural Stem Generation Rules per Intent**: For each of the 14 semantic intents (definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of), specify natural, exam-style stem patterns based on entity, predicate, and context.

## Deliverables
Write your exhaustive specification report to:
`c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_spec_miner_m4_1\handoff.md`

Send a message back to parent orchestrator (870ebe31-b7b8-4990-b9a6-83148369f1f4) when complete.
