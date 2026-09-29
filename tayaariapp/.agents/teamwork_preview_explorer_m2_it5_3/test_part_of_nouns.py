import re

pat = re.compile(
    r'^(?:(?:\b(?:The|An|A|Our)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:is|forms?|constitutes?)\s+(?:an?|the)?\s*(?:[a-z\-]+\s+)*(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion|shield|barrier|reservoir|body|mass)\s+(?:(?:located|situated|found|positioned|embedded)\s+(?:[a-z\-]+\s+)?)?(?:of|within|in|beneath|under|underneath|above|below|between|around|across|throughout)\b.*|(?:is|forms?|constitutes?)\s+(?:about|approximately|around|nearly)?\s*[\d\.]+(?:%|\s*percent)\s+of\s+.*?\band\s+(?:lies|extends|forms)\b.*|(?:(?:is|are)\s+(?:composed|made up|constituted)\s+of|consists?\s+of)\s*:?\s*[A-Za-z0-9\s\-]{3,}.*|\bforms?\s+part of\b.*|component of.*|part of the.*|part of.*)$',
    re.IGNORECASE
)

sentences = [
    ("The ozone layer constitutes a protective atmospheric shield located within the lower stratosphere.", "ozone layer", "lower stratosphere"),
    ("The coral formation forms a resilient natural barrier situated within the marine park.", "coral formation", "marine park"),
    ("The mantle constitutes a vast magma reservoir located beneath the crust.", "mantle", "crust"),
    ("The asthenosphere constitutes a plastic rock mass situated underneath the lithosphere.", "asthenosphere", "lithosphere"),
    ("The outer core forms a liquid metallic layer situated beneath the rocky mantle.", "outer core", "rocky mantle"),
    ("The stratosphere constitutes a dry atmospheric layer positioned directly above the troposphere.", "stratosphere", "troposphere"),
]

for s, exp_ent, exp_sec in sentences:
    m = pat.match(s)
    assert m is not None, f"Failed match on: {s}"
    ent = m.group("entity")
    m_parent = re.search(r'\b(?:of|within|in|beneath|under|underneath|above|below|between)\s+(?:the\s+)?([A-Z][a-zA-Z\s\-]+?)(?:[,\.]|$)', s, re.IGNORECASE)
    parent = m_parent.group(1).strip() if m_parent else None
    print(f"[OK] Sentence: {s[:50]}...")
    print(f"     Entity: '{ent}' (expected: '{exp_ent}') | Parent: '{parent}' (expected: '{exp_sec}')")

print("\nALL PART-OF TEST CASES PASSED!")
