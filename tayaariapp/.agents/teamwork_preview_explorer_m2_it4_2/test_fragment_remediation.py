import sys
sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")

import re
import v13_discovery.semantic_extractor as sem_mod

orig_audit = sem_mod.NoiseFilterGate.audit

def patched_audit(cls, text: str, is_block_context: bool = False, has_antecedent: bool = False):
    t = text.strip()
    if not t:
        return 'syntactic_fragment'
    # 1. Interrogative question filtering
    if re.search(r'\?\s*[\'\"\)\]]?\s*$', t):
        return 'interrogative_question'
    if re.match(r'^\s*(?:What|Why|How|Where|Which|Who|Whom|Whose)\s+(?:is|are|was|were|do|does|did|can|could|will|would|should|may|might|must|has|have|had|causes?|creates?|occurs?)\b', t, re.IGNORECASE):
        return 'interrogative_question'
    if re.match(r'^\s*Which\s+[A-Za-z0-9\s\-]+?\s+(?:is|are|was|were|contains?|features?|has|have|causes?)\b', t, re.IGNORECASE):
        return 'interrogative_question'
    if re.match(r'^\s*(?:Is|Are|Was|Were|Can|Could|Do|Does|Did)\s+[A-Za-z0-9\s\-]+?\s+[a-z]+', t, re.IGNORECASE) and not t.endswith('.'):
        return 'interrogative_question'
        
    # 2. Incomplete dangling phrases
    if re.search(r'\b(?:composed\s+of|consists?\s+of|known\s+as|defined\s+as|termed\s+as|referred\s+to\s+as|such\s+as|discovered\s+that)\s*[\.\!\?]?\s*$', t, re.IGNORECASE):
        return 'syntactic_fragment'
        
    m = re.search(r'\b(?:discovered|found|proved|shown|revealed|believed|demonstrated|established)\s+that\s+(.+)$', t, re.IGNORECASE)
    if m:
        clause = m.group(1).strip().rstrip('.!?')
        words = [w.lower() for w in re.sub(r'[^\w\s]', '', clause).split()]
        clause_verbs = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'could', 'will', 'would', 'forms', 'form', 'rotates', 'rotate', 'contains', 'contain', 'orbits', 'orbit', 'moves', 'move', 'extends', 'extend', 'consists', 'consist', 'exhibits', 'exhibit', 'composed'}
        if not any(w in clause_verbs for w in words):
            return 'syntactic_fragment'

    return orig_audit(text, is_block_context, has_antecedent)

sem_mod.NoiseFilterGate.audit = classmethod(patched_audit)

se = sem_mod.SemanticExtractor()
cases = [
    ('The oceanic crust is composed of', 0),
    ('The oceanic crust consists of', 0),
    ('The oceanic crust is known as', 0),
    ('Scientists have discovered that the inner core', 0),
    ('The continental shelf extends to a depth of', 0),
    ('Granite is the intrusive igneous rock that continents are made of.', 1),
    ('Solar wind is the stream of charged particles that the Earth magnetic field protects us from.', 1),
    ('What is an earthquake?', 0),
    ('How are metamorphic rocks formed in nature?', 0),
    ('Which atmospheric layer contains the ozone layer?', 0),
    ('Can sedimentary rocks transform into igneous rocks?', 0)
]

all_passed = True
for t, expected in cases:
    nodes = se.extract(t)
    actual = len(nodes)
    status = 'OK' if actual == expected else 'FAIL'
    if actual != expected:
        all_passed = False
    print(f'[{status}] {t[:50]:50} -> got {actual}, expected {expected}')

print('All passed:', all_passed)
