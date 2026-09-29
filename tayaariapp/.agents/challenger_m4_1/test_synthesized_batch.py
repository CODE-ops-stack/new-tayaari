import sys
import os
sys.path.insert(0, ".")

from v13_discovery.question_synthesizer import (
    QuestionSynthesizer,
    DistractorVerificationGate,
    OntologyRegistry,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.provenance import audit_provenance_integrity
from v13_discovery.normalizer import DocumentNormalizer

print("Synthesizing batch of 100 questions from real corpus...")
synth = QuestionSynthesizer()
corpus_path = "source-material/geography_extracted.txt"
questions = synth.synthesize_from_corpus(corpus_path, min_questions=100)
print(f"Synthesized {len(questions)} questions.")

# Check 1: Stem uniqueness
stems = [q.stem.strip().lower() for q in questions]
unique_stems = set(stems)
print(f"Stem uniqueness: {len(unique_stems)} / {len(questions)}")

# Check 2: Correct answer distribution
answer_counts = {}
for q in questions:
    ans = q.correctAnswer
    answer_counts[ans] = answer_counts.get(ans, 0) + 1
print(f"Answer distribution: {answer_counts}")

# Check 3: Gate verification on every generated question
violations_per_question = []
for idx, q in enumerate(questions):
    is_valid, errors = DistractorVerificationGate.verify_all(
        options=q.options,
        correct_key=q.correctAnswer,
        stem=q.stem,
        category=None  # Using general verification
    )
    if not is_valid:
        violations_per_question.append((idx, q.id, errors))

print(f"Questions failing DistractorVerificationGate: {len(violations_per_question)}")
for idx, qid, errs in violations_per_question[:5]:
    print(f"  Q[{idx}] ({qid}): {errs}")

# Check 4: Distractor dissection integrity
dissection_errors = []
for idx, q in enumerate(questions):
    correct_opt_id = q.correctAnswer
    if len(q.distractorDissections) != 3:
        dissection_errors.append((idx, f"Expected 3 dissections, found {len(q.distractorDissections)}"))
    for d in q.distractorDissections:
        if d.get("optionId") == correct_opt_id:
            dissection_errors.append((idx, f"Dissection assigned to correct answer {correct_opt_id}"))
        if d.get("trapType") not in VALID_ROOM_TRAP_TYPES:
            dissection_errors.append((idx, f"Invalid trapType: {d.get('trapType')}"))
        if len(d.get("dissection", "")) < 15:
            dissection_errors.append((idx, f"Dissection rationale too short: {d.get('dissection')}"))

print(f"Questions with dissection errors: {len(dissection_errors)}")

# Check 5: Provenance audit
normalizer = DocumentNormalizer()
with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()
norm_blocks = normalizer.normalize(corpus_path, raw_text)
norm_text = norm_blocks[0].text if norm_blocks else raw_text
corpus_dict = {corpus_path: norm_text, os.path.abspath(corpus_path): norm_text}

prov_records = [q.provenance for q in questions]
audit = audit_provenance_integrity(prov_records, source_corpus=corpus_dict)
print(f"Provenance audit: verdict={audit['audit_verdict']}, rate={audit['integrity_rate']}, tampered={audit['tampered_records']}, broken={len(audit['broken_links'])}")
