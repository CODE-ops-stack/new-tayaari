import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")

import re
import html
import unicodedata
import uuid
import v13_discovery.semantic_extractor as sem_mod
from v13_discovery.semantic_extractor import KnowledgeNode, SemanticExtractor, LinguisticSemanticExtractor

# Update PATTERNS
new_patterns = []
for intent, pat in sem_mod.LinguisticSemanticExtractor.PATTERNS:
    if intent == "spatial" and "extends up to" in pat.pattern:
        new_pat = re.compile(
            pat.pattern.replace("extends up to", "extends (?:up to|from|between|to)?"),
            re.IGNORECASE
        )
        new_patterns.append((intent, new_pat))
    elif intent == "classification" and pat.pattern.startswith(r'^(?:(?P<subject>'):
        # Add active divides ... into
        active_divide_pat = re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:divides?|classif(?:y|ies)|categoriz(?:es|e)|groups?)\s+(?P<pred>.*?into\s+.*)$',
            re.IGNORECASE
        )
        new_patterns.append((intent, active_divide_pat))
        new_patterns.append((intent, pat))
    else:
        new_patterns.append((intent, pat))

sem_mod.LinguisticSemanticExtractor.PATTERNS = new_patterns

# Also update fallback declarative to include plural verbs
orig_extract = sem_mod.LinguisticSemanticExtractor.extract

def patched_extract(cls, text: str, source_loc=None):
    clean_text = text.strip()
    clean_text = re.sub(r'^\s*(?:\[[A-Za-z0-9]+\]|\(?[A-Za-z0-9ivxlcdmIVXLCDM]+\)[\s\.\)]|\d+[\.\)])\s*', '', clean_text)
    
    # Appositive extraction for parenthetical clauses enclosed in em-dashes or hyphens
    intro_cond = None
    working_text = clean_text
    m_appos = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\-]+?)\s*(?:—|\s+-\s+)(?P<appositive>[^—\-]+?)(?:—|\s+-\s+)(?P<rest>[a-z].*)$', clean_text)
    if m_appos:
        entity_core = m_appos.group("entity").strip()
        appositive_cond = m_appos.group("appositive").strip()
        rest_clause = m_appos.group("rest").strip()
        working_text = f"{entity_core} {rest_clause}"
        intro_cond = appositive_cond

    # Call original with modified working text if appositive found
    res = orig_extract(working_text, source_loc)
    if res and intro_cond:
        res.conditions = intro_cond
        res.raw_evidence = clean_text
        return res
    if res:
        return res

    # Fallback with plural verbs
    match_decl = re.match(
        r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|has|have|form|forms|constitute|constitutes|contain|contains|feature|features|comprise|comprises|occurs?|progresses|develops|falls)\s+(?P<rest>.*)',
        working_text,
        re.IGNORECASE
    )
    if match_decl:
        pe = match_decl.group("entity").strip()
        verb = match_decl.group("verb").strip().lower()
        rest = match_decl.group("rest").strip()
        if not pe.lower().endswith(("in the", "of the", "to the", "from the")):
            intent_type = "attribute" if verb in {"has", "have", "features", "feature", "contains", "contain", "comprises", "comprise", "form", "forms", "constitute", "constitutes", "occurs", "occur", "progresses", "develops", "falls"} else "definition"
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type=intent_type,
                primary_entity=pe,
                predicate=f"{verb} {rest}",
                secondary_entities=[],
                conditions=intro_cond,
                raw_evidence=clean_text,
                source_location=source_loc or {},
                confidence=0.85,
                extraction_method="linguistic_rule"
            )
    return None

sem_mod.LinguisticSemanticExtractor.extract = classmethod(patched_extract)

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    s = unicodedata.normalize('NFKC', text)
    s = html.unescape(s)
    s = re.sub(r'(?<=\w)\s*&\s*(?=\w)', ' and ', s)
    s = re.sub(r'[\u200b\u200c\u200d\ufeff\u00ad]', ' ', s)
    s = re.sub(r'[\u201c\u201d\u201e\u201f\u00ab\u00bb]', '"', s)
    s = re.sub(r'[\u2018\u2019\u201a\u201b\u2032]', "'", s)
    s = re.sub(r'["\']([A-Za-z0-9\s\-]+?)["\']', r'\1', s)
    s = re.sub(r'(\d+)\s*[\u2013–]\s*(\d+)', r'\1-\2', s)
    s = re.sub(r'\\([*_{}\[\]()#+\-.!])', r'\1', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'__([^_]+)__', r'\1', s)
    s = re.sub(r'~~([^~]+)~~', r'\1', s)
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s

noise_cases = [
    ("Ligatures (fi, fl)", "The first layer of the atmosphere is the troposphere, which exhibits significant moisture fluxes."),
    ("Unicode Ligature chars", "The \ufb01rst layer of the atmosphere is the troposphere, which exhibits signi\ufb01cant moisture \ufb02uxes."),
    ("Smart Quotes", "\u201cThe lithosphere\u201d is defined as the rigid outer crust and upper mantle of the Earth."),
    ("Em-Dashes without space", "Igneous rocks\u2014formed through cooling of magma\u2014are classified into intrusive and extrusive types."),
    ("En-Dashes in ranges", "The mesosphere extends from 50\u201380 kilometres above the Earth surface."),
    ("Non-breaking spaces", "The\u00a0troposphere\u00a0is\u00a0the\u00a0lowest\u00a0layer\u00a0of the atmosphere."),
    ("Zero-width spaces", "The\u200btroposphere\u200bis\u200bthe\u200blowest\u200blayer\u200bof the atmosphere."),
    ("Markdown bold/italics in sentence", "The **lithosphere** is defined as the rigid outer shell of the Earth."),
    ("Markdown escape backslashes", "The \\*lithosphere\\* is defined as the rigid outer shell of the Earth."),
    ("HTML entity &amp;", "The crust &amp; upper mantle constitute the lithosphere."),
    ("Accented proper nouns", "The K\u00f6ppen climate classification system divides climates into five main vegetation groups.")
]

se = SemanticExtractor()
print("Extracting with proposed pipeline across all 11 noise cases:")
all_passed = True
for label, raw in noise_cases:
    clean = sanitize_text(raw)
    nodes = se.extract(clean)
    count = len(nodes)
    status = "PASS" if count == 1 else "FAIL"
    if count != 1:
        all_passed = False
    print(f"[{status}] {label:35} -> Nodes: {count}")
    for n in nodes:
        print(f"       Entity: '{n.primary_entity}' | Intent: {n.intent_type} | Pred: '{n.predicate}' | Cond: '{n.conditions}'")

print("\nAll 11 formatting noise test cases passed:", all_passed)
