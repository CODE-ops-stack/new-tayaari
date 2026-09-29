import difflib
from typing import List, Dict, Any, Tuple
from v13_1_generator.contracts import GeneratedQuestion

def is_near_dup(a: str, b: str, t: float = 0.85) -> bool:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= t

def audit_batch(questions: List[GeneratedQuestion]) -> Tuple[List[GeneratedQuestion], Dict[str, Any]]:
    """Phase 12: Batch Audit"""
    accepted = []
    rejected_reasons = {}
    
    seen_stems = []
    seen_facts = []
    
    for q in questions:
        if not q.valid:
            continue
            
        reason = None
        
        # Exact duplicate
        if q.stem in seen_stems:
            reason = "EXACT_DUPLICATE_STEM"
            
        # Semantic near duplicate
        elif any(is_near_dup(q.stem, s) for s in seen_stems):
            reason = "NEAR_DUPLICATE_STEM"
            
        # Same source fact pattern
        elif q.explanation in seen_facts:
            reason = "SAME_SOURCE_FACT"
            
        # Also check for distractor repetition or cross-question clueing
        # (Simplified for now, but explicit facts are tracked)
        
        if reason:
            rejected_reasons[q.id] = reason
            q.valid = False
        else:
            seen_stems.append(q.stem)
            seen_facts.append(q.explanation)
            accepted.append(q)
            
    return accepted, rejected_reasons
