import re

pat_part_of = re.compile(
    r'^(?:(?:\b(?:The|An|A|Our)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:(?:is|forms?|constitutes?)\s+(?:an?|the)?\s*(?:[a-z\-]+\s+)*(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|portion)\s+(?:(?:located|situated|found)\s+)?(?:of|within|in)\b|(?:is|are)\s+(?:composed|made up|constituted)\s+of\b|consists?\s+of\b|\bforms?\s+part of\b|component of|part of the|part of)\s*:?\s*(?P<pred>.*)$',
    re.IGNORECASE
)

text51 = "Our Solar System forms a small peripheral stellar component located within the Orion-Cygnus spiral arm of the Milky Way galaxy."
m51 = pat_part_of.match(text51)
print("text51 match:", bool(m51))
if m51:
    print("  entity:", m51.group("entity"))
    print("  pred:", m51.group("pred")[:60])
