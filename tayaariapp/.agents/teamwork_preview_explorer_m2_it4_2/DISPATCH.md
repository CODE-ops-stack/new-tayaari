# Dispatch — Explorer 2 (M2 Iteration 4)

You are teamwork_preview_explorer_m2_it4_2.
Your working directory is: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_m2_it4_2
Your parent orchestrator is: teamwork_preview_orchestrator_2 (Conv ID: e2c78cf0-a08b-4813-9278-2794b22a4aa2)

MANDATORY INPUTS TO READ:
1. ORIGINAL_REQUEST.md: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\ORIGINAL_REQUEST.md
2. PROJECT.md: c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_orchestrator_2\PROJECT.md
3. Challenger 2 Handoff (Iteration 3): c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_it3_2\handoff.md
4. Target files:
   - c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\semantic_extractor.py
   - c:\Users\harsh\Downloads\tayaari\tayaariapp\v13_discovery\normalizer.py

YOUR OBJECTIVE:
Investigate and formulate exact code remediations for Challenger 2's noise filtering and desegmentation defects:
1. Interrogative Sentence Filtering: Add an interrogative check to `NoiseFilterGate` to reject questions ending in `?` or starting with question words (`What`, `Why`, `How`, `Which`, `Where`, `When`, `Who`, `Whom`, `Whose`, `Is`, `Are`, `Can`, `Could`, `Do`, `Does`, `Did`).
2. Soft-Hyphen Desegmentation: Fix `LayoutDesegmenter.is_heading` in `normalizer.py` so hyphenated line wraps (lines ending in `-` or trailing soft hyphens) are NOT treated as section headings.
3. Incomplete Fragment Rejection: Filter incomplete/dangling phrases (`composed of$`, `consists of$`, `known as$`, `Scientists have discovered that$`).
4. Formatting Noise Normalization: Add normalization in `DocumentNormalizer` for smart quotes, em-dashes, markdown formatting, and unicode characters.

Produce exact code recommendations in handoff.md. Do NOT edit source files directly. Send a message to parent when done.
