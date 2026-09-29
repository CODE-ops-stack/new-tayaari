corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

import unicodedata
import re

def normalize_for_matching(text: str) -> str:
    t = unicodedata.normalize('NFKC', text)
    t = t.replace('\u2018', "'").replace('\u2019', "'")
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    t = re.sub(r'-\s*\n\s*', '', t)
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
    t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
    t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
    t = t.replace('Sungod', 'Sun god')
    t = t.replace('Earthsatellite', 'Earth satellite')
    t = t.replace('Rocketlaunch', 'Rocket launch')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

norm_corpus = normalize_for_matching(corpus)

# Check Node 63
evidence = 'Sol in Roman mythology is the Sungod.'
norm_ev = normalize_for_matching(evidence)
print('Evidence normalized:', repr(norm_ev))
print('In corpus:', norm_ev in norm_corpus)

# Check Node 62
evidence2 = "It is made of two Greek words, ge meaning earth and graphia meaning writing'."
norm_ev2 = normalize_for_matching(evidence2)
print()
print('Evidence2 normalized:', repr(norm_ev2))
print('In corpus:', norm_ev2 in norm_corpus)

# Check Node 52
evidence3 = "Venus is considered as Earths-twin' because its size and shape are very much sim"
norm_ev3 = normalize_for_matching(evidence3)
print()
print('Evidence3 normalized:', repr(norm_ev3))
print('In corpus:', norm_ev3 in norm_corpus)