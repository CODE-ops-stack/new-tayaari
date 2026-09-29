#!/usr/bin/env python3
"""
Test script generating 100 questions from source-material/geography_extracted.txt
and verifying that all 100 pass DistractorVerificationGate.verify_all() with 0% stem leakage.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    QuestionSynthesizer,
    DistractorVerificationGate,
)

def main():
    print("Initializing QuestionSynthesizer...")
    synth = QuestionSynthesizer()
    corpus_path = os.path.join(REPO_ROOT, "source-material", "geography_extracted.txt")

    print(f"Synthesizing 100 questions from {corpus_path}...")
    questions = synth.synthesize_from_corpus(corpus_path, min_questions=100)
    print(f"Total questions synthesized: {len(questions)}")
    assert len(questions) >= 100, f"Expected >= 100 questions, got {len(questions)}"

    failing_gate = []
    failing_leakage = []

    for idx, q in enumerate(questions):
        # 1. 5-point verification gate
        is_valid, errors = DistractorVerificationGate.verify_all(
            options=q.options,
            correct_key=q.correctAnswer,
            stem=q.stem,
            category=None
        )
        if not is_valid:
            failing_gate.append((idx, q.id, q.stem, q.correctAnswer, errors))

        # 2. Absence of clueing & stem leakage gate
        is_clue_free, clue_errors = DistractorVerificationGate.check_absence_of_clueing(
            options=q.options,
            correct_key=q.correctAnswer,
            stem=q.stem
        )
        if not is_clue_free:
            failing_leakage.append((idx, q.id, q.stem, q.correctAnswer, clue_errors))

    print(f"Gate failures: {len(failing_gate)} / {len(questions)}")
    print(f"Stem leakage failures: {len(failing_leakage)} / {len(questions)}")

    if failing_gate:
        for idx, qid, stem, ans, errs in failing_gate[:5]:
            print(f"  FAIL Q#{idx} ({qid}): ans={ans}, stem='{stem}', errs={errs}")

    assert len(failing_gate) == 0, f"Expected 0 gate failures, got {len(failing_gate)}"
    assert len(failing_leakage) == 0, f"Expected 0 stem leakage failures, got {len(failing_leakage)}"

    print("\nSUCCESS: All 100 questions strictly passed DistractorVerificationGate.verify_all() with 0% stem leakage!")

if __name__ == "__main__":
    main()
