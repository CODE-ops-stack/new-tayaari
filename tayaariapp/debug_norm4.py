import unicodedata
import re

def normalize_for_matching(text: str) -> str:
    t = unicodedata.normalize('NFKC', text)
    t = t.replace('\u2018', "'").replace('\u2019', "'")
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    t = t.replace("'", "").replace('"', '')
    t = t.replace('&', ' and ')
    t = t.replace('J&K', 'J and K')
    t = re.sub(r'-\s*\n\s*', '', t)
    t = re.sub(r'\s*\n\s*', ' ', t)
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
    t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
    t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
    t = t.replace('Sungod', 'Sun god')
    t = t.replace('Earthsatellite', 'Earth satellite')
    t = t.replace('Rocketlaunch', 'Rocket launch')
    t = t.replace('Earths-twin', 'Earths twin')
    t = re.sub(r"meaning'\s*'", 'meaning', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

corpus = open('source-material/geography_extracted_2.txt', 'r', encoding='utf-8', errors='ignore').read()
corpus1 = open('source-material/geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

# Check BADP
evidence = 'Programme (BADP) was introduced during the 7th Five-Year Plan (1985-1990) in India.'
norm_ev = normalize_for_matching(evidence)
print('Evidence normalized:', repr(norm_ev))

idx = corpus.find('Programme (BADP)')
if idx >= 0:
    corp_snippet = corpus[idx:idx+200]
    norm_corp = normalize_for_matching(corp_snippet)
    print('Corpus snippet normalized:', repr(norm_corp))
    print('Exact match:', norm_ev in norm_corp)

# Check S-Waves
evidence2 = 'They are of two types : P-Waves and S-'
norm_ev2 = normalize_for_matching(evidence2)
print()
print('Evidence2 normalized:', repr(norm_ev2))

idx2 = corpus.find('They are of two types')
if idx2 >= 0:
    corp_snippet2 = corpus[idx2:idx2+200]
    norm_corp2 = normalize_for_matching(corp_snippet2)
    print('Corpus snippet2 normalized:', repr(norm_corp2))
    print('Exact match:', norm_ev2 in norm_corp2)

# Check Himalayas
evidence3 = 'The Himalayas and the Alps are examples of ___________types of mountains.'
norm_ev3 = normalize_for_matching(evidence3)
print()
print('Evidence3 normalized:', repr(norm_ev3))

idx3 = corpus1.find('Himalayas and the Alps')
if idx3 >= 0:
    corp_snippet3 = corpus1[idx3:idx3+200]
    norm_corp3 = normalize_for_matching(corp_snippet3)
    print('Corpus snippet3 normalized:', repr(norm_corp3))
    print('Exact match:', norm_ev3 in norm_corp3)