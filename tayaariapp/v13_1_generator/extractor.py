import sys
import os

# Ensure import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Optional
from v13_1_generator.contracts import KnowledgeUnit, QuestionIntent, classify_source_block
from v13_discovery.semantic_extractor import HybridSemanticExtractor, KnowledgeNode

extractor = HybridSemanticExtractor()

def extract_knowledge(source_id: str, raw_text: str) -> Optional[QuestionIntent]:
    """
    Extract structured KnowledgeUnit and QuestionIntent from source text.
    Implements Phase 4 (Source Gating) and Phase 5 (Knowledge Extraction).
    """
    # Phase 4: Block gating
    block_type = classify_source_block(raw_text)
    if block_type in ("OCR_FRAGMENT", "FRAGMENT", "UNKNOWN"):
        return None

    # Semantic Extraction
    node: KnowledgeNode = extractor.extract_sentence(raw_text)
    if not node:
        return None

    # Require explicit non-ambiguous relations
    if not node.primary_entity or len(node.primary_entity) < 3:
        return None
    if not node.raw_evidence:
        return None
        
    # Exclude unresolved pronouns
    lower_ent = node.primary_entity.lower().split()
    pronouns = {"it", "they", "he", "she", "this", "these", "those"}
    if lower_ent[0] in pronouns:
        return None

    # Construct explicit typed contract
    ku = KnowledgeUnit(
        source_id=source_id,
        raw_text=raw_text,
        block_type=block_type,
        entities=[node.primary_entity] + (node.secondary_entities or [])
    )

    qi = QuestionIntent(
        knowledge=ku,
        target_entity=node.primary_entity,
        intent_type=node.intent_type,
        cognitive_level="RECALL", # Base level, will be refined by audit
    )
    
    return qi
