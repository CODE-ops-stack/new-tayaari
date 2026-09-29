import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
import re
from v13_discovery.semantic_extractor import LinguisticSemanticExtractor, canonicalize_intent

with open('data/golden_eval_set.json', encoding='utf-8') as f:
    data = json.load(f)

positives = [p for p in data['examples'] if p['expected_label'] == 'positive']

extractor = LinguisticSemanticExtractor()

print(f"{'ID':<8} | {'EXPECTED':<14} | {'MATCHED VIA':<25} | {'GOT INTENT':<14} | {'PRIMARY ENTITY'}")
print("-" * 100)

for p in positives:
    clean_text = p['text'].strip()
    clean_text = re.sub(r'^\s*(?:\[[A-Za-z0-9]+\]|\(?[A-Za-z0-9ivxlcdmIVXLCDM]+\)[\s\.\)]|\d+[\.\)])\s*', '', clean_text)
    
    # Check locative
    m_loc = extractor.LOCATIVE_INV_REGEX.match(clean_text)
    if m_loc:
        print(f"{p['id']:<8} | {p['intent']:<14} | {'LOCATIVE_INV_REGEX':<25} | {'spatial':<14} | {m_loc.group('entity')}")
        continue
        
    m_pass = extractor.PASSIVE_DEF_REGEX.match(clean_text)
    if m_pass:
        print(f"{p['id']:<8} | {p['intent']:<14} | {'PASSIVE_DEF_REGEX':<25} | {'definition':<14} | {m_pass.group('term')}")
        continue

    working_text = clean_text
    while True:
        m_intro = extractor.INTRO_PREP_REGEX.match(working_text)
        if not m_intro:
            break
        working_text = working_text[len(m_intro.group(0)):].strip()

    matched_pat = None
    for idx, (intent, pat) in enumerate(extractor.PATTERNS):
        m = pat.match(working_text) or pat.match(clean_text)
        if m:
            matched_pat = (idx, intent, pat, m)
            break
            
    if matched_pat:
        idx, intent, pat, m = matched_pat
        entity = m.groupdict().get("entity") or m.groupdict().get("target") or ""
        print(f"{p['id']:<8} | {p['intent']:<14} | {f'PATTERNS[{idx}] {intent}':<25} | {intent:<14} | {entity}")
        continue

    match_decl = re.match(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|form|forms|occurs|constitutes|contains|features|progresses|develops|comprises|falls)\s+(?P<rest>.*)',
        working_text,
        re.IGNORECASE
    )
    if match_decl:
        verb = match_decl.group('verb')
        intent = "definition" if verb in {"is", "are"} else "attribute"
        entity = match_decl.group('entity')
        print(f"{p['id']:<8} | {p['intent']:<14} | {'FALLBACK DECLARATIVE':<25} | {intent:<14} | {entity}")
        continue

    print(f"{p['id']:<8} | {p['intent']:<14} | {'*** NO MATCH ***':<25} | {'None':<14} | -")
