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

evidence = 'They are semicircles and the distance between them decreases steadily polewards until it becomes zer'
norm_ev = normalize_for_matching(evidence)
ev_words = norm_ev.split()

corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()
norm_corpus = normalize_for_matching(corpus)
corpus_words = norm_corpus.split()

# Simulate subsequence matching
ev_idx = 0
matched_words = []
for i, cw in enumerate(corpus_words):
    if ev_idx < len(ev_words):
        ew = ev_words[ev_idx]
        if cw == ew:
            matched_words.append((ev_idx, ew, i, cw))
            ev_idx += 1
        elif ev_idx == len(ev_words) - 1 and cw.startswith(ew) and len(ew) >= 3:
            matched_words.append((ev_idx, ew, i, cw))
            ev_idx += 1

print(f'Matched {ev_idx}/{len(ev_words)} words')
print('Matched words:')
for m in matched_words:
    print(f'  ev[{m[0]}]={m[1]} -> corpus[{m[2]}]={m[3]}')

if ev_idx < len(ev_words):
    print(f'\nFirst unmatched: ev[{ev_idx}] = {ev_words[ev_idx]}')
    # Find this word in corpus
    for i, cw in enumerate(corpus_words):
        if cw == ev_words[ev_idx]:
            print(f'  Found at corpus[{i}]')
            break
    else:
        print(f'  NOT FOUND in corpus')