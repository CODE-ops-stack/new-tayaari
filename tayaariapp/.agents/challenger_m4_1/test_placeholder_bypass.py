import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import DistractorVerificationGate

placeholders_to_test = [
    "Option 1",
    "Option 2",
    "Choice A",
    "Choice 1",
    "All of the above",
    "N/A",
    "NA",
    "Dummy",
    "Sample",
    "Test Option",
]

for ph in placeholders_to_test:
    opts = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": ph}
    is_valid, errors = DistractorVerificationGate.check_semantic_plausibility(opts)
    print(f"'{ph}' -> caught? {not is_valid}, errors: {errors}")
