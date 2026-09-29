import sys
import os

# Ensure UTF-8 output encoding on Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")
sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_challenger_m2_it3_2")

import re
import html
import unicodedata
import uuid
from typing import List, Dict, Any, Optional

import v13_discovery.normalizer as norm_mod
import v13_discovery.semantic_extractor as sem_mod
from v13_discovery.normalizer import DocumentNormalizer, LayoutDesegmenter, NormalizedBlock, BlockType
from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    DiscourseContext,
    NoiseFilterGate,
    LinguisticSemanticExtractor,
    KnowledgeNode,
    PRONOUN_TOKENS
)

# ==============================================================================
# REMEDIATION 1 & 3: NoiseFilterGate Questions & Dangling Fragments
# ==============================================================================
orig_audit = NoiseFilterGate.audit

INTERROGATIVE_REGEX = re.compile(
    r'^\s*(?:'
    r'(?:What|Why|How|Where|Which|Who|Whom|Whose|When)\s+(?:is|are|was|were|do|does|did|can|could|will|would|should|may|might|must|has|have|had|causes?|creates?|occurs?)\b|'
    r'Which\s+[A-Za-z0-9\s\-]+?\s+(?:is|are|was|were|contains?|features?|has|have|causes?)\b|'
    r'(?:Is|Are|Was|Were|Can|Could|Do|Does|Did|Will|Would|Should|May|Might|Must)\s+[A-Za-z0-9\s\-]+?\s+[a-z]+'
    r')',
    re.IGNORECASE
)

DANGLING_FRAG_REGEX = re.compile(
    r'\b(?:composed\s+of|consists?\s+of|known\s+as|defined\s+as|termed\s+as|referred\s+to\s+as|such\s+as|discovered\s+that)\s*[\.\!\?]?\s*$',
    re.IGNORECASE
)

def patched_audit(cls, text: str, is_block_context: bool = False, has_antecedent: bool = False) -> Optional[str]:
    t = text.strip()
    if not t:
        return "syntactic_fragment"

    # 1. Question filtering
    if re.search(r'\?\s*[\'\"\)\]]?\s*$', t):
        return "interrogative_question"
    if INTERROGATIVE_REGEX.match(t) and not t.endswith('.'):
        return "interrogative_question"

    # 2. Incomplete dangling phrases
    if DANGLING_FRAG_REGEX.search(t):
        return "syntactic_fragment"

    m = re.search(r'\b(?:discovered|found|proved|shown|revealed|believed|demonstrated|established)\s+that\s+(.+)$', t, re.IGNORECASE)
    if m:
        clause = m.group(1).strip().rstrip('.!?')
        words = [w.lower() for w in re.sub(r'[^\w\s]', '', clause).split()]
        clause_verbs = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'could', 'will', 'would', 'forms', 'form', 'rotates', 'rotate', 'contains', 'contain', 'orbits', 'orbit', 'moves', 'move', 'extends', 'extend', 'consists', 'consist', 'exhibits', 'exhibit', 'composed'}
        if not any(w in clause_verbs for w in words):
            return "syntactic_fragment"

    return orig_audit(text, is_block_context, has_antecedent)

NoiseFilterGate.audit = classmethod(patched_audit)

# ==============================================================================
# REMEDIATION 2: LayoutDesegmenter.is_heading Soft-Hyphen Fix
# ==============================================================================
def patched_is_heading(cls, line: str) -> bool:
    """Identifies isolated section headings or topic headers that should not be merged into prose."""
    s = line.strip()
    if not s or len(s) > 45:
        return False
    # Soft-hyphen or trailing hyphen: line wrap across column/line break, NEVER a heading
    if s.endswith(('-', '\u00ad', '—', '–')) or re.search(r'[\-\u00ad]\s*$', s):
        return False
    if s.endswith(('.', '!', '?', ';', ',')):
        return False
    if re.search(r'\b[a-z]{2,}\.\s+[A-Z]', s):
        return False
    if s.startswith('#'):
        return True
    if s.endswith(':'):
        return True
    words = [w.lower() for w in re.sub(r'[^\w\s]', '', s).split()]
    if not words or any(w in cls.FINITE_VERBS for w in words):
        return False
    if words[-1] in cls.DANGLING_ENDINGS:
        return False
    # Title Case or ALL CAPS
    return (s.isupper() or s.istitle() or all(w[0].isupper() for w in s.split() if w.isalpha()))

LayoutDesegmenter.is_heading = classmethod(patched_is_heading)

# ==============================================================================
# REMEDIATION 4: Text Normalization for Formatting Noise & Unicode
# ==============================================================================
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

# Inject sanitize_text into DocumentNormalizer.normalize
orig_normalize = DocumentNormalizer.normalize
def patched_normalize(self, arg1: str, arg2: str = "doc_1") -> List[NormalizedBlock]:
    if "\n" in arg1 or "|" in arg1 or len(arg1) > len(arg2):
        raw_text = sanitize_text(arg1)
        source_file = arg2
    else:
        raw_text = sanitize_text(arg2)
        source_file = arg1
    return orig_normalize(self, raw_text, source_file)

DocumentNormalizer.normalize = patched_normalize

# Update LinguisticSemanticExtractor PATTERNS & fallback
new_patterns = []
for intent, pat in sem_mod.LinguisticSemanticExtractor.PATTERNS:
    if intent == "spatial" and "extends up to" in pat.pattern:
        new_pat = re.compile(
            pat.pattern.replace("extends up to", "extends up to|extends from|extends between"),
            re.IGNORECASE
        )
        new_patterns.append((intent, new_pat))
    elif intent == "classification" and pat.pattern.startswith(r'^(?:(?P<subject>'):
        new_pat = re.compile(
            r'^(?:(?P<subject>[A-Za-z\s]+?)\s+)?(?:classif(?:y|ies)|divid(?:e|es)|categoriz(?:es|e)|groups?)\s+(?P<target>.*?)\s+into\s+(?P<pred>.*)$',
            re.IGNORECASE
        )
        new_patterns.append((intent, new_pat))
    elif intent == "part-of" and "consists?\\s+of)\\s*:?\\s*.*" in pat.pattern:
        # Require non-empty complement for composed of / consists of
        new_pat = re.compile(
            pat.pattern.replace(
                r'(?:(?:is|are)\s+(?:composed|made up|constituted)\s+of|consists?\s+of)\s*:?\s*.*',
                r'(?:(?:is|are)\s+(?:composed|made up|constituted)\s+of|consists?\s+of)\s*:?\s*[A-Za-z0-9\s\-]{3,}.*'
            ),
            re.IGNORECASE
        )
        new_patterns.append((intent, new_pat))
    else:
        new_patterns.append((intent, pat))

sem_mod.LinguisticSemanticExtractor.PATTERNS = new_patterns

orig_extract = sem_mod.LinguisticSemanticExtractor.extract
def patched_extract(cls, text: str, source_loc=None):
    clean_text = sanitize_text(text.strip())
    clean_text = re.sub(r'^\s*(?:\[[A-Za-z0-9]+\]|\(?[A-Za-z0-9ivxlcdmIVXLCDM]+\)[\s\.\)]|\d+[\.\)])\s*', '', clean_text)

    # Interrogative check inside extractor
    if re.search(r'\?\s*[\'\"\)\]]?\s*$', clean_text) or INTERROGATIVE_REGEX.match(clean_text):
        return None

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

    res = orig_extract(working_text, source_loc)
    if res and intro_cond:
        res.conditions = intro_cond
        res.raw_evidence = clean_text
        return res
    if res:
        # Verify entity is not an interrogative word
        if res.primary_entity.lower() in {"what", "why", "how", "which", "where", "when", "who", "whom", "can", "could", "is", "are"}:
            return None
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
        # Reject interrogative pronouns and dangling complements
        if pe.lower() in {"what", "why", "how", "which", "where", "when", "who", "whom", "can", "could", "is", "are", "do", "does", "did"}:
            return None
        if pe.lower().startswith(("what ", "which ", "how ", "why ", "where ", "who ", "can ", "could ")):
            return None
        if rest.lower().endswith(("composed of", "consists of", "known as", "defined as", "discovered that", "such as")):
            return None
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

# ==============================================================================
# RUN CHALLENGER 2'S FULL ADVERSARIAL SUITE
# ==============================================================================
from test_adversarial_suite import run_all_challenges
print("=" * 70)
print("EXECUTING CHALLENGER 2 ADVERSARIAL SUITE WITH ITERATION 4 REMEDIATIONS")
print("=" * 70)
run_all_challenges()
