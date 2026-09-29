import json
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from v13_discovery.question_synthesizer import (
    DistractorDissector,
    VALID_ROOM_TRAP_TYPES,
    OntologyRegistry,
    QuestionSynthesizer
)

reg = OntologyRegistry()
cat = reg.get_category("atmospheric_layers")

print("Testing all 8 trap types:")
for trap in VALID_ROOM_TRAP_TYPES:
    res = DistractorDissector.dissect(
        option_id="opt_b",
        distractor_text="Stratosphere",
        correct_text="Troposphere",
        category=cat,
        intent_type="definition",
        evidence="Troposphere is the lowest atmospheric layer.",
        forced_trap_type=trap
    )
    dis_len = len(res["dissection"])
    print(f"[{trap}] ({dis_len} chars): {res['dissection'][:65]}...")
    assert res["trapType"] == trap
    assert dis_len >= 15
    assert res["optionId"] == "opt_b"

print("\nVerifying 100 corpus questions...")
synth = QuestionSynthesizer(reg)
questions = synth.synthesize_from_corpus("source-material/geography_extracted.txt", min_questions=100)
dissection_errors = 0

for i, q in enumerate(questions):
    correct_opt_id = q.correctAnswer
    opt_keys = set(f"opt_{k}" for k in q.options.keys())
    distractor_opt_ids = opt_keys - {correct_opt_id}
    
    # Invariant 1: Exactly 3 dissections
    if len(q.distractorDissections) != 3:
        print(f"Q{i}: wrong count of dissections {len(q.distractorDissections)}")
        dissection_errors += 1
    
    assigned_ids = set()
    for d in q.distractorDissections:
        # Invariant 2: Never assigned to correct answer
        if d["optionId"] == correct_opt_id:
            print(f"Q{i}: dissection assigned to correct answer {correct_opt_id}")
            dissection_errors += 1
        assigned_ids.add(d["optionId"])
        # Invariant 3: Valid Room DB trap type
        if d["trapType"] not in VALID_ROOM_TRAP_TYPES:
            print(f"Q{i}: invalid trap type {d['trapType']}")
            dissection_errors += 1
        # Invariant 4: Substantive rationale
        if len(d["dissection"].strip()) < 15:
            print(f"Q{i}: rationale too short")
            dissection_errors += 1
    
    # Invariant 5: Covers all distractors
    if assigned_ids != distractor_opt_ids:
        print(f"Q{i}: assigned ids {assigned_ids} != distractor ids {distractor_opt_ids}")
        dissection_errors += 1
    
    # Invariant 6: JSON serialization
    try:
        json_str = json.dumps(q.distractorDissections)
        parsed = json.loads(json_str)
        assert len(parsed) == 3
    except Exception as ex:
        print(f"Q{i}: JSON error: {ex}")
        dissection_errors += 1

print(f"Total dissection errors across 100 corpus questions: {dissection_errors}")
if dissection_errors == 0:
    print("ALL DISSECTION INVARIANTS PERFECTLY SATISFIED!")
