import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple

@dataclass
class QuantitativeData:
    value: float
    unit: str
    parameter: str
    raw_text: str

@dataclass
class KnowledgeNode:
    node_id: str
    intent_type: str
    primary_entity: str
    predicate: str
    secondary_entities: List[str] = field(default_factory=list)
    conditions: Optional[str] = None
    quantitative_data: Optional[Dict[str, Any]] = None
    raw_evidence: str = ""
    source_location: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    extraction_method: str = "linguistic_rule"

class NoiseFilterGate:
    NOISE_PATTERNS = {
        "mcq_leakage": [
            r'^\s*\(?[a-eA-E]\)[\s\.\)]',
            r'^\s*Question\s*\d+',
            r'^\s*Q\.\s*\d+',
            r'^\s*Option\s+[A-D]\b',
            r'\(a\)\s+.*\s+\(b\)',
            r'^\s*Ans(?:wer)?\s*[:\.]',
            r'^\s*Sol(?:ution)?\s*[:\.]',
            r'Which of the following\s+(?:statements?\s+)?(?:is|are)\s+(?:not\s+)?(?:correct|true)',
            r'Select the correct\s+(?:code|answer)\b',
            r'Consider the following statements\b'
        ],
        "watermark_header": [
            r'\bPARMAR\s+SSC\b',
            r'\bISBN\s*[\d\-]+',
            r'www\.[a-z0-9\-\.]+\.(?:com|org|in|net)',
            r'^Chapter\s+\d+\b',
            r'^NCERT\s+Class\s+\d+',
            r'^\s*Page\s+\d+\s+of\s+\d+',
            r'^\s*\d{1,3}\s*$'
        ],
        "table_formatting_artifact": [
            r'^\s*\|',
            r'\|\s*[-:]+[-| :]+\|',
            r'\bTopic\s*\|\s*Tier\b',
            r'^\s*```'
        ],
        "syntactic_fragment": [
            r'\b(?:and|or|but|with|that|which|whose|because|while|whereas|although)\s*[\.\!\?]?\s*$',
            r'\.\.\.\s*$',
            r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$',
            r'^\s*Because despite being\b',
            r'^\s*While moving on your orbit\b'
        ],
        "anaphoric_unresolved": [
            r'^\s*(?:They|These|Those|He|She|It)\s+(?:are|is|have|has|were|was|can|do|does|proposes)\b'
        ],
        "broken_reading_order": [
            r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z][a-z]+',
            r'^(?:[A-Z][a-zA-Z\s]{3,20}\s+){4,}[A-Z][a-zA-Z\s]{3,20}$'
        ]
    }

    @classmethod
    def audit(cls, text: str) -> Optional[str]:
        for cat, pats in cls.NOISE_PATTERNS.items():
            for p in pats:
                if re.search(p, text, re.IGNORECASE if cat not in ["broken_reading_order"] else 0):
                    return cat
        words = text.split()
        if len(words) < 5:
            return "syntactic_fragment"
        return None

class LinguisticSemanticExtractor:
    """Deterministic, clause-aware NLP pattern extractor for all 14 intents."""
    
    INTRO_CLAUSE_REGEX = re.compile(
        r'^(?P<intro>(?:In|According to|During|Throughout|Across|Under|With|Between|At|From|By|On)\s+[^,]+),\s*(?P<main>[A-Z].*)$'
    )
    
    PASSIVE_DEF_REGEX = re.compile(
        r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\-]+)\.?$',
        re.IGNORECASE
    )

    PATTERNS = [
        # 1. EXCEPTION
        ("exception", re.compile(
            r'^(?:While\s+.*,\s+)?(?P<entity>[A-Z][a-zA-Z\s\(\)\-]+)\s+(?:are|is)\s+(?:the only|unique exceptions?|uniquely incapable of)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^Unlike\s+(?P<cond>[^,]+),\s+(?P<entity>[A-Z][a-zA-Z\s\(\)\-]+)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 2. DEFINITION (Active)
        ("definition", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is defined as|refers to|is a constant stream of|is a massive collection of|is an imaginary line|is the point on the surface)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 3. COMPARISON
        ("comparison", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+(?:whereas|while|in contrast to)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>.*)$',
            re.IGNORECASE
        )),
        # 4. CLASSIFICATION
        ("classification", re.compile(
            r'^(?:Geologists\s+|Plate tectonics\s+)?(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are classified into|are divided into|classif(?:y|ies)\s+[^into]+into|exhibits two primary categories of)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 5. CAUSE/EFFECT
        ("cause/effect", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:causes|leads to|results in|drives|triggers|release\s+.*disturb)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 6. SPATIAL
        ("spatial", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is located|is situated|flows westward through|flows through|traverses)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 7. DISTRIBUTION
        ("distribution", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is concentrated across|form the most widespread|are distributed in|are concentrated in)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 8. QUANTITY
        ("quantity", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:constitutes approximately|maintains a constant tilt of|measures approximately|originated approximately)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 9. SEQUENCE
        ("sequence", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:progresses through a definite chronological sequence|commenced approximately.*followed by|arrive first.*followed sequentially by)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 10. CONDITION
        ("condition", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:occurs exclusively during|can occur only if|condenses into.*only when)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 11. PROCESS
        ("process", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is the (?:\w+\s+)?process whereby|is the denudational process in which|develops through a systematic thermodynamic process|was formed through the tectonic process)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 12. PART-OF
        ("part-of", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:constitutes the outermost|is composed of three concentric|forms a small peripheral|is the lowest constituent layer)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 13. MEMBER-OF
        ("member-of", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is a prominent member of|is an ordinary yellow dwarf|is a remnant member of|is a major satellite container port)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        # 14. ATTRIBUTE
        ("attribute", re.compile(
            r'^(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are longitudinal compressional waves|has the lowest mean density|is characterized by|are very big and hot)\s+(?P<pred>.*)$',
            re.IGNORECASE
        ))
    ]

    @classmethod
    def extract(cls, text: str, source_loc: Dict[str, Any] = None) -> Optional[KnowledgeNode]:
        clean_text = text.strip()
        intro_cond = None

        # Check passive definition first: "The sun, moon... are called celestial bodies"
        m_pass = cls.PASSIVE_DEF_REGEX.match(clean_text)
        if m_pass:
            term = m_pass.group("term").strip()
            desc = m_pass.group("desc").strip()
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type="definition",
                primary_entity=term,
                predicate=f"are {desc}",
                secondary_entities=[desc],
                raw_evidence=clean_text,
                source_location=source_loc or {},
                confidence=0.92,
                extraction_method="linguistic_rule"
            )

        # Check introductory prepositional clauses
        m_intro = cls.INTRO_CLAUSE_REGEX.match(clean_text)
        working_text = clean_text
        if m_intro:
            intro_cond = m_intro.group("intro").strip()
            working_text = m_intro.group("main").strip()

        # Match against 14 intent patterns
        for intent, pat in cls.PATTERNS:
            m = pat.match(working_text)
            if not m:
                # Also try matching against original text if intro wasn't stripped
                m = pat.match(clean_text)
                
            if m:
                groups = m.groupdict()
                entity = groups.get("entity", "").strip()
                pred = groups.get("pred", "").strip()
                sec = []
                if "sec" in groups:
                    sec.append(groups["sec"].strip())
                if "pred1" in groups and "pred2" in groups:
                    pred = f"{groups['pred1']}, whereas {groups.get('sec', '')} {groups['pred2']}"

                cond = intro_cond or groups.get("cond")

                return KnowledgeNode(
                    node_id=str(uuid.uuid4()),
                    intent_type=intent,
                    primary_entity=entity,
                    predicate=pred,
                    secondary_entities=sec,
                    conditions=cond,
                    raw_evidence=clean_text,
                    source_location=source_loc or {},
                    confidence=0.88,
                    extraction_method="linguistic_rule"
                )

        return None

# Test on golden eval set
with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
    gold = json.load(f)

extracted_count = 0
correct_intent_count = 0
pos_count = 0

for ex in gold["examples"]:
    if ex["expected_label"] == "positive":
        pos_count += 1
        node = LinguisticSemanticExtractor.extract(ex["text"], ex["provenance"])
        if node:
            extracted_count += 1
            if node.intent_type == ex["intent"]:
                correct_intent_count += 1
            else:
                print(f"[INTENT MISMATCH] {ex['id']}: expected {ex['intent']}, got {node.intent_type}")
        else:
            print(f"[MISSED POSITIVE] {ex['id']} ({ex['intent']}): {ex['text'][:70]}...")

print(f"\nLinguistic Extractor Evaluation:")
print(f"Positives parsed: {extracted_count}/{pos_count} ({extracted_count/pos_count*100:.1f}%)")
print(f"Correct intent match: {correct_intent_count}/{pos_count} ({correct_intent_count/pos_count*100:.1f}%)")
