import sys
sys.path.insert(0, ".")
from v13_discovery.question_synthesizer import (
    OntologyRegistry,
    QuestionSynthesizer,
    DistractorVerificationGate,
)
from v13_discovery.semantic_extractor import KnowledgeNode

ontology = OntologyRegistry()
cat_circ = ontology.get_category("circulation_cells")
cat_clim = ontology.get_category("climatic_phenomena")

print("=== Checking Ontology Membership for 'Hadley cell' ===")
print("Is 'Hadley cell' in circulation_cells?", "Hadley cell" in cat_circ.members)
print("Is 'Hadley cell' in climatic_phenomena?", "Hadley cell" in cat_clim.members)
resolved_cat = ontology.find_category_for_entity("Hadley cell")
print("Resolved category:", resolved_cat.category_id if resolved_cat else None)

synth = QuestionSynthesizer(ontology)
node = KnowledgeNode(
    node_id="node_hadley_verification",
    intent_type="definition",
    primary_entity="Hadley cell",
    predicate="is an atmospheric circulation cell",
    secondary_entities=[],
    conditions=[],
    quantitative_data=None,
    raw_evidence="The Hadley cell is a low-latitude overturning circulation with rising air near the equator.",
    source_location={"sourceId": "test.txt", "line": 1, "offset": 0},
    confidence=1.0
)

print("\n=== Synthesizing Question for 'Hadley cell' ===")
cq = synth.synthesize(node)
print("Stem:", cq.stem)
print("Options:", cq.options)
print("Correct Answer:", cq.correctAnswer)

is_valid, errors = DistractorVerificationGate.check_category_compatibility(cq.options, cat_circ)
print("\n=== Category Compatibility Gate Check against 'circulation_cells' ===")
print("Gate Valid?:", is_valid)
print("Errors:", errors)

circulation_members = {m.lower() for m in cat_circ.members}
all_in_circulation = all(opt.strip().lower() in circulation_members for opt in cq.options.values())
print("All options exclusively from circulation_cells?:", all_in_circulation)

assert is_valid, f"Verification gate failed: {errors}"
assert all_in_circulation, f"Non-circulation distractors found: {cq.options}"
print("\nHadley cell test: PASS")
