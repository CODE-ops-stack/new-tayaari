# Dispatch — Challenger 2 (M2 Iteration 3)

You are teamwork_preview_challenger_m2_it3_2.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_it3_2
Your parent orchestrator is: teamwork_preview_orchestrator_2 (Conv ID: e2c78cf0-a08b-4813-9278-2794b22a4aa2)

MANDATORY INPUTS TO READ:
1. ORIGINAL_REQUEST.md: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
2. PROJECT.md: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_2\PROJECT.md
3. Worker Handoff: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_worker_m2_3\handoff.md
4. Forensic Auditor M2 It2 report: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_auditor_m2_it2_1\handoff.md

YOUR MISSION:
Adversarially challenge the generalized extractor and normalizer:
1. Test boundary edge cases:
   - Very long sentences (>150 words)
   - Formatting noise (special characters, unicode ligatures, escaped symbols)
   - Multi-column text layouts, table blocks with merged cells and headers
   - Plural vs singular coreference propagation across sentences in NormalizedBlock
2. Check for false positives: Ensure noise patterns (headings, questions, bibliographic entries, incomplete fragments) are rejected.
3. Issue an authoritative verdict: APPROVE or REQUEST_CHANGES.
4. Write your findings and empirical test logs in handoff.md and notify the parent orchestrator via send_message.
