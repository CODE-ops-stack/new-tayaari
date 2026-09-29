## 2026-09-06T07:38:54Z
# Task Assignment: Worker 1 — Milestone 4 Implementation (Question & Defensible Distractor Synthesizer)

## Identity
- Agent: worker_m4_1
- Type: teamwork_preview_worker
- Working Directory: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m4_1
- Parent: teamwork_preview_orchestrator_4 (Conv ID: 870ebe31-b7b8-4990-b9a6-83148369f1f4)

## Files to Read (in order)
1. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md (Mandatory: read §R3, §R5, §Acceptance 5)
2. c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_4\PROJECT.md
3. Spec Miner Handoff:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_spec_miner_m4_1\handoff.md
4. Explorer 2 Handoff & Prototype:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_2\handoff.md
5. Explorer 3 Handoff & Unit Test Prototypes:
   c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m4_3\handoff.md
6. Target Modules & Dependencies:
   - c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\provenance.py
   - c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\semantic_extractor.py
   - c:\Users\harsh\Downloads\tayaari\tayaariapp\tests\e2e\test_helpers.py

## Write Ownership
You have exclusive write ownership of:
- `v13_discovery/question_synthesizer.py`
- `tests/test_v13_distractor_engine.py`

## Implementation Objectives
1. **Implement `v13_discovery/question_synthesizer.py`**:
   - `OntologyRegistry`: 32+ domain categories covering Earth Sciences, geography, and astronomy, with member sets, aliases, and category definitions.
   - `DistractorVerificationGate`: Enforce the 5 criteria:
     1. Category compatibility (siblings in ontology)
     2. Grammatical fit & parallelism (uniform casing, number, no stem-terminal article leakage)
     3. Semantic plausibility (genuine curriculum concepts, no placeholders)
     4. Evidence support / counter-factual validity (distractor true entity, but false for stem predicate)
     5. Absence of clueing & length parity (length disparity < 3.0x, mutual distinctness, zero stem leakage)
   - `DistractorDissector`: Generate Room DB-compliant trap annotations and diagnostic rationales (>10 chars) for all 8 authorized trap types (`ABSOLUTE_WORDING`, `FACT_DISTORTION`, `FAMILIARITY_TRAP`, `CONCEPT_MIX`, `FALSE_CORRELATION`, `PARTIAL_TRUTH`, `TIMELINE_MISMATCH`, `UNCLASSIFIED_TRAP`) for every distractor (never for correct answer).
   - `NaturalStemSynthesizer`: Strict anti-quotation rules (NQ1–NQ5). Formulate natural civil-service exam stems across all 14 semantic intents.
   - `QuestionSynthesizer`: Generate `CandidateQuestion` objects, shuffle options with balanced distribution, and bind 6-link Merklized provenance records via `ProvenanceTracker.bind_candidate_question()` and `ProvenanceRecord.from_knowledge_node()`.
   - Batch Generation Method: `synthesize_from_corpus(corpus_path, min_questions=100)` generating >=100 high-quality candidate questions from real corpus nodes.
   - Markdown Serializer: Method `to_room_markdown()` conforming to `DataImporter.kt` syntax (remember: `Explanation:` must precede `Correct Answer:`).

2. **Implement `tests/test_v13_distractor_engine.py`**:
   - Implement the 24 test methods designed by Explorer 3 covering:
     * Stem Naturalness & Anti-Quotation enforcement
     * Ontological Category Adherence
     * Distractor Dissection Validity (all 8 trap types, correct length, no correct answer tagged)
     * Grammatical & Stylistic Parity
     * Unbreakable Provenance Integrity (tamper detection, Merklized link hashing)
     * Scale Synthesis Verification (>=100 questions from corpus)

3. **Verification Commands**:
   - `python -m unittest tests/test_v13_distractor_engine.py`
   - `python -m pytest tests/test_v13_distractor_engine.py`
   - `python -m unittest discover -s tests -p "test_*.py"`
   - `python run_e2e_tests.py`

## Deliverables
- Write complete handoff report to:
  `c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m4_1\handoff.md`
- Send message back to parent orchestrator (`870ebe31-b7b8-4990-b9a6-83148369f1f4`) upon completion with test results.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
