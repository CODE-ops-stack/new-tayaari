import ast
import json
import re
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

# Load existing files
with open(os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py"), encoding="utf-8") as f:
    se_code = f.read()

with open(os.path.join(REPO_ROOT, "v13_discovery", "normalizer.py"), encoding="utf-8") as f:
    norm_code = f.read()

with open(os.path.join(REPO_ROOT, "data", "golden_eval_set.json"), encoding="utf-8") as f:
    eval_set = json.load(f)

print("=== APPLYING SHADOW REMEDIATIONS (E1 + E2 + E3) ===")

# --- Explorer 1 Remediations ---
# 1. Quantity pattern (line 738)
se_mod = se_code.replace(
    'maintains a constant tilt of|measures approximately|originated approximately',
    r'(?:has|have|had|maintains?|maintained|exhibits?|possesses?)\s+(?:an?|a\s+constant)?\s*(?:[a-z\-]+\s+)?(?:radius|diameter|circumference|elevation|altitude|depth|density|mass|volume|area|tilt|inclination|angle)\s+of|measures approximately|originated approximately'
)

# 2. Sequence pattern (line 716)
se_mod = se_mod.replace(
    'commenced approximately.*followed by|arrive(?:s)? first.*followed sequentially by',
    r'(?:arrive(?:s|d)?|form(?:s|ed)?|condense(?:s|d)?|begin(?:s)?|began|commence(?:s|d)?)\b.*?\bfollowed\s+(?:by|sequentially\s+by|in\s+turn\s+by)'
)

# 3. Superlative verbs (line 776)
se_mod = se_mod.replace(
    r'(?:highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)',
    r'(?:[a-z\-]+est|highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)'
)
se_mod = se_mod.replace(
    '(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed)',
    '(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed|produced|generated|emitted|yielded)'
)

# 3b. Line 983 match_decl verb list
se_mod = se_mod.replace(
    'orbits?|rotates?|flows?)',
    'orbits?|rotates?|flows?|produced?|generated?|emitted?|yielded?)'
)

# 4. Attribute adverbs (line 792)
se_mod = se_mod.replace(
    r'(?:are|is)\s+(?:very|extremely|highly|mostly)?\s*[a-z\-]+\s+and\s+[a-z\-]+',
    r'(?:are|is)\s+(?:[a-z\-]+ly\s+|very\s+|mostly\s+)?\s*[a-z\-]+\s+and\s+[a-z\-]+'
)

# 5. Fallback declarative attr_verbs (line 1001)
se_mod = se_mod.replace(
    'attr_verbs = {"exhibits", "possesses", "displays", "maintains", "features", "contains", "demonstrates", "reveals"}',
    'attr_verbs = {"exhibits", "possesses", "displays", "maintains", "features", "contains", "demonstrates", "reveals", "produced", "produce", "generated", "generate", "emitted", "emit", "yielded", "yield"}'
)

# --- Explorer 2 Remediations ---
# 6. NoiseFilterGate fragment pattern (line 550)
se_mod = se_mod.replace(
    r"r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$',",
    r"r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$',"
)

# 7. NoiseFilterGate broken_reading_order (line 569)
se_mod = se_mod.replace(
    r"r'\b(?:[A-Z][a-z]+\s+){5,}',",
    r"r'^(?![^.\n]*\b(?:is|are|was|were|has|have|orbits?|contains?|features?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$',"
)

# 8. Normalizer split_merged_headers (lines 196-202)
old_norm_block = """        s = re.sub(r'UniverseGalaxySolar System', 'Universe. Galaxy. Solar System.', s)
        s = re.sub(r'Planetesimal TheoryNebular HypothesisCopernicus Theory', 'Planetesimal Theory. Nebular Hypothesis. Copernicus Theory.', s)
        s = re.sub(r'MeteoroidMeteorMeteorite', 'Meteoroid. Meteor. Meteorite.', s)
        s = re.sub(r'PhotosphereChromosphereCorona', 'Photosphere. Chromosphere. Corona.', s)
        s = re.sub(r'Terrestrial PlanetsJovian Planets', 'Terrestrial Planets vs Jovian Planets.', s)
        s = re.sub(r'Three Types of Plate BoundariesThree Types of Plate Boundaries', 'Three Types of Plate Boundaries:', s)"""

new_norm_block = """        # Deduplicate repeated multi-token phrases from table / header collisions
        s = re.sub(r'\\b(.{10,200}?)\\s*\\1\\b', r'\\1', s)
        # Generalized split for concatenated PascalCase / camelCase tokens
        s = re.sub(r'([a-z])([A-Z])', r'\\1 \\2', s)
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\\1 \\2', s)"""

norm_mod = norm_code.replace(old_norm_block, new_norm_block)

# --- Explorer 3 Remediations ---
# 9. Part-of containment nouns in Pattern 11 (line 754)
se_mod = se_mod.replace(
    r'(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion)',
    r'(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion|shield|barrier|reservoir|body|mass)'
)

print("Shadow replacements complete. Compiling modules in memory...")

# Execute shadow modules in dedicated namespaces
norm_ns = {}
exec(norm_mod, norm_ns)

se_ns = {
    'DocumentNormalizer': norm_ns['DocumentNormalizer'],
    'NormalizedBlock': norm_ns['NormalizedBlock'],
}
exec(se_mod, se_ns)

SemanticExtractor = se_ns['SemanticExtractor']
NoiseFilterGate = se_ns['NoiseFilterGate']
canonicalize_intent = se_ns['canonicalize_intent']

extractor = SemanticExtractor()

print("\n--- TEST 1: Ozone Layer Protective Atmospheric Shield ---")
s_ozone = "The ozone layer constitutes a protective atmospheric shield located within the lower stratosphere."
nodes = extractor.extract(s_ozone)
print(f"Ozone extraction nodes count: {len(nodes)}")
if nodes:
    print(f"Intent: {canonicalize_intent(nodes[0].intent_type)}")
    print(f"Entity: {nodes[0].primary_entity}")
    print(f"Secondary: {nodes[0].secondary_entities}")
    assert canonicalize_intent(nodes[0].intent_type) == "part_of", f"Expected part_of, got {nodes[0].intent_type}"
    print("[PASS] Ozone layer correctly extracted as part_of!")
else:
    print("[FAIL] Ozone layer failed to extract!")

print("\n--- TEST 2: James Webb Space Telescope (5 TitleCase tokens) ---")
s_jwst = "The James Webb Space Telescope is an optical space observatory orbiting the Sun-Earth L2 Lagrange point."
audit_res = NoiseFilterGate.audit(s_jwst)
print(f"NoiseFilterGate.audit: {audit_res}")
assert audit_res is None, f"Expected None, got {audit_res}"
nodes_jwst = extractor.extract(s_jwst)
print(f"JWST nodes count: {len(nodes_jwst)}")
assert len(nodes_jwst) >= 1, "Failed to extract JWST node"
print(f"JWST Intent: {canonicalize_intent(nodes_jwst[0].intent_type)}")
print("[PASS] JWST not falsely rejected by reading order filter!")

print("\n--- TEST 3: Past-tense Superlative 'produced' ---")
s_krak = "The Krakatoa eruption of 1883 produced the loudest acoustic sound in recorded history."
nodes_krak = extractor.extract(s_krak)
print(f"Krakatoa nodes count: {len(nodes_krak)}")
assert len(nodes_krak) >= 1, "Failed to extract Krakatoa node"
print(f"Krakatoa Intent: {canonicalize_intent(nodes_krak[0].intent_type)}")
assert canonicalize_intent(nodes_krak[0].intent_type) == "attribute"
print("[PASS] Krakatoa past-tense superlative 'produced' correctly extracted as attribute!")

print("\n--- TEST 4: Adverb generalization in compound attributes ---")
s_cumu = "Cumulonimbus clouds are unusually tall and turbulent, producing severe localized thunderstorms."
nodes_cumu = extractor.extract(s_cumu)
print(f"Cumulonimbus nodes count: {len(nodes_cumu)}")
assert len(nodes_cumu) >= 1, "Failed to extract Cumulonimbus node"
print(f"Cumulonimbus Intent: {canonicalize_intent(nodes_cumu[0].intent_type)}")
assert canonicalize_intent(nodes_cumu[0].intent_type) == "attribute"
print("[PASS] 'unusually' tall and turbulent correctly extracted as attribute!")

print("\n--- TEST 5: Golden Eval Set Item POS-032 & Unseen Variants ---")
s_gold_32 = "The Earth's axis of rotation maintains a constant tilt of 66.5 degrees relative to its orbital plane."
s_unseen_32a = "The Earth's axis of rotation maintains an axial tilt of 23.5 degrees relative to its orbital plane."
s_unseen_32b = "Mars maintains an axial inclination of 25.2 degrees relative to its orbital plane."
n_g32 = extractor.extract(s_gold_32)
n_u32a = extractor.extract(s_unseen_32a)
n_u32b = extractor.extract(s_unseen_32b)
assert n_g32 and canonicalize_intent(n_g32[0].intent_type) == "quantity"
assert n_u32a and canonicalize_intent(n_u32a[0].intent_type) == "quantity"
assert n_u32b and canonicalize_intent(n_u32b[0].intent_type) == "quantity"
print("[PASS] Quantity pattern generalizes across golden POS-032 and unseen axial tilt/inclination!")

print("\n--- TEST 6: Golden Eval Set Item POS-034/036 & Unseen Sequence Variants ---")
s_gold_34 = "The genesis of the Solar System commenced approximately 4.8 billion years ago with the gravitational collapse of a giant molecular cloud, followed by the formation of a rotating accretion disk."
s_gold_36 = "During an earthquake rupture, high-velocity primary (P) waves arrive first at seismic monitoring stations, followed sequentially by secondary (S) shear waves, and concluded by destructive high-amplitude surface waves."
s_unseen_seq = "During cell division, chromosomes condense first in the nucleus, followed in turn by spindle attachment and nuclear envelope breakdown."
n_g34 = extractor.extract(s_gold_34)
n_g36 = extractor.extract(s_gold_36)
n_useq = extractor.extract(s_unseen_seq)
assert n_g34 and canonicalize_intent(n_g34[0].intent_type) == "sequence"
assert n_g36 and canonicalize_intent(n_g36[0].intent_type) == "sequence"
assert n_useq and canonicalize_intent(n_useq[0].intent_type) == "sequence"
print("[PASS] Sequence pattern generalizes across POS-034, POS-036, and unseen biological sequences!")

print("\n--- TEST 7: Golden Eval Set Item NEG-021 & Unseen Fragment Variants ---")
s_neg_21 = "Out of total water resources"
s_unseen_frag = "Out of total forest resources"
audit_21 = NoiseFilterGate.audit(s_neg_21)
audit_frag = NoiseFilterGate.audit(s_unseen_frag)
assert audit_21 == "syntactic_fragment"
assert audit_frag == "syntactic_fragment"
print("[PASS] NoiseFilterGate correctly rejects both NEG-021 and unseen 'Out of total forest resources' as syntactic_fragment!")

print("\n--- TEST 8: Full 111-Item Golden Eval Set Benchmark ---")
positives = [it for it in eval_set['examples'] if it['expected_label'] == 'positive']
negatives = [it for it in eval_set['examples'] if it['expected_label'] == 'negative']
print(f"Loaded {len(positives)} positive items, {len(negatives)} negative items.")

pos_passed = 0
pos_failed = []
for it in positives:
    nds = extractor.extract(it['text'])
    if nds and len(nds) >= 1:
        # Check intent match if specified
        exp_intent = it.get('intent')
        act_intent = canonicalize_intent(nds[0].intent_type)
        if exp_intent and exp_intent != "none":
            if act_intent == canonicalize_intent(exp_intent):
                pos_passed += 1
            else:
                pos_failed.append((it['id'], f"Intent mismatch: exp '{exp_intent}', got '{act_intent}'", it['text'][:50]))
        else:
            pos_passed += 1
    else:
        pos_failed.append((it['id'], "No nodes extracted", it['text'][:50]))

print(f"Positive Items: {pos_passed}/{len(positives)} PASSED")
if pos_failed:
    print(f"Positive Failures ({len(pos_failed)}):")
    for f in pos_failed:
        print(f"  [{f[0]}]: {f[1]} -> '{f[2]}'")

neg_rejected = 0
neg_accepted = []
for it in negatives:
    nds = extractor.extract(it['text'])
    if not nds or len(nds) == 0:
        neg_rejected += 1
    else:
        neg_accepted.append((it['id'], len(nds), it['text'][:50]))

print(f"Negative Items: {neg_rejected}/{len(negatives)} REJECTED")
if neg_accepted:
    print(f"Negative False Acceptances ({len(neg_accepted)}):")
    for fa in neg_accepted:
        print(f"  [{fa[0]}]: falsely extracted {fa[1]} nodes -> '{fa[2]}'")

assert pos_passed == len(positives), f"Only {pos_passed}/{len(positives)} positive items passed"
assert neg_rejected == len(negatives), f"Only {neg_rejected}/{len(negatives)} negative items rejected"

print("\n=======================================================")
print(">>> ALL 111 GOLDEN EVALUATION SET ITEMS VALIDATED 100%! <<<")
print("=======================================================")
