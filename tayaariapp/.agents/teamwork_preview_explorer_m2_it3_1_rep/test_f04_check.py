import re

pat_part_of = re.compile(
    r'^(?:(?:\b(?:The|An|A|Our)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:is|forms?|constitutes?)\s+(?:an?|the)?\s*(?:[a-z\-]+\s+)*(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|portion)\s+(?:(?:located|situated|found)\s+)?(?:of|within|in)\b.*|(?:is|forms?|constitutes?)\s+(?:about|approximately|around|nearly)?\s*[\d\.]+(?:%|\s*percent)\s+of\s+.*?\band\s+(?:lies|extends|forms)\b.*|(?:(?:is|are)\s+(?:composed|made up|constituted)\s+of|consists?\s+of)\s*:?\s*.*|\bforms?\s+part of\b.*|component of.*|part of the.*|part of.*)$',
    re.IGNORECASE
)

text_f04 = "The mantle constitutes about 84% of Earth's volume and lies between the crust and outer core."
m_f04 = pat_part_of.match(text_f04)
print("text_f04 (mantle) matched part-of:", bool(m_f04))

text_p29 = "The Sun constitutes approximately 99.86 percent of the total cumulative mass of the entire Solar System, with the majority of the remainder concentrated in Jupiter."
m_p29 = pat_part_of.match(text_p29)
print("text_p29 (Sun) matched part-of (should be False):", bool(m_p29))
