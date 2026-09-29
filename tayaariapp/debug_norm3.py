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

# Find the relevant sections in normalized corpus
for keyword in ['Sol in Roman', 'two Greek words', 'Venus is considered']:
    idx = norm_corpus.find(keyword)
    if idx >= 0:
        print(f'Found "{keyword}" at {idx}:')
        print(repr(norm_corpus[idx:idx+200]))
    else:
        print(f'NOT FOUND: "{keyword}"')
    print()