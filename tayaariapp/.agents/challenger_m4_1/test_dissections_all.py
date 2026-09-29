import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import DistractorDissector, VALID_ROOM_TRAP_TYPES

print("Testing all 8 trap types:")
for trap in VALID_ROOM_TRAP_TYPES:
    res = DistractorDissector.dissect(
        option_id="opt_b",
        distractor_text="Stratosphere",
        correct_text="Troposphere",
        category=None,
        intent_type="definition",
        evidence="The troposphere is the lowest atmospheric layer.",
        forced_trap_type=trap
    )
    print(f"  Trap: {trap:<20} | Length: {len(res['dissection']):<3} | Dissection snippet: {res['dissection'][:60]}...")
