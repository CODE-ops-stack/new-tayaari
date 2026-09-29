import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import DistractorVerificationGate

options = {"a": "Oxbow lake", "b": "Cirque", "c": "Moraine", "d": "Delta"}
stems = [
    "Which fluvial process creates an?",
    "Which geological feature represents a?",
    "In Earth science, this structure forms an:",
    "Which natural formation constitutes a?",
]
for s in stems:
    is_valid, errors = DistractorVerificationGate.check_grammatical_fit(options, s)
    print(f"'{s}' -> caught? {not is_valid}, errors: {errors}")
