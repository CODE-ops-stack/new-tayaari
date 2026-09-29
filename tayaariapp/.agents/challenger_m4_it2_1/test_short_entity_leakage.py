import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import DistractorVerificationGate

entities_to_test = [
    ("Fog", "Which atmospheric condensation phenomenon known as fog reduces visibility below 1 km?"),
    ("Ice", "Which solid form of water known as ice covers polar regions?"),
    ("Sun", "Which central star known as the sun provides light to the solar system?"),
    ("Ore", "Which naturally occurring mineral aggregate known as ore contains extractable metals?"),
]

print("=== Testing 3-Letter Entity Stem Leakage ===")
all_passed = True
for entity, leaking_stem in entities_to_test:
    options = {"a": entity, "b": "Distractor1", "c": "Distractor2", "d": "Distractor3"}
    is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
        options=options,
        correct_key="opt_a",
        stem=leaking_stem
    )
    print(f"Entity '{entity}' with stem '{leaking_stem}' -> Caught? {not is_valid}, errors: {errors}")
    if is_valid or not any("Stem leakage detected" in e for e in errors):
        all_passed = False

# Also test negative cases: ensure substring matches do not falsely trigger
negative_tests = [
    ("Ice", "Which process on the ocean surface causes evaporation?"), # 'ice' inside 'surface'
    ("Ore", "Which landform existed before the glaciation epoch?"), # 'ore' inside 'before'
]

print("\n=== Testing False Positive Substring Boundaries ===")
for entity, clean_stem in negative_tests:
    options = {"a": entity, "b": "Distractor1", "c": "Distractor2", "d": "Distractor3"}
    is_valid, errors = DistractorVerificationGate.check_absence_of_clueing(
        options=options,
        correct_key="opt_a",
        stem=clean_stem
    )
    leak_errors = [e for e in errors if "Stem leakage detected" in e]
    print(f"Entity '{entity}' with stem '{clean_stem}' -> False positive? {len(leak_errors) > 0}, errors: {leak_errors}")
    if len(leak_errors) > 0:
        all_passed = False

print(f"\nOverall short-entity leakage test: {'PASS' if all_passed else 'FAIL'}")
