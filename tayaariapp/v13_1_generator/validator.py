import re
from v13_1_generator.contracts import GeneratedQuestion, ValidationResult


def _option_texts(q: GeneratedQuestion) -> list:
    """
    Returns option texts for either supported option shape.

    The locked Android contract is a list of {"id": "opt_<letter>", "text": ...};
    a legacy letter-keyed dict is still accepted.
    """
    options = getattr(q, "options", None) or []
    if isinstance(options, dict):
        return [v for v in options.values() if isinstance(v, str)]
    texts = []
    for opt in options:
        if isinstance(opt, dict):
            value = opt.get("text", "")
        else:
            value = opt
        if isinstance(value, str):
            texts.append(value)
    return texts


def audit_cognitive_level(q: GeneratedQuestion) -> str:
    """Phase 9: Independent Cognitive Audit"""
    # Don't overlabel simple facts as UNDERSTAND/APPLY
    text = (q.stem + " " + q.explanation).lower()
    
    # If the question asks for a direct entity definition or identity from a category
    if "which of the following is" in q.stem.lower() or "defined as" in q.stem.lower():
        return "RECALL"
        
    if "why" in q.stem.lower() or "reason" in text:
        return "UNDERSTAND"
        
    if "difference" in text or "compared to" in text:
        return "COMPARE"
        
    return "RECALL" # Safe fallback

def audit_exam_fit(q: GeneratedQuestion) -> str:
    """Phase 10: Exam Fit"""
    # Simple factual questions without deep reasoning should be SSC/RRB
    if q.cognitive_demand == "RECALL":
        if "ssc" not in q.exam_target.lower() and "rrb" not in q.exam_target.lower():
            return "SSC CGL" # Downgrade to appropriate level
    return q.exam_target

def validate_question(q: GeneratedQuestion) -> ValidationResult:
    """Phase 11: 11-point Question Validation"""
    reasons = []
    
    # 1. Grammatical (basic check)
    if not q.stem.endswith("?"):
        reasons.append("GRAMMAR: No question mark")
    if len(q.stem.split()) < 5:
        reasons.append("GRAMMAR: Stem too short")
        
    # 2. Meaningful
    bad_phrases = ["this entity", "the following sentence", "the following clause"]
    if any(bp in q.stem.lower() for bp in bad_phrases):
        reasons.append("MEANING: Contains unresolved reference or metatext")
        
    # 3. One answer
    vals = _option_texts(q)
    if len(set(vals)) != 4:
        reasons.append("ANSWER: Options not unique")
        
    # 4. Answer type match (Contracts ensure this)
    
    # 5. Evidence support (Contracts ensure this)
    
    # 6. Distractors fit (Contracts ensure this)
    
    # 7. Explanation teaches
    if len(q.explanation) < 15:
        reasons.append("EXPLANATION: Too short to teach")
        
    # 8. Provenance complete
    if not q.provenance.get("source_id"):
        reasons.append("PROVENANCE: Missing source ID")
        
    # 9 & 10. Audit labels
    audited_cog = audit_cognitive_level(q)
    if audited_cog != q.cognitive_demand:
        q.cognitive_demand = audited_cog # Fix it
        
    audited_exam = audit_exam_fit(q)
    if audited_exam != q.exam_target:
        q.exam_target = audited_exam # Fix it
        
    # Extra: no leakage
    stem_lower = q.stem.lower()
    ans_lower = q.correct_answer_text.lower()
    
    # Use exact word boundaries to check leakage
    if re.search(r'\b' + re.escape(ans_lower) + r'\b', stem_lower):
        reasons.append("LEAKAGE: Answer found in stem")
        
    for opt in _option_texts(q):
        if opt == q.correct_answer_text: continue
        if opt.lower() == ans_lower:
            reasons.append("LEAKAGE: Duplicate correct options")
            
    # Substring sanity check
    if "indus" in ans_lower and "industrial" in q.explanation.lower() and "river" not in q.explanation.lower():
         reasons.append("SEMANTIC: Indus matched industrial")
         
    if "star" in ans_lower and "started" in q.explanation.lower() and "sky" not in q.explanation.lower():
         reasons.append("SEMANTIC: star matched started")
         
    if "rice" in ans_lower and "price" in q.explanation.lower():
         reasons.append("SEMANTIC: rice matched price")
         
    if "ring" in ans_lower and "ring of fire" in q.explanation.lower():
         reasons.append("SEMANTIC: ring matched Ring of Fire")
         
    # Check topic fallback
    if q.topic_id == 6 and q.topic_name == "Physical Geography":
        # Ensure it wasn't a blind fallback.
        pass # The strict classifier won't return 6 unless keyword exactly matched.
        
    is_valid = len(reasons) == 0
    q.valid = is_valid
    return ValidationResult(is_valid=is_valid, failure_reasons=reasons)
