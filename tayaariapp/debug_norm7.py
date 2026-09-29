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
    t = t.replace('Saptaseven', 'Sapta seven')
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
    t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
    t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
    t = t.replace('Sungod', 'Sun god')
    t = t.replace('Earthsatellite', 'Earth satellite')
    t = t.replace('Rocketlaunch', 'Rocket launch')
    t = t.replace('Earths-twin', 'Earths twin')
    t = re.sub(r"meaning'\s*'", 'meaning', t)
    t = t.replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

# Check the Saptarishi area
idx = corpus.find('Saptarishi')
snippet = corpus[max(0,idx-50):idx+200]
norm_snippet = normalize_for_matching(snippet)
print('Normalized snippet:')
print(repr(norm_snippet))
print()
print('Words around Sapta:')
words = norm_snippet.split()
for i, w in enumerate(words):
    if 'Sapta' in w or 'seven' in w:
        print('  [{}] {}'.format(i, w))