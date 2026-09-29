import random
import re
from typing import Optional, Tuple, List
from v13_1_generator.contracts import QuestionIntent, AnswerContract, DistractorContract, GeneratedQuestion
from v13_1_generator.ontology import ONTOLOGY_BANKS, detect_semantic_type

def synthesize_stem(intent: QuestionIntent, answer_text: str) -> Optional[str]:
    """
    Phase 7: Stem Synthesis. Generate questions from structured intent without raw source wrapping.
    """
    ent = intent.target_entity
    # Use generic but grammatically sound templates based on intent
    itype = intent.intent_type
    
    # We don't want to leak the answer in the stem!
    # Let's say the target entity IS the answer.
    
    stem = ""
    if itype == "definition":
        stem = f"Which of the following is defined as: {intent.knowledge.raw_text.replace(answer_text, 'this').replace(answer_text.lower(), 'this')}?"
    elif itype == "attribute":
        stem = f"Which of the following entities is characterized by the following attribute: {intent.knowledge.raw_text.replace(answer_text, 'it').replace(answer_text.lower(), 'it')}?"
    elif itype == "classification":
        stem = f"To which classification does the following statement refer: {intent.knowledge.raw_text.replace(answer_text, 'this category').replace(answer_text.lower(), 'this category')}?"
    elif itype == "cause_effect":
        stem = f"What is the primary cause or effect described in the following context: {intent.knowledge.raw_text.replace(answer_text, 'this phenomenon').replace(answer_text.lower(), 'this phenomenon')}?"
    else:
        # Fallback for other intents but still avoiding raw wrapper with answer leakage
        stem = f"Which of the following best fits the description: {intent.knowledge.raw_text.replace(answer_text, 'this').replace(answer_text.lower(), 'this')}?"
    
    # Clean up
    stem = re.sub(r'\s+', ' ', stem).strip()
    # Check if the stem is a proper question
    if not stem.endswith("?"):
        stem += "?"
        
    return stem

def build_contracts(intent: QuestionIntent) -> Optional[Tuple[AnswerContract, DistractorContract]]:
    """
    Phase 6 & 8: Answer and Distractor Contracts.
    """
    semantic_type = detect_semantic_type(intent.target_entity, intent.knowledge.raw_text)
    if not semantic_type:
        return None
        
    # Find exact answer text from ontology
    correct_text = None
    for member in ONTOLOGY_BANKS[semantic_type]:
        pattern = r'\b' + re.escape(member.lower()) + r'\b'
        if member.lower() == intent.target_entity.lower() or re.search(pattern, intent.target_entity.lower()):
            correct_text = member
            break
            
    if not correct_text:
        return None
        
    answer_contract = AnswerContract(
        intent=intent,
        correct_answer=correct_text,
        semantic_type=semantic_type
    )
    
    # Build distractors
    pool = [m for m in ONTOLOGY_BANKS[semantic_type] if m.lower() != correct_text.lower()]
    if len(pool) < 3:
        return None
        
    import hashlib
    seed = int(hashlib.md5(correct_text.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    rng.shuffle(pool)
    
    distractors = pool[:3]
    
    distractor_contract = DistractorContract(
        answer_contract=answer_contract,
        distractors=distractors,
        trap_types=["sibling_category", "sibling_category", "sibling_category"]
    )
    
    return answer_contract, distractor_contract

def assemble_question(intent: QuestionIntent, ac: AnswerContract, dc: DistractorContract) -> Optional[GeneratedQuestion]:
    stem = synthesize_stem(intent, ac.correct_answer)
    if not stem:
        return None
        
    # Check for stem leakage
    if ac.correct_answer.lower() in stem.lower():
        return None
        
    options_list = dc.distractors + [ac.correct_answer]
    random.shuffle(options_list)
    
    opts_dict = {}
    correct_key = ""
    for idx, letter in enumerate(["a", "b", "c", "d"]):
        opts_dict[letter] = options_list[idx]
        if options_list[idx] == ac.correct_answer:
            correct_key = f"opt_{letter}"
            
    # Assign temporary taxonomy, will be strictly audited later
    from v13_1_generator.classification import classify_topic_strict, assign_exam_strict
    
    topic_id, topic_name = classify_topic_strict(ac.correct_answer + " " + intent.knowledge.raw_text)
    
    q = GeneratedQuestion(
        id="", # Assigned later
        stem=stem,
        options=opts_dict,
        correct_key=correct_key,
        correct_answer_text=ac.correct_answer,
        explanation=intent.knowledge.raw_text,
        cognitive_demand=intent.cognitive_level,
        exam_target=assign_exam_strict(topic_name, intent.cognitive_level),
        topic_id=topic_id,
        topic_name=topic_name,
        tier="Tier 1",
        format="MCQ",
        pdf_sequence_number="0",
        currentness_status="Static",
        provenance={"source_id": intent.knowledge.source_id, "evidence": intent.knowledge.raw_text},
        distractor_dissections=[{"text": d, "trap": "sibling"} for d in dc.distractors],
        contracts={"semantic_type": ac.semantic_type, "intent_type": intent.intent_type},
        valid=False # Pending validation
    )
    return q
