# Original User Request

## Initial Request — 2026-09-03T10:33:42Z

Build and validate a substantially better source-driven educational question discovery pipeline (V13) for the Tayaari Pakki Android application. The goal is to maximize legitimate knowledge recovery (high recall) and minimize false acceptance (high precision) while generating natural exam-quality questions with defensible distractors. 

Working directory: c:/Users/harsh/Downloads/tayaari/tayaariapp
Integrity mode: development

## Requirements

### R1. Forensic & Corpus Analysis
Trace the actual V12 content pipeline to identify architectural failure points. Profile the real source-material corpus to quantify lost knowledge types.

### R2. Advanced Knowledge Representation
Design an extraction architecture that maps source blocks to explicit semantic intents (definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of). **You are permitted to use external Python NLP libraries (e.g., spacy, nltk) and/or local API-based LLMs to achieve robust semantic parsing.** Do not rely solely on simple Subject-Verb-Object (SVO) regex patterns.

### R3. Question & Distractor Engineering
Build explicit Question Intents before wording. Distractors must be independently verified for category compatibility, grammatical fit, semantic plausibility, evidence support, and absence of clueing/contradiction. A verified fact is not automatically a valid distractor if it creates a semantically invalid combination.

### R4. Multi-Agent Auditing System
Implement a system of independent validation agents: 
- Cognitive Auditor (validate RECALL, UNDERSTAND, COMPARE, APPLY, etc.)
- Exam-Fit Auditor (UPSC, BPSC, SSC CGL, etc.)
- Adversarial Auditor (check factual errors, ambiguity, bad grammar, source paraphrase, leakage). 
**You may use API-based LLMs as the independent internal validation/auditing engines.** The final quality gate must be capable of rejecting a question that the generator itself considers valid.

### R5. Mandatory Experiments & Provenance
Compare at least three viable extraction/representation approaches before final implementation. Process at least 100 real source units. Generate at least 100 opportunities or exhaust the corpus. Every accepted question must have unbreakable provenance (Question → Intent → Knowledge Unit → Evidence → Source → Location).

## Acceptance Criteria

### Execution & Verification
- [ ] At least three extraction approaches were compared, and the metrics (precision, recall, false acceptance/rejection) are documented.
- [ ] A representative evaluation set containing at least 50 positive and 50 negative examples is built and tested.
- [ ] At least 50 candidate questions were generated (if evidence permitted) and subjected to independent adversarial auditing.
- [ ] A complete regeneration cycle was executed after systemic repair of first-round audit failures.
- [ ] No generated questions rely on generic source quotation templates (e.g., "What is a direct consequence of '[fragment]'?").
- [ ] All existing regression tests pass.
- [ ] New regression tests exist for MCQ leakage, OCR fragments, multi-word entities, non-SVO facts, semantic duplicates, and provenance failures.
- [ ] Android unit tests (`.\gradlew.bat clean testDebugUnitTest`) pass.
- [ ] Android app builds successfully (`.\gradlew.bat clean assembleDebug`).
