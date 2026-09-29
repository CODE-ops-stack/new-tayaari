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
    t = t.replace('southwest', 'south west')
    t = t.replace('southeast', 'south east')
    t = t.replace('northwest', 'north west')
    t = t.replace('northeast', 'north east')
    t = t.replace('twentyone', 'twenty one')
    t = t.replace('snowcapped', 'snow capped')
    t = t.replace('seafloor', 'sea floor')
    t = t.replace('midnight', 'mid night')
    t = t.replace('Saptaseven', 'Sapta seven')
    t = t.replace('semicircles', 'semi circles')
    t = t.replace('semiannual', 'semi annual')
    t = t.replace('semifinal', 'semi final')
    t = t.replace('semipermanent', 'semi permanent')
    t = t.replace('semiconductor', 'semi conductor')
    t = t.replace('Coed', 'concerted')
    t = t.replace('Coed', 'concerted')
    t = t.replace('Saptaseven', 'Sapta seven')
    t = t.replace('\ufffd', '')
    t = t.replace('\u2014', ' ')
    t = t.replace('\u2013', ' ')
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
    t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
    t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
    t = t.replace('Sungod', 'Sun god')
    t = t.replace('Earthsatellite', 'Earth satellite')
    t = t.replace('Rocketlaunch', 'Rocket launch')
    t = t.replace('Earths-twin', 'Earths twin')
    t = re.sub(r"meaning'\s*'", 'meaning', t)
    t = t.replace('-', ' ')
    t = t.replace('\u2014', ' ')
    t = t.replace('\u2013', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

evidence = 'Project in Bharmaur Region Bharmaur tribal area comprises Bharmaur and Holi tehsils of Chamba distri'
corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_india_economy.txt', 'r', encoding='utf-8', errors='ignore').read()

# Find the relevant corpus snippet
idx = corpus.find('Bharmaur tribal area')
corpus_snippet = corpus[max(0,idx-50):idx+200]

norm_ev = normalize_for_matching(evidence)
norm_corpus = normalize_for_matching(corpus_snippet)

print('Norm evidence:', repr(norm_ev))
print('Norm corpus:', repr(norm_corpus))
print('Exact match:', norm_ev in norm_corpus)

# Check prefix match for last word
ev_words = norm_ev.split()
corpus_words = norm_corpus.split()
last_ew = ev_words[-1]
print(f'Last evidence word: {last_ew}')
for i, cw in enumerate(corpus_words):
    if cw.startswith(last_ew) and len(last_ew) >= 3:
        print(f'Prefix match: corpus_words[{i}] = {cw}')
        break