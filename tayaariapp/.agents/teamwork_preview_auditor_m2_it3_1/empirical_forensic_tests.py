import sys
import os
import unittest

cur = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.abspath(os.path.join(cur, "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    PRONOUN_TOKENS,
    canonicalize_intent
)
from v13_discovery.normalizer import NormalizedBlock

def run_empirical_generalization_tests():
    se = SemanticExtractor()
    print("=== DYNAMIC GENERALIZATION EXPERIMENTS ===")

    # Exp A
    s_gold_a = "Primary waves (P-waves) are longitudinal compressional waves that vibrate parallel to the direction of wave propagation."
    s_unseen_a = "Primary waves (P-waves) are fast mechanical vibrations that travel through rock."
    res_gold_a = se.extract(s_gold_a)
    res_unseen_a = se.extract(s_unseen_a)
    print(f"Exp A - Gold intent: {res_gold_a[0].intent_type if res_gold_a else None}, Entity: {res_gold_a[0].primary_entity if res_gold_a else None}")
    print(f"Exp A - Unseen intent: {res_unseen_a[0].intent_type if res_unseen_a else None}, Entity: {res_unseen_a[0].primary_entity if res_unseen_a else None}")
    assert res_gold_a and res_gold_a[0].intent_type == "attribute", "Exp A Gold failed"
    assert res_unseen_a and res_unseen_a[0].intent_type == "attribute", f"Exp A Unseen failed: got {res_unseen_a[0].intent_type if res_unseen_a else None}"

    # Exp B
    s_gold_b = "Saturn has the lowest mean density among all planets in the Solar System at 0.69 grams per cubic centimeter, making it less dense than water."
    s_unseen_b = "Saturn has the highest equatorial bulge among all planets in the Solar System at 0.69 grams per cubic centimeter, making it less dense than water."
    res_gold_b = se.extract(s_gold_b)
    res_unseen_b = se.extract(s_unseen_b)
    print(f"Exp B - Gold intent: {res_gold_b[0].intent_type if res_gold_b else None}, Entity: {res_gold_b[0].primary_entity if res_gold_b else None}")
    print(f"Exp B - Unseen intent: {res_unseen_b[0].intent_type if res_unseen_b else None}, Entity: {res_unseen_b[0].primary_entity if res_unseen_b else None}")
    assert res_gold_b and res_gold_b[0].intent_type == "attribute", "Exp B Gold failed"
    assert res_unseen_b and res_unseen_b[0].intent_type == "attribute", f"Exp B Unseen failed: got {res_unseen_b[0].intent_type if res_unseen_b else None}"

    # Exp C
    s_gold_c = "The Sun is an ordinary yellow dwarf star located in the Orion Cygnus Arm."
    s_unseen_c = "The Sun is an ordinary main-sequence star located in the Milky Way."
    res_gold_c = se.extract(s_gold_c)
    res_unseen_c = se.extract(s_unseen_c)
    print(f"Exp C - Gold intent: {res_gold_c[0].intent_type if res_gold_c else None}, Entity: {res_gold_c[0].primary_entity if res_gold_c else None}")
    print(f"Exp C - Unseen intent: {res_unseen_c[0].intent_type if res_unseen_c else None}, Entity: {res_unseen_c[0].primary_entity if res_unseen_c else None}")
    assert res_gold_c and canonicalize_intent(res_gold_c[0].intent_type) == "member_of", "Exp C Gold failed"
    assert res_unseen_c and canonicalize_intent(res_unseen_c[0].intent_type) == "member_of", f"Exp C Unseen failed: got {res_unseen_c[0].intent_type if res_unseen_c else None}"

    # Novel Exp D: Superlative attribute
    s_unseen_d = "Neptune has the strongest supersonic winds among all planets in the Solar System, reaching speeds of 2,100 km/h."
    res_unseen_d = se.extract(s_unseen_d)
    print(f"Novel Exp D - Unseen intent: {res_unseen_d[0].intent_type if res_unseen_d else None}, Entity: {res_unseen_d[0].primary_entity if res_unseen_d else None}")
    assert res_unseen_d and res_unseen_d[0].intent_type == "attribute", f"Novel Exp D failed: got {res_unseen_d[0].intent_type if res_unseen_d else None}"

    # Novel Exp E: Exception
    s_unseen_e = "While nearly all elements in the periodic table are solids at room temperature, mercury and bromine are unique exceptions that remain liquid."
    res_unseen_e = se.extract(s_unseen_e)
    print(f"Novel Exp E - Unseen intent: {res_unseen_e[0].intent_type if res_unseen_e else None}, Entity: {res_unseen_e[0].primary_entity if res_unseen_e else None}")
    assert res_unseen_e and res_unseen_e[0].intent_type == "exception", f"Novel Exp E failed: got {res_unseen_e[0].intent_type if res_unseen_e else None}"

    # Novel Exp F: Cause/Effect
    s_unseen_f = "Intense tectonic compression causes catastrophic buckling of lithospheric strata."
    res_unseen_f = se.extract(s_unseen_f)
    print(f"Novel Exp F - Unseen intent: {res_unseen_f[0].intent_type if res_unseen_f else None}, Entity: {res_unseen_f[0].primary_entity if res_unseen_f else None}")
    assert res_unseen_f and canonicalize_intent(res_unseen_f[0].intent_type) == "cause_effect", f"Novel Exp F failed: got {res_unseen_f[0].intent_type if res_unseen_f else None}"

    # Novel Exp G: Definition
    s_unseen_g = "An ecosystem is defined as a biological community of interacting organisms and their physical environment."
    res_unseen_g = se.extract(s_unseen_g)
    print(f"Novel Exp G - Unseen intent: {res_unseen_g[0].intent_type if res_unseen_g else None}, Entity: {res_unseen_g[0].primary_entity if res_unseen_g else None}")
    assert res_unseen_g and res_unseen_g[0].intent_type == "definition", f"Novel Exp G failed: got {res_unseen_g[0].intent_type if res_unseen_g else None}"

    # Novel Exp H: Process
    s_unseen_h = "Pyrolysis converts dense biomass into combustible charcoal and synthetic biogas."
    res_unseen_h = se.extract(s_unseen_h)
    print(f"Novel Exp H - Unseen intent: {res_unseen_h[0].intent_type if res_unseen_h else None}, Entity: {res_unseen_h[0].primary_entity if res_unseen_h else None}")
    assert res_unseen_h and res_unseen_h[0].intent_type == "process", f"Novel Exp H failed: got {res_unseen_h[0].intent_type if res_unseen_h else None}"

    print("ALL GENERALIZATION EXPERIMENTS PASSED!\n")


def run_pronoun_shield_tests():
    se = SemanticExtractor()
    print("=== PRONOUN SHIELD VERIFICATION ===")

    isolated_test_cases = [
        "It is characterized by extreme aridity and sparse vegetation.",
        "They are composed of three concentric geosphere layers.",
        "These are longitudinal compressional vibrations.",
        "This is a massive collection of stars.",
        "It contains immense reserves of metallic minerals.",
        "They have the lowest density among all planets in the Solar System.",
        "Its thickness reaches up to 100 kilometres in oceanic regions.",
        "He proposed the continental drift theory in 1912.",
        "She discovered pulsars in 1967.",
        "These rocks are formed through igneous processes." # Note: demonstrative determiner 'These rocks' SHOULD extract entity 'These rocks'
    ]

    for sentence in isolated_test_cases:
        # Test as raw string
        nodes_str = se.extract(sentence)
        # Test as isolated NormalizedBlock
        block = NormalizedBlock("blk_isolated", sentence, "PROSE", [sentence], {})
        nodes_blk = se.extract(block)

        is_determiner_phrase = sentence.startswith("These rocks")

        if is_determiner_phrase:
            # Demonstrative determiner modifying a noun should extract valid entity
            assert len(nodes_str) >= 1 or len(nodes_blk) >= 1, f"Failed on determiner phrase: {sentence}"
            for n in nodes_str + nodes_blk:
                entity = getattr(n, "primary_entity", getattr(n, "primaryEntity", ""))
                assert entity.lower() not in PRONOUN_TOKENS, f"Leaked pronoun token on determiner: {entity}"
            print(f"Determiner phrase allowed validly: '{sentence}' -> entity: '{nodes_blk[0].primary_entity}'")
        else:
            # Isolated bare pronouns must be completely blocked (0 nodes emitted)
            print(f"Testing isolated pronoun: '{sentence}'")
            print(f"  Result as str: {len(nodes_str)} nodes")
            print(f"  Result as block: {len(nodes_blk)} nodes")
            assert len(nodes_str) == 0, f"LEAKAGE AS STR on '{sentence}': got {nodes_str}"
            assert len(nodes_blk) == 0, f"LEAKAGE AS BLOCK on '{sentence}': got {nodes_blk}"
            for n in nodes_str + nodes_blk:
                entity = getattr(n, "primary_entity", getattr(n, "primaryEntity", ""))
                assert entity.lower() not in PRONOUN_TOKENS, f"LEAKAGE DETECTED: Primary entity '{entity}' in PRONOUN_TOKENS!"

    # Test discourse resolution (grounded pronoun within block)
    print("\nTesting discourse coreference resolution within multi-sentence block:")
    s1 = "The Thar Desert is an arid geographical region in northwestern India."
    s2 = "It is characterized by extreme aridity and sparse vegetation."
    block_multi = NormalizedBlock("blk_multi", f"{s1} {s2}", "PROSE", [s1, s2], {})
    nodes_multi = se.extract(block_multi)

    print(f"Multi-sentence block nodes count: {len(nodes_multi)}")
    for i, n in enumerate(nodes_multi):
        print(f"  Node {i+1}: Intent={n.intent_type}, Entity='{n.primary_entity}', Predicate='{n.predicate}'")

    assert len(nodes_multi) == 2, f"Expected 2 nodes, got {len(nodes_multi)}"
    assert nodes_multi[0].primary_entity in ["Thar Desert", "The Thar Desert"], f"Unexpected node 1 entity: {nodes_multi[0].primary_entity}"
    assert nodes_multi[1].primary_entity == "Thar Desert", f"Expected Node 2 entity 'Thar Desert', got '{nodes_multi[1].primary_entity}'"
    assert nodes_multi[1].primary_entity.lower() not in PRONOUN_TOKENS, "Node 2 entity is a pronoun!"

    # Test plural discourse resolution
    s_plur1 = "Primary waves are fast seismic waves."
    s_plur2 = "They are characterized by high velocity and compressional motion."
    block_plur = NormalizedBlock("blk_plur", f"{s_plur1} {s_plur2}", "PROSE", [s_plur1, s_plur2], {})
    nodes_plur = se.extract(block_plur)

    print(f"\nPlural multi-sentence block nodes count: {len(nodes_plur)}")
    for i, n in enumerate(nodes_plur):
        print(f"  Plural Node {i+1}: Intent={n.intent_type}, Entity='{n.primary_entity}', Predicate='{n.predicate}'")

    assert len(nodes_plur) == 2, f"Expected 2 plural nodes, got {len(nodes_plur)}"
    assert nodes_plur[1].primary_entity == "Primary waves", f"Expected Node 2 entity 'Primary waves', got '{nodes_plur[1].primary_entity}'"
    assert nodes_plur[1].primary_entity.lower() not in PRONOUN_TOKENS, "Plural Node 2 entity is a pronoun!"

    print("\nALL PRONOUN SHIELD TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_empirical_generalization_tests()
    run_pronoun_shield_tests()
