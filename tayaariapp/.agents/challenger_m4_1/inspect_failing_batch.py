import sys
sys.path.insert(0, ".")

from v13_discovery.question_synthesizer import (
    QuestionSynthesizer,
    DistractorVerificationGate,
)

synth = QuestionSynthesizer()
corpus_path = "source-material/geography_extracted.txt"
questions = synth.synthesize_from_corpus(corpus_path, min_questions=100)

failing = []
for idx, q in enumerate(questions):
    is_valid, errors = DistractorVerificationGate.verify_all(
        options=q.options,
        correct_key=q.correctAnswer,
        stem=q.stem,
        category=None
    )
    if not is_valid:
        failing.append((idx, q, errors))

print(f"Total failing questions: {len(failing)}")
for idx, q, errors in failing:
    correct_letter = q.correctAnswer.replace("opt_", "")
    print(f"\n--- Question #{idx} ({q.id}) ---")
    print(f"Stem: {q.stem}")
    print(f"Correct: {q.correctAnswer} -> {q.options[correct_letter]}")
    print(f"Errors: {errors}")
