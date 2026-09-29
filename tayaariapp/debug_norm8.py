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

norm_corpus = normalize_for_matching(corpus)
words = norm_corpus.split()

# Check for Sapta
found = False
for i, w in enumerate(words):
    if 'Sapta' in w:
        print('Found at index {}: {}'.format(i, w))
        found = True
        break
if not found:
    print('Sapta NOT FOUND in corpus words')
    # Check for Sapta-seven
    for i, w in enumerate(words):
        if 'Sapta-seven' in w or 'Sapta seven' in w:
            print('Found Sapta-seven at index {}: {}'.format(i, w))
            found = True
            break
    if not found:
        print('Sapta-seven also NOT FOUND')
        # Check raw corpus for Sapta
        if 'Sapta' in norm_corpus:
            print('But Sapta IS in normalized corpus string')
        else:
            print('Sapta NOT in normalized corpus string either')