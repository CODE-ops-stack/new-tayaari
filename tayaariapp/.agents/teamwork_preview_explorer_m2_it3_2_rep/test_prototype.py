#!/usr/bin/env python3
import json
import sys
import os

from prototype_patterns import GeneralizedSemanticExtractor

def test_counter_examples():
    print("=== TESTING EXPERIMENTS A, B, C (COUNTER-EXAMPLES) ===")
    cases = [
        ("Exp A - Gold", "Primary waves (P-waves) are longitudinal compressional waves that vibrate parallel to the direction of wave propagation.", "attribute"),
        ("Exp A - Unseen", "Primary waves (P-waves) are fast mechanical vibrations that travel through rock.", "attribute"),
        ("Exp B - Gold", "Saturn has the lowest mean density among all planets in the Solar System at 0.69 grams per cubic centimeter, making it less dense than water.", "attribute"),
        ("Exp B - Unseen", "Saturn has the highest equatorial bulge among all planets in the Solar System at 0.69 grams per cubic centimeter, making it less dense than water.", "attribute"),
        ("Exp C - Gold", "The Sun is an ordinary yellow dwarf star located in the Orion Cygnus Arm.", "member-of"),
        ("Exp C - Unseen", "The Sun is an ordinary main-sequence star located in the Milky Way.", "member-of"),
    ]
    all_ok = True
    for name, text, expected in cases:
        got = GeneralizedSemanticExtractor.extract_intent(text)
        ok = (got == expected)
        status = "PASS" if ok else f"FAIL (got {got})"
        print(f"  {name:16}: Expected={expected:12} | Result={status}")
        if not ok:
            all_ok = False
    return all_ok

def test_golden_eval_set():
    print("\n=== TESTING POSITIVE ITEMS IN data/golden_eval_set.json ===")
    with open("data/golden_eval_set.json", encoding="utf-8") as f:
        data = json.load(f)
    pos = [x for x in data["examples"] if x["expected_label"] == "positive"]

    alias_map = {
        "cause/effect": "cause/effect",
        "part-of": "part-of",
        "member-of": "member-of"
    }

    mismatches = 0
    for p in pos:
        exp = p["intent"]
        got = GeneralizedSemanticExtractor.extract_intent(p["text"])
        if got != exp:
            mismatches += 1
            print(f"  MISMATCH [{p['id']}]: Exp={exp:14} | Got={str(got):14} | Text: {p['text'][:65]}...")
    print(f"Total Positive: {len(pos)} | Mismatches: {mismatches}")
    return mismatches == 0

def test_unseen_14_intents():
    print("\n=== TESTING UNSEEN EDUCATIONAL SENTENCES (ALL 14 INTENTS) ===")
    unseen_dataset = [
        # 1. definition
        ("UNSEEN-DEF-1", "definition", "Photosynthesis is defined as the biochemical process whereby green plants synthesize carbohydrates from carbon dioxide and water."),
        ("UNSEEN-DEF-2", "definition", "An aquifer refers to an underground layer of water-bearing permeable rock, rock fractures, or unconsolidated materials."),
        # 2. attribute
        ("UNSEEN-ATT-1", "attribute", "Secondary waves (S-waves) are transverse shear vibrations that displace rock particles perpendicular to the direction of wave travel."),
        ("UNSEEN-ATT-2", "attribute", "Jupiter has the greatest gravitational acceleration among all planets in the Solar System at 24.79 meters per second squared."),
        # 3. cause/effect
        ("UNSEEN-CAU-1", "cause/effect", "Sulfur dioxide emissions from industrial combustion cause acid precipitation by reacting with atmospheric moisture."),
        ("UNSEEN-CAU-2", "cause/effect", "Severe coastal erosion is triggered by storm surges during intense tropical hurricanes."),
        # 4. comparison
        ("UNSEEN-COM-1", "comparison", "Granite is much coarser-grained than basalt due to slow subterranean magma cooling."),
        ("UNSEEN-COM-2", "comparison", "Arteries carry oxygenated blood away from the heart at high hydrostatic pressure, whereas veins transport deoxygenated blood back to the heart under low pressure."),
        # 5. spatial
        ("UNSEEN-SPA-1", "spatial", "The Mariana Trench is located in the western Pacific Ocean, extending over 2,500 kilometres along a convergent plate boundary."),
        ("UNSEEN-SPA-2", "spatial", "Between the Western Ghats and the Arabian Sea lies the Konkan coastal plain."),
        # 6. distribution
        ("UNSEEN-DIS-1", "distribution", "Extensive reserves of petroleum are concentrated in the sedimentary basins of the Persian Gulf region."),
        ("UNSEEN-DIS-2", "distribution", "Mangrove forests are distributed across tropical and subtropical intertidal estuaries and deltaic shorelines."),
        # 7. classification
        ("UNSEEN-CLA-1", "classification", "Meteorologists classify clouds into three altitude families: high clouds, middle clouds, and low clouds."),
        ("UNSEEN-CLA-2", "classification", "Plate boundaries can be divided into divergent boundaries, convergent boundaries, and transform fault margins."),
        # 8. quantity
        ("UNSEEN-QUA-1", "quantity", "The Mariana Trench extends to a depth of approximately 10,994 meters below sea level at the Challenger Deep."),
        ("UNSEEN-QUA-2", "quantity", "Electromagnetic radiation in a vacuum travels at approximately 299,792 kilometres per second."),
        # 9. sequence
        ("UNSEEN-SEQ-1", "sequence", "The hydrological cycle progresses through a continuous sequence: solar evaporation from ocean surfaces, atmospheric condensation into clouds, terrestrial precipitation, and surface runoff back to oceans."),
        ("UNSEEN-SEQ-2", "sequence", "During cell division, mitosis progresses through four chronological stages: prophase, metaphase, anaphase, and telophase."),
        # 10. condition
        ("UNSEEN-CON-1", "condition", "Atmospheric dew forms only when the ground surface temperature falls below the dew point temperature on calm, clear nights."),
        ("UNSEEN-CON-2", "condition", "Glacial flow can occur only if the accumulated ice thickness exceeds 30 meters, generating sufficient internal plastic deformation."),
        # 11. exception
        ("UNSEEN-EXC-1", "exception", "Except for the platypus and echidna, all living mammals give birth to live young rather than laying eggs."),
        ("UNSEEN-EXC-2", "exception", "Mercury is the only metallic element that remains liquid at standard ambient room temperature and pressure."),
        # 12. process
        ("UNSEEN-PRO-1", "process", "Cellular respiration converts biochemical energy from glucose nutrients into adenosine triphosphate (ATP) molecules and metabolic waste."),
        ("UNSEEN-PRO-2", "process", "Regional metamorphism is the thermodynamic process whereby intense heat and confining pressure recrystallize shale rocks into foliated schists."),
        # 13. part-of
        ("UNSEEN-PAR-1", "part-of", "The inner core constitutes the innermost solid metallic sphere of the Earth, consisting primarily of an iron-nickel alloy."),
        ("UNSEEN-PAR-2", "part-of", "Mitochondria form an essential organelle component located within the cytoplasm of eukaryotic cells."),
        # 14. member-of
        ("UNSEEN-MEM-1", "member-of", "Betelgeuse is a prominent red supergiant star located in the constellation of Orion."),
        ("UNSEEN-MEM-2", "member-of", "The Indian rhinoceros is a vulnerable member of the greater one-horned rhinoceros family indigenous to the Brahmaputra valley.")
    ]

    all_ok = True
    for item_id, expected, text in unseen_dataset:
        got = GeneralizedSemanticExtractor.extract_intent(text)
        ok = (got == expected)
        status = "PASS" if ok else f"FAIL (got {got})"
        print(f"  [{item_id}] {expected:14}: {status} | Text: {text[:60]}...")
        if not ok:
            all_ok = False
    return all_ok

def test_negatives():
    print("\n=== TESTING NEGATIVE ITEMS (NOISE FILTER + EXTRACTOR) ===")
    import sys
    sys.path.insert(0, ".")
    from v13_discovery.semantic_extractor import NoiseFilterGate

    with open("data/golden_eval_set.json", encoding="utf-8") as f:
        data = json.load(f)
    neg = [x for x in data["examples"] if x["expected_label"] == "negative"]

    false_accepts = 0
    for n in neg:
        text = n["text"]
        # In isolated sentence context, unresolved pronouns should be rejected
        rej = NoiseFilterGate.audit(text, is_block_context=False)
        if rej is not None:
            continue
        # If noise gate let it through, check if extractor matches anything
        intent = GeneralizedSemanticExtractor.extract_intent(text)
        if intent is not None:
            false_accepts += 1
            print(f"  FALSE ACCEPT [{n['id']}]: cat={n.get('rejection_category')} | intent={intent} | text={text[:60]}...")
    print(f"Total Negative: {len(neg)} | False Acceptances: {false_accepts}")
    return false_accepts == 0

if __name__ == "__main__":
    c1 = test_counter_examples()
    c2 = test_golden_eval_set()
    c3 = test_unseen_14_intents()
    c4 = test_negatives()
    print(f"\nOVERALL SUMMARY: Counter-examples={c1}, Golden Set={c2}, Unseen 14 Intents={c3}, Negative Noise={c4}")
