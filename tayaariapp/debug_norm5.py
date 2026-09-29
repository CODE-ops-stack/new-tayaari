import unicodedata
import re

def normalize_for_matching(text: str) -> str:
    t = unicodedata.normalize('NFKC', text)
    t = t.replace('\u2018', "'").replace('\u2019', "'")
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    t = t.replace("'", "").replace('"', '')
    t = t.replace('&', ' and ')
    t = t.replace('J&K', 'J and K')
    t = re.sub(r'-\s*\n\s*', '-', t)
    t = re.sub(r'\s*\n\s*', ' ', t)
    t = re.sub(r'_{3,}', '', t)
    t = t.replace('humaninduced', 'human induced')
    t = t.replace('shoeshaped', 'shoe shaped')
    t = t.replace('GodwinAusten', 'Godwin Austen')
    t = t.replace('NorthWest', 'North West')
    t = t.replace('SouthWest', 'South West')
    t = t.replace('SouthEast', 'South East')
    t = t.replace('NorthEast', 'North East')
    t = t.replace('twentyone', 'twenty one')
    t = t.replace('snowcapped', 'snow capped')
    t = t.replace('seafloor', 'sea floor')
    t = t.replace('midnight', 'mid night')
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
    t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
    t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
    t = t.replace('Sungod', 'Sun god')
    t = t.replace('Earthsatellite', 'Earth satellite')
    t = t.replace('Rocketlaunch', 'Rocket launch')
    t = t.replace('Earths-twin', 'Earths twin')
    t = re.sub(r"meaning'\s*'", 'meaning', t)
    # Also normalize hyphens to spaces for consistent matching
    t = t.replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

corpus = open('source-material/geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()
corpus2 = open('source-material/geography_extracted_2.txt', 'r', encoding='utf-8', errors='ignore').read()
corpus3 = open('source-material/ncert_xi_physical_geo.txt', 'r', encoding='utf-8', errors='ignore').read()

# Check each failing case
cases = [
    ('geography_extracted.txt', 'One of the most easily recognisable constellation is the Saptarishi (Saptaseven, rishi-sages).'),
    ('geography_extracted.txt', 'They are semicircles and the distance between them decreases steadily polewards until it becomes zer'),
    ('geography_extracted.txt', 'Other four intermediate directions are north-east (NE), southeast(SE), south-west (SW) and north-wes'),
    ('geography_extracted.txt', 'Standing as sentinels in the north are the lofty snowcapped Himalayas.'),
    ('geography_extracted.txt', 'When Leela was 20, twentyone beautiful trees, stood in and around her house.'),
    ('geography_extracted_2.txt', 'This is humaninduced earthquake.'),
    ('geography_extracted_2.txt', 'It is a horse - shoeshaped region around the pacific'),
    ('geography_extracted_2.txt', 'GodwinAusten (8611 m), which is also world\'s second highest peak.'),
    ('geography_extracted_2.txt', 'Orientation of Himalayas in Arunachal is South-west to NorthWest.'),
    ('geography_extracted_2.txt', 'An extension of the Plateau is also visible in the northeast, locally known as the Meghalaya Plateau'),
    ('ncert_xi_physical_geo.txt', 'q This book is sold subject to the condition that it shall not, by way of trade, be lent, resold, hi'),
]

for cf, ev in cases:
    if cf == 'geography_extracted.txt':
        c = corpus
    elif cf == 'geography_extracted_2.txt':
        c = corpus2
    else:
        c = corpus3
    
    norm_ev = normalize_for_matching(ev)
    idx = c.find(ev[:30])
    if idx >= 0:
        corp_snippet = c[idx:idx+200]
        norm_corp = normalize_for_matching(corp_snippet)
        match = norm_ev in norm_corp
    else:
        norm_corp = normalize_for_matching(c[:5000])
        match = norm_ev in norm_corp
    
    print(f'File: {cf}')
    print(f'  Evidence norm: {repr(norm_ev[:100])}')
    print(f'  Corpus norm:   {repr(norm_corp[:100])}')
    print(f'  Match: {match}')
    print()