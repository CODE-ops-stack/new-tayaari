import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional

@dataclass
class KnowledgeUnit:
    source_id: str
    raw_text: str
    block_type: str
    entities: List[str]
    
@dataclass
class QuestionIntent:
    knowledge: KnowledgeUnit
    target_entity: str
    intent_type: str
    cognitive_level: str
    
@dataclass
class AnswerContract:
    intent: QuestionIntent
    correct_answer: str
    semantic_type: str
    
@dataclass
class DistractorContract:
    answer_contract: AnswerContract
    distractors: List[str]
    trap_types: List[str]

@dataclass
class GeneratedQuestion:
    id: str
    stem: str
    options: Dict[str, str]
    correct_key: str
    correct_answer_text: str
    explanation: str
    cognitive_demand: str
    exam_target: str
    topic_id: int
    topic_name: str
    tier: str
    format: str
    pdf_sequence_number: str
    currentness_status: str
    provenance: Dict[str, Any]
    distractor_dissections: List[Dict[str, str]]
    contracts: Dict[str, Any]
    valid: bool

@dataclass
class ValidationResult:
    is_valid: bool
    failure_reasons: List[str]

def exact_word_match(target: str, text: str) -> bool:
    """Safely check if target appears as a whole word in text."""
    pattern = r'\b' + re.escape(target) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))

def classify_source_block(text: str) -> str:
    """Classifies source block and rejects OCR artifacts."""
    text_lower = text.lower()
    ocr_markers = ["copyright", "price", "rs.", "rs ", "published by", "page", "isbn", "all rights reserved"]
    
    if any(exact_word_match(m, text_lower) for m in ocr_markers):
        return "OCR_FRAGMENT"
        
    if re.match(r'^[0-9\.\s]+$', text):
        return "OCR_FRAGMENT"
        
    # Check for complete sentences
    if not re.search(r'[.!?]\s*$', text.strip()):
        return "FRAGMENT"
        
    return "PROSE"
