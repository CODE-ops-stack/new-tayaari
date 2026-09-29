import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")

import re
import html
import unicodedata
from v13_discovery.normalizer import DocumentNormalizer, LayoutDesegmenter
from v13_discovery.semantic_extractor import SemanticExtractor, LinguisticSemanticExtractor

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    # 1. Unicode NFKC normalization
    s = unicodedata.normalize('NFKC', text)
    
    # 2. HTML unescape
    s = html.unescape(s)
    # Standalone & to and
    s = re.sub(r'(?<=\w)\s*&\s*(?=\w)', ' and ', s)
    
    # 3. Replace zero-width spaces and invisible separators with space
    s = re.sub(r'[\u200b\u200c\u200d\ufeff\u00ad]', ' ', s)
    
    # 4. Normalize quotes: convert smart quotes to standard quotes, then strip quoting around phrases
    s = re.sub(r'[\u201c\u201d\u201e\u201f\u00ab\u00bb]', '"', s)
    s = re.sub(r'[\u2018\u2019\u201a\u201b\u2032]', "'", s)
    s = re.sub(r'["\']([A-Za-z0-9\s\-]+?)["\']', r'\1', s)
    
    # 5. Normalize en-dashes in numeric ranges (50–80 -> 50-80)
    s = re.sub(r'(\d+)\s*[\u2013–]\s*(\d+)', r'\1-\2', s)
    
    # 6. Normalize em-dashes
    s = re.sub(r'[\u2014—]', ' - ', s)
    
    # 7. Strip markdown formatting: bold (**), italics (* or _), escapes (\*)
    s = re.sub(r'\\([*_{}\[\]()#+\-.!])', r'\1', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'__([^_]+)__', r'\1', s)
    s = re.sub(r'~~([^~]+)~~', r'\1', s)
    
    # 8. Accented Latin characters using NFKD decomposition
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    
    # Clean whitespace
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s

# Test cases
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
print("Extracting with current SemanticExtractor on sanitized text:")
for label, raw in noise_cases:
    clean = sanitize_text(raw)
    nodes = se.extract(clean)
    print(f"[{label}] -> Nodes: {len(nodes)} | Clean: '{clean}'")
    for n in nodes:
        print(f"   -> Entity: '{n.primary_entity}' | Intent: {n.intent_type} | Pred: '{n.predicate}'")
