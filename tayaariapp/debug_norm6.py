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
    t = t.replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

evidence = 'One of the most easily recognisable constellation is the Saptarishi (Saptaseven, rishi-sages).'
norm_ev = normalize_for_matching(evidence)
print('Evidence norm:', repr(norm_ev))

# Find in corpus
idx = corpus.find('recognisable')
if idx >= 0:
    corp_snippet = corpus[max(0,idx-50):idx+200]
    norm_corp = normalize_for_matching(corp_snippet)
    print('Corpus snippet norm:', repr(norm_corp))
    print('Match:', norm_ev in norm_corp)
else:
    print('recognisable not found in corpus')