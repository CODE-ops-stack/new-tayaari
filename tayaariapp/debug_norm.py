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

corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

# Node 63
evidence = 'Sol in Roman mythology is the Sungod.'
norm_ev = normalize_for_matching(evidence)
print('Evidence normalized:', repr(norm_ev))

idx = corpus.find('Sol in Roman')
if idx >= 0:
    corp_snippet = corpus[idx:idx+100]
    norm_corp = normalize_for_matching(corp_snippet)
    print('Corpus snippet normalized:', repr(norm_corp))
    print('Exact match:', norm_ev in norm_corp)
else:
    print('Sol in Roman not found in corpus')
    # Search for Sol
    idx = corpus.find('Sol')
    if idx >= 0:
        corp_snippet = corpus[max(0,idx-20):idx+100]
        norm_corp = normalize_for_matching(corp_snippet)
        print('Corpus snippet normalized:', repr(norm_corp))
        print('Exact match:', norm_ev in norm_corp)

# Check subsequence
ev_words = norm_ev.split()
corpus_words = norm_corp.split()
ev_idx = 0
for cw in corpus_words:
    if ev_idx < len(ev_words) and cw == ev_words[ev_idx]:
        ev_idx += 1
print('Subsequence match:', ev_idx == len(ev_words))
print('Words matched:', ev_idx, '/', len(ev_words))
print('Ev words:', ev_words)
print('Corpus words:', corpus_words[:30])

# Node 62
print()
evidence2 = "It is made of two Greek words, ge meaning earth and graphia meaning writing'."
norm_ev2 = normalize_for_matching(evidence2)
print('Evidence2 normalized:', repr(norm_ev2))

idx2 = corpus.find('two Greek words')
if idx2 >= 0:
    corp_snippet2 = corpus[idx2:idx2+150]
    norm_corp2 = normalize_for_matching(corp_snippet2)
    print('Corpus snippet2 normalized:', repr(norm_corp2))
    print('Exact match:', norm_ev2 in norm_corp2)

# Node 52
print()
evidence3 = "Venus is considered as Earths-twin' because its size and shape are very much sim"
norm_ev3 = normalize_for_matching(evidence3)
print('Evidence3 normalized:', repr(norm_ev3))

idx3 = corpus.find('Venus is considered')
if idx3 >= 0:
    corp_snippet3 = corpus[idx3:idx3+200]
    norm_corp3 = normalize_for_matching(corp_snippet3)
    print('Corpus snippet3 normalized:', repr(norm_corp3))
    print('Exact match:', norm_ev3 in norm_corp3)