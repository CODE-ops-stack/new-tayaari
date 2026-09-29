# Task Assignment: Explorer 2 — Milestone 4 Ontological Distractor Engine

## Identity
- Agent: explorer_m4_2
- Type: teamwork_preview_explorer
- Working Directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_2
- Parent: teamwork_preview_orchestrator_4 (Conv ID: 870ebe31-b7b8-4990-b9a6-83148369f1f4)

## Documents to Read (in order)
1. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md (§R3, §Acceptance 5)
2. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md
3. c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\semantic_extractor.py (KnowledgeNode, 14 semantic intents)
4. c:\Users\harsh\Downloads\tayaari\tayaariapp\tests\e2e\test_helpers.py (CandidateQuestion, VALID_ROOM_TRAP_TYPES)
5. c:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt (Corpus domain: physical geography, climatology, geomorpology, astronomy)

## Objectives & Scope
1. **Ontological Taxonomy Design**: Design category taxonomy covering geography/science domains (e.g. terrestrial planets, outer planets, atmospheric layers, cloud types, river landforms, glacial features, ocean currents, soil horizons, minerals, faults).
2. **5-Point Distractor Verification Criteria**:
   - Category compatibility: Distractors must belong to the exact same ontological category as the target entity (e.g. if answer is "Troposphere", distractors must be other atmospheric layers like "Stratosphere", "Mesosphere", "Thermosphere", never rivers or planets).
   - Grammatical fit: Same part of speech, singular/plural agreement, tense, and article agreement with the stem.
   - Semantic plausibility: Distractors must represent viable options that competitive exam candidates would consider.
   - Evidence support / factual validity: The distractor terms themselves are real educational entities, but their association with the question predicate is false.
   - Absence of clueing/leakage: No length outliers, grammatical giveaways, or mutual contradictions that eliminate options without knowledge.
3. **Distractor Dissection Engine**:
   - For every generated distractor, synthesize the diagnostic trap annotation:
     * `trapType`: one of `VALID_ROOM_TRAP_TYPES`
     * `rationale`: diagnostic explanation of why this option is incorrect and what cognitive trap it exploits.
4. **Architecture & Class Design**:
   - Provide concrete class design for `v13_discovery/question_synthesizer.py` (e.g., `OntologyRegistry`, `DistractorGenerator`, `QuestionSynthesizer`).
   - Include drop-in prototype code/skeletons.

## Deliverables
Write your comprehensive architectural report and prototype skeletons to:
`c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_2\handoff.md`

Send a message back to parent orchestrator (870ebe31-b7b8-4990-b9a6-83148369f1f4) when complete.
