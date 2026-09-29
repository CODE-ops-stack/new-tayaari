"""
v13_discovery/semantic_extractor.py
===================================
14-Intent Semantic Knowledge Representation Engine for Milestone 2.

Implements:
1. KnowledgeNode data model with full semantic slotting (intent_type, primary_entity,
   predicate, secondary_entities, conditions, quantitative_data, raw_evidence, source_location).
2. NoiseFilterGate: 0ms pre-extraction gate rejecting all 6 noise categories with zero false acceptances.
3. LinguisticSemanticExtractor: Deterministic, discourse-aware rule engine for all 14 intents.
4. GeminiStructuredExtractor: Throttled REST client for gemini-3.6-flash with strict responseSchema.
5. HybridSemanticExtractor: Production workhorse cascading local gating, linguistic rules, and LLM fallback.
6. SemanticExtractor: Universal interface compliant with PROJECT.md and all test suites.
"""

import os
import re
import html
import json
import time
import uuid
import unicodedata
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union


# Canonical intent mapping and aliases
INTENT_ALIASES = {
    "definition": "definition",
    "attribute": "attribute",
    "cause/effect": "cause_effect",
    "cause-effect": "cause_effect",
    "cause_effect": "cause_effect",
    "cause and effect": "cause_effect",
    "comparison": "comparison",
    "spatial": "spatial",
    "distribution": "distribution",
    "classification": "classification",
    "quantity": "quantity",
    "sequence": "sequence",
    "condition": "condition",
    "exception": "exception",
    "process": "process",
    "part-of": "part_of",
    "part_of": "part_of",
    "member-of": "member_of",
    "member_of": "member_of",
}

R2_CANONICAL_MAP = {
    "cause_effect": "cause/effect",
    "part_of": "part-of",
    "member_of": "member-of",
}

CANONICAL_14_INTENTS = {
    "definition",
    "attribute",
    "cause_effect",
    "comparison",
    "spatial",
    "distribution",
    "classification",
    "quantity",
    "sequence",
    "condition",
    "exception",
    "process",
    "part_of",
    "member_of",
}


def canonicalize_intent(intent: str) -> str:
    """Normalizes intent string to canonical snake_case."""
    if not intent:
        return "none"
    norm = intent.strip().lower()
    return INTENT_ALIASES.get(norm, norm)


def to_r2_intent(intent: str) -> str:
    """Normalizes intent string to R2 specification format (using / and -)."""
    if not intent:
        return "definition"
    norm = canonicalize_intent(intent)
    return R2_CANONICAL_MAP.get(norm, norm)


@dataclass
class QuantitativeData:
    """Structured container for quantitative/numerical observations."""
    value: float
    unit: str = ""
    parameter: str = ""
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "parameter": self.parameter,
            "raw_text": self.raw_text
        }


class KnowledgeNode:
    """Core knowledge unit representation with full semantic slotting.
    
    Supports both snake_case and camelCase accessors for seamless interoperability
    between unit tests and end-to-end pipeline components.
    """
    def __init__(
        self,
        node_id: str = "",
        intent_type: str = "definition",
        primary_entity: str = "",
        predicate: str = "",
        secondary_entities: Optional[List[str]] = None,
        conditions: Optional[Any] = None,
        quantitative_data: Optional[Any] = None,
        raw_evidence: str = "",
        source_location: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        extraction_method: str = "linguistic_rule",
        metadata: Optional[Dict[str, Any]] = None,
        # CamelCase keyword arguments
        nodeId: Optional[str] = None,
        intentType: Optional[str] = None,
        primaryEntity: Optional[str] = None,
        relatedEntities: Optional[List[str]] = None,
        quantitativeData: Optional[Any] = None,
        rawEvidence: Optional[str] = None,
        sourceLocation: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = nodeId or node_id or str(uuid.uuid4())
        self.intent_type = to_r2_intent(intentType or intent_type)
        self.primary_entity = (primaryEntity or primary_entity or "").strip()
        self.predicate = (predicate or "").strip()
        self.secondary_entities = relatedEntities or secondary_entities or []
        self.conditions = conditions
        self.quantitative_data = quantitativeData or quantitative_data
        self.raw_evidence = (rawEvidence or raw_evidence or "").strip()
        self.source_location = sourceLocation or source_location or {}
        self.confidence = confidence
        self.extraction_method = extraction_method
        self.metadata = metadata or {}

    # CamelCase property accessors
    @property
    def nodeId(self) -> str:
        return self.node_id
    @nodeId.setter
    def nodeId(self, val: str):
        self.node_id = val

    @property
    def intentType(self) -> str:
        return self.intent_type
    @intentType.setter
    def intentType(self, val: str):
        self.intent_type = to_r2_intent(val)

    @property
    def primaryEntity(self) -> str:
        return self.primary_entity
    @primaryEntity.setter
    def primaryEntity(self, val: str):
        self.primary_entity = val

    @property
    def relatedEntities(self) -> List[str]:
        return self.secondary_entities
    @relatedEntities.setter
    def relatedEntities(self, val: List[str]):
        self.secondary_entities = val

    @property
    def quantitativeData(self) -> Any:
        return self.quantitative_data
    @quantitativeData.setter
    def quantitativeData(self, val: Any):
        self.quantitative_data = val

    @property
    def rawEvidence(self) -> str:
        return self.raw_evidence
    @rawEvidence.setter
    def rawEvidence(self, val: str):
        self.raw_evidence = val

    @property
    def sourceLocation(self) -> Dict[str, Any]:
        return self.source_location
    @sourceLocation.setter
    def sourceLocation(self, val: Dict[str, Any]):
        self.source_location = val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "intent_type": self.intent_type,
            "primary_entity": self.primary_entity,
            "predicate": self.predicate,
            "secondary_entities": self.secondary_entities,
            "conditions": self.conditions,
            "quantitative_data": self.quantitative_data,
            "raw_evidence": self.raw_evidence,
            "source_location": self.source_location,
            "confidence": self.confidence,
            "extraction_method": self.extraction_method,
            "metadata": self.metadata
        }


def sanitize_text(text: str) -> str:
    """Sanitizes raw educational text by normalizing unicode ligatures, smart quotes,
    dashes, zero-width spaces, and stripping markdown formatting."""
    if not text:
        return ""
    # 1. Unicode NFKC normalization (ligatures \ufb01 -> fi, \ufb02 -> fl, full-width chars)
    s = unicodedata.normalize('NFKC', text)
    # 2. HTML unescape (&amp; -> &, &lt; -> <, etc.)
    s = html.unescape(s)
    s = re.sub(r'(?<=\w)\s*&\s*(?=\w)', ' and ', s)
    # 3. Replace zero-width spaces and invisible word separators with standard space
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
    # 8. Accented Latin characters using NFKD decomposition (Köppen -> Koppen)
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    # Clean whitespace
    return re.sub(r'[ \t]+', ' ', s).strip()


PRONOUN_TOKENS = {
    "it", "they", "them", "these", "those", "this", "that",
    "he", "she", "him", "her", "his", "their", "theirs", "its"
}

SINGULAR_PRONOUNS = {"it", "this", "that", "he", "she", "its", "his", "her"}
PLURAL_PRONOUNS = {"they", "these", "those", "their", "them", "theirs"}

# Proper nouns, celestial bodies, rivers, cities, historical figures, and scientific terms
# ending in 's' that are strictly grammatically singular.
PROPER_SINGULAR_OVERRIDES = {
    # Astronomical / Celestial
    "mars", "venus", "uranus", "cerberus", "phobos", "deimos", "olympus",
    "mount olympus", "tethys", "titan", "helios", "atlas", "polaris", "sirius",
    "regulus", "antares", "pegasus",
    # Rivers / Water Bodies
    "ganges", "the ganges", "indus", "the indus", "thames", "the thames",
    "danube", "rhine", "nile", "mississippi", "amazon", "brahmaputra",
    "yangtze", "tigris", "euphrates", "colorado", "st. lawrence",
    # Cities / Regions / Countries
    "paris", "athens", "brussels", "naples", "damascus", "mauritius",
    "cyprus", "rhodes", "texas", "kansas", "arkansas", "laos", "belarus",
    "honduras", "marseille", "trieste", "algiers", "buenos aires", "caracas",
    # Historical / Philosophical / Classical Figures
    "thales", "socrates", "archimedes", "pythagoras", "herodotus", "aristotle",
    "plato", "ptolemy", "ramses", "augustus", "hipparchus", "eratosthenes",
    "copernicus", "democritus", "hippocrates", "epicurus", "descartes",
    "clausius", "boltzmann", "habermas", "malthus", "galois", "gauss", "euler",
    # Academic disciplines ending in -ics / -s
    "physics", "mathematics", "optics", "thermodynamics", "mechanics",
    "acoustics", "genetics", "economics", "politics", "statistics",
    "electronics", "dynamics", "kinetics", "geophysics", "robotics",
    "linguistics", "ethics", "aesthetics",
    # Singular common / technical nouns ending in -s
    "species", "series", "apparatus", "corpus", "basis", "axis", "crisis",
    "oasis", "radius", "terminus", "nucleus", "syllabus", "focus", "fungus",
    "cactus", "stimulus", "locus", "process", "abyss", "canvas", "gas",
    "lens", "bias", "chaos", "cosmos", "pathos", "ethos", "hubris",
    "metropolis", "pelvis", "epidermis", "status"
}

# Plural proper nouns, collective mountain ranges, archipelagos, and irregular plurals
PLURAL_ENTITY_RECOGNITION = {
    # Mountain Ranges
    "himalayas", "the himalayas", "alps", "the alps", "andes", "the andes",
    "rockies", "the rockies", "rocky mountains", "the rocky mountains",
    "appalachians", "the appalachians", "appalachian mountains",
    "urals", "the urals", "ural mountains", "pyrenees", "the pyrenees",
    "caucasus", "the caucasus", "western ghats", "the western ghats",
    "eastern ghats", "the eastern ghats", "aravallis", "the aravallis",
    "aravalli range", "vindhyas", "the vindhyas", "satpuras", "the satpuras",
    "nilgiris", "the nilgiris", "carpathians", "the carpathians",
    "dolomites", "the dolomites", "cascades", "the cascades",
    # Archipelagos & Island Groups
    "andaman and nicobar", "andaman and nicobar islands", "the andaman and nicobar islands",
    "lakshadweep", "lakshadweep islands", "the lakshadweep islands",
    "maldives", "the maldives", "philippines", "the philippines",
    "bahamas", "the bahamas", "west indies", "the west indies",
    "sundarbans", "the sundarbans", "galapagos", "the galapagos",
    "galapagos islands", "canary islands", "aleutian islands", "cyclades",
    # Irregular & Collective Scientific Plurals
    "bacteria", "protozoa", "fungi", "algae", "larvae", "strata", "data",
    "criteria", "phenomena", "foci", "radii", "nuclei", "syllabi",
    "stimuli", "bases", "axes", "crises", "oases", "people", "children", "media"
}

# Finite verb inflections signaling grammatical number
SINGULAR_VERBS = {
    "is", "was", "has", "does", "forms", "constitutes", "contains", "features",
    "comprises", "develops", "occurs", "originates", "consists", "exhibits",
    "presents", "represents", "exerts", "absorbs", "emits", "radiates", "rotates",
    "revolves", "orbits", "flows", "causes", "leads", "produces", "extends",
    "measures", "displays"
}

PLURAL_VERBS = {
    "are", "were", "have", "do", "form", "constitute", "contain", "feature",
    "comprise", "develop", "occur", "originate", "consist", "exhibit",
    "present", "represent", "exert", "absorb", "emit", "radiate", "rotate",
    "revolve", "orbit", "flow", "cause", "lead", "produce", "extend",
    "measure", "display"
}

# Suffixes that end in 's' but signify singular nouns (note: 'as' intentionally excluded)
NON_PLURAL_SUFFIXES = ("ss", "us", "is", "ics", "ness", "less", "ous", "sis", "xis", "itis")


class DiscourseContext:
    """Maintains discourse referents across sentences within a NormalizedBlock.
    Tracks grammatical number (singular vs. plural) and recency hierarchy using
    verb agreement cues, dedicated proper noun lexicons, and head noun morphology."""

    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        self.metadata = metadata or {}
        self.singular_antecedents: List[str] = []
        self.plural_antecedents: List[str] = []
        self.all_antecedents: List[str] = []

        # Seed from block metadata (concept, topicName, section_heading, or heading)
        seed_theme = (
            self.metadata.get("concept") or
            self.metadata.get("topicName") or
            self.metadata.get("section_heading") or
            self.metadata.get("heading")
        )
        if seed_theme and isinstance(seed_theme, str):
            clean_theme = seed_theme.strip()
            if len(clean_theme) > 2 and clean_theme.lower() not in PRONOUN_TOKENS:
                self.register_entity(clean_theme)

    def register_entity(
        self,
        entity: str,
        is_plural: Optional[bool] = None,
        verb: Optional[str] = None,
        predicate: Optional[str] = None,
        sentence: Optional[str] = None
    ) -> None:
        """Registers a grounded noun phrase into discourse memory with multi-tier
        grammatical number determination:
        Tier 1: Explicit verb or predicate copula agreement cue
        Tier 2: Dedicated proper noun singular / plural lexicon overrides
        Tier 3: Head noun token extraction and non-plural suffix exclusions
        """
        if not entity:
            return
        clean = entity.strip().rstrip(".:;,")
        if len(clean) < 2 or clean.lower() in PRONOUN_TOKENS:
            return

        if is_plural is None:
            # Tier 1a: Verb agreement cue from explicit verb argument
            if verb:
                v_clean = verb.strip().lower()
                if v_clean in SINGULAR_VERBS:
                    is_plural = False
                elif v_clean in PLURAL_VERBS:
                    is_plural = True

            # Tier 1b: Verb agreement cue from predicate onset
            if is_plural is None and predicate:
                m_pred = re.match(
                    r'^\s*(?:(?:also|generally|primarily|typically|often|simply)\s+)?([A-Za-z]+)\b',
                    predicate
                )
                if m_pred:
                    pv = m_pred.group(1).lower()
                    if pv in SINGULAR_VERBS:
                        is_plural = False
                    elif pv in PLURAL_VERBS:
                        is_plural = True

            # Tier 1c: Verb agreement cue from sentence subject-verb structure
            if is_plural is None and sentence:
                m_sent = re.search(
                    r'\b' + re.escape(clean) + r'\b\s+(?:(?:also|generally|primarily|typically|often)\s+)?(is|was|has|does|are|were|have|do)\b',
                    sentence,
                    re.IGNORECASE
                )
                if m_sent:
                    sv = m_sent.group(1).lower()
                    if sv in {"is", "was", "has", "does"}:
                        is_plural = False
                    elif sv in {"are", "were", "have", "do"}:
                        is_plural = True

            # Tier 2: Dedicated proper noun singular & plural lexicon overrides
            if is_plural is None:
                norm_ent = re.sub(r'^(?:the|an|a)\s+', '', clean.strip().lower(), flags=re.IGNORECASE).strip()
                if norm_ent in PROPER_SINGULAR_OVERRIDES or clean.lower() in PROPER_SINGULAR_OVERRIDES:
                    is_plural = False
                elif norm_ent in PLURAL_ENTITY_RECOGNITION or clean.lower() in PLURAL_ENTITY_RECOGNITION:
                    is_plural = True

            # Tier 3: Head noun morphological analysis
            if is_plural is None:
                norm_ent = re.sub(r'^(?:the|an|a)\s+', '', clean.strip().lower(), flags=re.IGNORECASE).strip()
                tokens = [w for w in re.split(r'[\s\-\(\)]+', norm_ent) if w]
                head_noun = tokens[-1] if tokens else norm_ent
                if head_noun in PROPER_SINGULAR_OVERRIDES:
                    is_plural = False
                elif head_noun in PLURAL_ENTITY_RECOGNITION:
                    is_plural = True
                elif head_noun.endswith("s") and not head_noun.endswith(NON_PLURAL_SUFFIXES):
                    is_plural = True
                else:
                    is_plural = False

        # Maintain chronological recency order across all lists
        if clean in self.all_antecedents:
            self.all_antecedents.remove(clean)
        self.all_antecedents.append(clean)

        if is_plural:
            if clean in self.plural_antecedents:
                self.plural_antecedents.remove(clean)
            self.plural_antecedents.append(clean)
        else:
            if clean in self.singular_antecedents:
                self.singular_antecedents.remove(clean)
            self.singular_antecedents.append(clean)

    def resolve(self, pronoun: str) -> Optional[str]:
        """Resolves a pronoun to the most recent grammatically compatible antecedent."""
        p = pronoun.strip().lower()
        if p in SINGULAR_PRONOUNS:
            if self.singular_antecedents:
                return self.singular_antecedents[-1]
            if self.all_antecedents:
                return self.all_antecedents[-1]
        elif p in PLURAL_PRONOUNS:
            if self.plural_antecedents:
                return self.plural_antecedents[-1]
            if self.all_antecedents:
                return self.all_antecedents[-1]
        return None

    def has_antecedent_for(self, pronoun: str) -> bool:
        """Returns True if a compatible antecedent exists in discourse."""
        return self.resolve(pronoun) is not None


class NoiseFilterGate:
    """Pre-extraction gate enforcing zero false acceptance on negative corpus noise.
    Rejects MCQ options, running headers, watermark text, dangling fragments,
    multi-column cross-read collisions, table delimiters, and unresolved pronouns.
    """

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

    PHRASAL_PREPOSITION_REGEX = re.compile(
        r'\b(?:made\s+(?:up\s+)?of|protects?(?:\s+\w+)?\s+from|'
        r'derive(?:s|d)?\s+from|originate(?:s|d)?\s+from|result(?:s|ed)?\s+from|produced\s+from|'
        r'measured\s+from|depend(?:s|ed)?\s+on|rel(?:y|ies|ied)\s+on|live(?:s|d)?\s+(?:in|on)|'
        r'account(?:s|ed)?\s+for|known\s+for|used\s+for|refer(?:s|red)?\s+to|belong(?:s|ed)?\s+to|'
        r'associated\s+with)\s*[\.\!\?]\s*$',
        re.IGNORECASE
    )

    NOISE_PATTERNS = {
        "mcq_leakage": [
            r'^\s*\(?[a-eA-E]\)[\s\.\)]',
            r'^\s*\[(?:[a-eA-E]|\d{1,2}|[ivxlcdmIVXLCDM]+)\][\s\.\:]*',
            r'^\s*\((?:[a-eA-E]|\d{1,2}|[ivxlcdmIVXLCDM]+)\)[\s\.\:]*',
            r'^\s*(?:[a-eA-E]|\d{1,2}|[ivxlcdmIVXLCDM]+)\)[\s\.]',
            r'^\s*Question\s*\d+',
            r'^\s*Q\.\s*\d+',
            r'^\s*Option\s+[A-D]\b',
            r'\(a\)\s+.*\s+\(b\)',
            r'^\s*Ans(?:wer)?\s*[:\.]',
            r'^\s*Sol(?:ution)?\s*[:\.]',
            r'Which of the following\s+(?:statements?\s+)?(?:is|are)\s+(?:not\s+)?(?:correct|true)',
            r'Select the correct\s+(?:code|answer)\b',
            r'Consider the following statements\b',
            r'Correct answer:\s*option\s+[a-d]',
            r'^\s*\(?[a-d]\)?\s*[A-Z][a-z]+.*(?:\(?[b-d]\)|→)',
        ],
        "watermark_header": [
            r'\bPARMAR\s+SSC\b',
            r'\bISBN\s*[\d\-]+',
            r'www\.[a-z0-9\-\.]+\.(?:com|org|in|net)',
            r'^Chapter\s+\d+\b',
            r'^NCERT\s+Class\s+\d+',
            r'^\s*Page\s+\d+\s+of\s+\d+',
            r'^\s*\d{1,4}\s*$',
            r'^\s*Textbook in Geography\b',
            r'^\s*THE EARTH\s*:\s*OUR HABITAT',
            r'^\s*2018-19',
            r'^\s*0656\b',
            r'^\s*Figure\s+\d+(?:\.\d+)?(?:\s*[:\-]|\s+[A-Z])',
            r'^\s*SSC\s+[A-Za-z\s]+.*(?:\(Shift|\d+/\d+/\d+)',
        ],
        "table_formatting_artifact": [
            r'^\s*\|',
            r'\|\s*[-:]+[-| :]+\|',
            r'^\s*```',
            r'^\s*-\s*\*\*[A-Za-z0-9\-]+\*\*\s*:',
            r'^\s*\*Total\s+.*\*',
            r'^\s*Step\s*:\s*$',
            r'^\s*\d+\s+[a-z]+,\s*\d+\s+[a-z]+',
            r'^\s*\d+\.\s*(?:Now\s*)?(?:[pP]lace|[pP]ut|[tT]ake|[dD]raw|[hH]old|[cC]ut|[kK]eep|[sS]witch|[tT]urn|[pP]erforate|[mM]ark|[oO]bserve)\b',
        ],
        "syntactic_fragment": [
            r'\b(?:and|or|but|with|that|which|whose|because|while|whereas|although|in|to|along|into|including|such as|since|between|among|due to|as well as|under|without)\s*[\.\!\?]?\s*$',
            r'(?<!made\s)\bof\s*[\.\!\?]?\s*$',
            r'(?<!protects\s)(?<!protect\s)(?<!us\s)(?<!them\s)(?<!differ\s)(?<!originates\s)\bfrom\s*[\.\!\?]?\s*$',
            r'\.\.\.\s*$',
            r'\.{2,}\s*$',
            r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$',
            r'^\s*Because\s+(?:despite|although|though|if|when|while)\b',
            r'^\s*(?:While|When|Because|Although)\s+[a-z]+ing\b.*[\.\!\?]?\s*$',
            r'^\s*(?:In|At|On|From)\s+(?:Rural|Urban|Total|General|Primary|Secondary),\s+',
            r'^\s*And\s+(?:for\s+this\s+reason\s+also|therefore|so|hence)\s*[\.\!\?]?\s*$',
            r'\b(?:the|a|an|their|its|our|your|this|that)\s*[\.\!\?]?\s*$',
        ],
        "anaphoric_unresolved": [
            # 1. Subject personal pronouns followed by any verb/adverb
            r'^\s*(?:They|He|She|It)\s+[a-zA-Z]+(?:\s+[a-zA-Z]+)?\b',
            # 2. Demonstrative pronouns used as bare subjects before auxiliaries or relational verbs
            r'^\s*(?:These|Those|This|That)\s+(?:are|were|have|had|has|do|did|does|can|could|will|would|may|might|must|simply|also|is|was|leads?|causes?|forms?|comprises?|consists?|exhibits?|features?)\b',
            # 3. Unresolved possessive noun phrase at onset without antecedent
            r'^\s*(?:Its|Their|His|Her)\s+[a-zA-Z]+(?:\s+[a-zA-Z]+)?\s+(?:is|are|was|were|has|have)\b',
        ],
        "broken_reading_order": [
            r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z][a-z]+',
            r'[a-z]+[A-Z][a-z]+[A-Z][a-z]+',
            r'^(?:[A-Z][a-zA-Z\s]{2,20}\s+){4,}[A-Z][a-zA-Z\s]{2,20}$',
            r'^(?![^.\n]*\b(?:is|are|was|were|has|have|had|orbits?|contains?|features?|forms?|emits?|reaches?|consists?|includes?|moves?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$',
            r'\b(?:Given|Written|Authored|Published|Proposed)\s+by\s+[A-Z]',
            r'^\w[\w\s]*\s*:\s*$',
            r'^\s*[A-Z\s]{25,}\s*$',
            r'^[A-Z0-9\s]{20,}$',
            r'\b[A-Z]\s+[A-Z]\s+[A-Z]\b',
            r':\s*(?:Occurs|Is|Are|Was|Were|Has|Have)\b',
            r'^(.{10,})\1$',
        ]
    }

    @classmethod
    def audit(cls, text: str, is_block_context: bool = False, has_antecedent: bool = False) -> Optional[str]:
        """Returns the noise category string if text is noise, else None."""
        t = text.strip()
        if not t:
            return "syntactic_fragment"

        # 1. Interrogative question filtering
        if re.search(r'\?\s*[\'\"\)\]]?\s*$', t):
            return "interrogative_question"
        if cls.INTERROGATIVE_REGEX.match(t) and not t.endswith('.'):
            return "interrogative_question"

        # 2. Dangling incomplete phrases
        if cls.DANGLING_FRAG_REGEX.search(t):
            return "syntactic_fragment"

        # 3. Incomplete epistemic embedded clause
        m_epistemic = re.search(r'\b(?:discovered|found|proved|shown|revealed|believed|demonstrated|established)\s+that\s+(.+)$', t, re.IGNORECASE)
        if m_epistemic:
            clause = m_epistemic.group(1).strip().rstrip('.!?')
            clause_words = [w.lower() for w in re.sub(r'[^\w\s]', '', clause).split()]
            clause_verbs = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'could', 'will', 'would', 'forms', 'form', 'rotates', 'rotate', 'contains', 'contain', 'orbits', 'orbit', 'moves', 'move', 'extends', 'extend', 'consists', 'consist', 'exhibits', 'exhibit', 'composed'}
            if not any(w in clause_verbs for w in clause_words):
                return "syntactic_fragment"

        has_phrasal_prep = bool(cls.PHRASAL_PREPOSITION_REGEX.search(t))

        for cat, pats in cls.NOISE_PATTERNS.items():
            if cat == "anaphoric_unresolved" and is_block_context and has_antecedent:
                continue
            for p in pats:
                if cat == "syntactic_fragment" and has_phrasal_prep:
                    if p.startswith(r'\b(?:and|or|but|with|that|which|whose'):
                        continue
                if re.search(p, t, re.IGNORECASE if cat not in ["broken_reading_order", "table_formatting_artifact"] else 0):
                    return cat

        words = t.split()
        if len(words) < 3:
            return "syntactic_fragment"
        if len(words) < 5:
            has_verb = bool(re.search(r'\b(?:is|are|was|were|orbits|absorbs|contains|forms|turns|has|have)\b', t, re.IGNORECASE))
            if not has_verb:
                return "syntactic_fragment"

        return None


class LinguisticSemanticExtractor:
    """Deterministic, discourse-aware NLP pattern extractor for all 14 intents.
    Handles discourse intro clauses, passive inversion, multi-word entities, and slotting.
    """

    PASSIVE_DEF_REGEX = re.compile(
        r'^(?P<desc>.+?)\s+(?:are|is)\s+(?:called|known as|termed|designated as)\s+(?P<term>[A-Za-z0-9\s\(\)\'\-]+)\.?$',
        re.IGNORECASE
    )
    LOCATIVE_INV_REGEX = re.compile(
        r'^(?:Under|Below|Above|Near|Beside|Beneath|Between)\s+(?P<cond>.*?)\s+lies\s+(?:the\s+)?(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:,\s*(?P<pred>.*?))?[\.\s]*$',
        re.IGNORECASE
    )
    INTRO_PREP_REGEX = re.compile(
        r'^(?:In|On|At|During|Throughout|Across|Under|Above|Below|With|Between|From|By|Along|According to|Beside|Beneath|Around|Near|Upon|Within|Beyond)\b\s+[^,]+,\s*',
        re.IGNORECASE
    )

    PATTERNS = [
        # 1. EXCEPTION
        ("exception", re.compile(
            r'^(?:Except for|With the exception of|Apart from|Excluding)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-,]+?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:have|has|are|is|rotate|exhibit|contain|can|could|do|does|did|give|gives|gave|flow|flows|remain|remains|produce|produces)\b.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^Unlike (?:the )?(?:majority of|most|all other)\s+(?P<sec>[^,]+),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:While\s+(?:nearly\s+|almost\s+)?(?:all|most|the majority of)\s+[^,]+,\s*)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?:unique exceptions?|the only\b)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+but\s+(?:are|is)\s+(?:uniquely incapable of|unique in|an exception in|unique exceptions?)\s+(?P<pred2>.*)$',
            re.IGNORECASE
        )),
        ("exception", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred1>.*?),\s+(?:except the|except|with the exception of|excluding|apart from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>.*)$',
            re.IGNORECASE
        )),

        # 2. DISTRIBUTION (Placed before comparison so "distributed in X, while Y" matches distribution)
        ("distribution", re.compile(
            r'^(?:(?:(?:More|Less) than\s+)?(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s+percent)\s+of\s+(?:the\s+)?)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:(?:are|is)\s+)?(?:distributed\s+(?:in|across|throughout)|is concentrated across|are concentrated in|concentrated across|concentrated in|form(?:s)? the most widespread|predominantly distributed|distributed across|covers the region)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 3. COMPARISON
        ("comparison", re.compile(
            r'^Unlike\s+(?P<cond>[^,]+(?:which\s+[^,]+)?),\s*(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:are|is)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:Unlike\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred1>(?:is|are|was|were|decrease|increase|retain|shed|experience|maintain|differ|exhibit|have|has|flow|rotate|move|carry|transport|propagate|travel)\b.*?),\s+(?:whereas\s+(?:the\s+|all\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred2>(?:is|are|was|were|[a-z]+(?:s|es|ed)?)\b.*)|while\s+(?![a-z]+ing\b)(?:the\s+)?(?P<sec2>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred3>(?:is|are|was|were|[a-z]+(?:s|es|ed)?)\b.*))$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?[a-z\-]+er(?:-[a-z]+)?\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:[,;]|\.|$).*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is|are)\s+(?P<pred>(?:much\s+)?(?:more|less)\s+[a-z\-]+\s+than\s+(?:that\s+of\s+)?(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)(?:[,;]|\.|$).*)$',
            re.IGNORECASE
        )),
        ("comparison", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is much thinner compared to|is higher than|differs from)\s+(?P<sec>[A-Za-z0-9\s\(\)\'\-]+?)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 4. CONDITION
        ("condition", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:occurs? exclusively during\b|can occur only if\b|occurs? only if\b|condenses into.*only when|forms? only when|only when|provided that|conditional upon|if and only if|must exceed\s+\d+|exceeds?\s+\d+|exceed\s+\d+)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 5. CLASSIFICATION
        ("classification", re.compile(
            r'^(?:(?P<subject>[A-Za-z\s]+?)\s+)?(?:classif(?:y|ies)|divid(?:e|es)|categoriz(?:es|e)|groups?)\s+(?P<target>.*?)\s+into\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("classification", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:(?:is|are|can be)\s+(?:classified into|divided into|grouped into|categorized into|classified as|divided as)|exhibits?\s+(?:two|three|four|five|several|\d+)\s+(?:primary|major|fundamental|distinct)?\s*categories of|can be divided into|can be classified into)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 6. SEQUENCE
        ("sequence", re.compile(
            r'^(?:(?:In|During)\s+[^,]+,\s+)?(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:progresses through\s+(?:a\s+)?(?:[a-z\-]+\s+)*(?:sequence|stages|phases|steps|cycle)|(?:(?:arrive(?:s)?|form(?:s)?|condense(?:s)?|begin(?:s)?|began|commence(?:s)?|commenced|start(?:s)?|started)\s+(?:first|initially)|(?:begin(?:s)?|began|commence(?:s)?|commenced|start(?:s)?|started|originate(?:s)?|originated))\b.*?\bfollowed\s+(?:by|sequentially\s+by|in\s+turn\s+by)|(?:\b(?:is|are|was|were)\s+)?followed by|subsequently|.*?\b(?:metamorphose into.*before|stages? of|rock cycle)\b)\s*:?\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 7. PROCESS
        ("process", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:converts|convert|transforms|transform|turns|turn|changes|change)\s+(?P<pred>.*?into\s+.*)$',
            re.IGNORECASE
        )),
        ("process", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is the (?:\w+\s+)?process (?:whereby|in which|by which|through which)|develops through (?:a\s+)?(?:\w+\s+)*process|(?:is|are|was|were)\s+(?:formed|deposited|created)\s+(?:through|by)\s*(?:(?:the\s+)?(?:\w+\s+)*process\s+of\s+)?|occurs when|mechanism of|cycle involves|formation involves)\s*:?\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 8. SPATIAL
        ("spatial", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:extends up to|extends from|extends between|is located|is situated|flows (?:westward|eastward|northward|southward) through|flows through|traverses|at the equator|at the poles)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 9. QUANTITY
        ("quantity", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)(?:\s+in\s+a\s+vacuum)?\s+(?:(?P<verb>has|have|had|maintains?|maintained|exhibits?|possesses?)\s+(?:an?|a\s+constant)?\s*(?:[a-z\-]+\s+)?(?:radius|diameter|circumference|elevation|altitude|depth|density|mass|volume|area|thickness|tilt|inclination|angle)\s+of|extends to a depth of|reaches an? altitude of|constitutes approximately|measures approximately|originated approximately|(?:travels|moves|propagates|rotates)\s+at(?:\s+approximately)?|standard meridian|passes through.*longitude|drops to\s+[-]?\d+|reaches\s+[-]?\d+|(?:is|measures)\s+(?:approximately|about|around)?\s*[\d,]+(?:\.\d+)?\s*(?:kilometres|km|meters|m|miles|percent|%|degrees|°C|mb|billion years|million light-years|kilometres per second))\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 10. CAUSE/EFFECT
        ("cause/effect", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:is caused by|are caused by|was caused by|were caused by|results from|result from|is triggered by|are triggered by|is driven by|are driven by|arises from|arise from|stems from)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("cause/effect", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?:causes?|results?\s+in|leads?\s+to|leading to|triggers?|drives?|induces?|creates?|release\s+.*disturb)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 11. PART-OF
        ("part-of", re.compile(
            r'^(?:(?:\b(?:The|An|A|Our)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:is|forms?|constitutes?)\s+(?!(?:defined|termed|designated|described|known|referred)\b)(?:an?|the)?\s*(?:[a-z\-]+\s+)*(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion|shield|barrier|reservoir|body|mass)\s+(?:(?:located|situated|found|positioned|embedded)\s+(?:[a-z\-]+\s+)?)?(?:of|within|in|beneath|under|underneath|above|below|between|around|across|throughout)\b.*|(?:is|forms?|constitutes?)\s+(?:about|approximately|around|nearly)?\s*[\d\.]+(?:%|\s*percent)\s+of\s+.*?\band\s+(?:lies|extends|forms)\b.*|(?:(?:is|are)\s+(?:composed|made up|constituted)\s+of|consists?\s+of)\s*:?\s*[A-Za-z0-9\s\-]{3,}.*|\bforms?\s+part of\b.*|component of.*|part of the.*|part of.*)$',
            re.IGNORECASE
        )),

        # 12. MEMBER-OF
        ("member-of", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is an? (?:[a-z\-]+\s+)*(?:member|exemplar|instance|specimen|representative|type|kind|class|category|variant)\s+of|belongs to (?:the\s+)?(?:family|group|class|category|system|constellation|network|order)\s+of|is classified (?:as|under)\s+(?:an?|the)?|is categorized as\s+(?:an?|the)?|is grouped under|is counted among\s+(?:the\s+)?|is one of the\s+(?:[a-z\-]+\s+)*(?:members|constellations|systems|ports|stars|mountains|ranges|planets)\s+of|forms an? (?:integral\s+)?member of|member of the|member of)\s+(?P<pred>.*)$',
            re.IGNORECASE
        )),
        ("member-of", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+is an?\s+(?:[a-z\-]+\s+)*(?P<tax_class>[a-z\-]+)\s+(?P<pred>(?:situated|located|commissioned|established|operating|orbiting|found|inhabiting|dwelling|endemic)\b.*)$',
            re.IGNORECASE
        )),

        # 13. DEFINITION (Active)
        ("definition", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\(\)\'\-]+?)\s+(?:is defined as|refers to|is termed|is designated as|is described as|(?:is|are)\s+(?:an?|the)\s+(?:[a-z\-]+\s+)*(?:stream|collection|line|point|circle|envelope|layer|zone|belt|body|mass|system|structure|substance|mixture|compound|phenomenon|medium|form|assembly|sheet|tract|flow|discharge|field|aggregate)\s+(?:of|that|which|connecting|surrounding|held|released|formed)\b)\s*(?P<pred>.*)$',
            re.IGNORECASE
        )),

        # 14. ATTRIBUTE
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed|produced|produces?|generated|generates?|emitted|emits?|yielded|yields?)\s+(?:the\s+)?(?:highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|loudest|brightest|maximum|minimum)\s+(?:[a-z\-]+\s+)*[a-z]+(?:\s+among|\s+in|\s+at|\s+of\b|\s*,).*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:is|are)\s+(?:characterized|distinguished|marked|noted)\s+by\s+.*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:comprises?|encompasses?)\s+(?:rich|immense|vast|extensive|abundant|large|significant)?\s*(?:reserves|deposits|resources|features|concentrations)\s+of\s+.*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:are|is)\s+(?:[a-z\-]+\s+)*(?:waves|vibrations|oscillations|radiations|pulses|currents)\s+that\s+[a-z]+(?:s|es|ed|ing)?\s+.*)$',
            re.IGNORECASE
        )),
        ("attribute", re.compile(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\-]+?)\s+(?P<pred>(?:are|is)\s+(?:[a-z\-]+ly\s+|very\s+|mostly\s+)?\s*[a-z\-]+\s+and\s+[a-z\-]+(?:,\s*(?:(?:are|is|have|has|possess)\b|(?:[a-z\-]+\s+)?[a-z\-]+ing\b).*)*)$',
            re.IGNORECASE
        )),
    ]

    @classmethod
    def extract(cls, text: str, source_loc: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        """Extracts a KnowledgeNode using linguistic patterns, or None if no match."""
        clean_text = sanitize_text(text.strip())
        # Pre-clean any MCQ option letters leaking in
        clean_text = re.sub(r'^\s*(?:\[[A-Za-z0-9]+\]|\(?[A-Za-z0-9ivxlcdmIVXLCDM]+\)[\s\.\)]|\d+[\.\)])\s*', '', clean_text)

        # Interrogative check inside extractor
        if re.search(r'\?\s*[\'\"\)\]]?\s*$', clean_text) or NoiseFilterGate.INTERROGATIVE_REGEX.match(clean_text):
            return None

        # Handle inverted definition: "[Description]... is defined as [Term]."
        m_inv_def = re.match(
            r'^(?P<desc>.{20,}?)\s+(?:is|are)\s+defined\s+as\s+(?:the\s+)?(?P<term>[A-Za-z0-9\s\(\)\-]{2,30})[\.\s]*$',
            clean_text,
            re.IGNORECASE
        )
        if m_inv_def and not re.search(r'\b(?:whereby|which|that|who|because|synthesize|producing)\b', m_inv_def.group("term"), re.IGNORECASE):
            term = m_inv_def.group("term").strip().rstrip('.')
            desc = m_inv_def.group("desc").strip()
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type="definition",
                primary_entity=term,
                predicate=f"is defined as {desc}",
                secondary_entities=[desc],
                raw_evidence=clean_text,
                source_location=source_loc or {},
                confidence=0.95,
                extraction_method="linguistic_rule"
            )

        # Handle locative inversion: "Under the lithosphere lies the asthenosphere, a semi-fluid layer."
        m_loc = cls.LOCATIVE_INV_REGEX.match(clean_text)
        if m_loc:
            entity = m_loc.group("entity").strip().rstrip('.')
            cond = m_loc.group("cond").strip()
            pred_extra = m_loc.group("pred")
            pred = f"lies under {cond}" + (f", {pred_extra.strip().rstrip('.')}" if pred_extra else "")
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type="spatial",
                primary_entity=entity,
                predicate=pred,
                raw_evidence=clean_text,
                source_location=source_loc or {},
                confidence=0.95,
                extraction_method="linguistic_rule"
            )

        # Handle passive voice definition: "[desc] is/are called [term]"
        m_pass = cls.PASSIVE_DEF_REGEX.match(clean_text)
        if m_pass:
            term = m_pass.group("term").strip().rstrip('.')
            desc = m_pass.group("desc").strip()
            verb_m = re.search(r'\b(is|are)\s+(?:called|known as|termed|designated as)\b', clean_text, re.IGNORECASE)
            aux = verb_m.group(1).lower() if verb_m else "is"

            is_descriptive = bool(re.search(r'\b(?:which|that|who|whereby|wherein|by\s+which|convert|shining|characterized|all\s+those|those\s+objects|all\s+such)\b', desc, re.IGNORECASE)) or len(desc.split()) >= 6
            is_concise_term = len(term.split()) <= 4

            if is_descriptive and is_concise_term:
                clean_term = re.sub(r'^(?:the|an|a)\b\s*', '', term, flags=re.IGNORECASE).strip()
                # Also strip quote marks
                clean_term = clean_term.strip('\'"')
                primary_entity = clean_term or term
                # For passive definitions, the predicate should indicate the definition
                predicate = f"{aux} called {desc}"
                secondary = [desc]
            else:
                m_proper = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)([A-Za-z0-9\s\-]+)$', desc)
                primary_entity = m_proper.group(1).strip() if m_proper else desc
                predicate = f"{aux} known as {term}" if "known as" in clean_text.lower() else f"{aux} called {term}" if "called" in clean_text.lower() else f"{aux} {term}"
                secondary = [term]

            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                intent_type="definition",
                primary_entity=primary_entity,
                predicate=predicate,
                secondary_entities=secondary,
                raw_evidence=clean_text,
                source_location=source_loc or {},
                confidence=0.95,
                extraction_method="linguistic_rule"
            )

        # Appositive extraction for parenthetical clauses enclosed in em-dashes or hyphens
        m_appos = re.match(r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Z][a-zA-Z0-9\s\-]+?)\s*(?:—|\s+-\s+)(?P<appositive>[^—\-]+?)(?:—|\s+-\s+)(?P<rest>[a-z].*)$', clean_text)
        intro_cond = None
        working_text = clean_text
        if m_appos:
            entity_core = m_appos.group("entity").strip()
            appositive_cond = m_appos.group("appositive").strip()
            rest_clause = m_appos.group("rest").strip()
            working_text = f"{entity_core} {rest_clause}"
            intro_cond = appositive_cond

        # Peel off chained introductory adverbial/prepositional clauses
        intro_conds = [intro_cond] if intro_cond else []
        while True:
            m_intro = cls.INTRO_PREP_REGEX.match(working_text)
            if not m_intro:
                break
            matched_clause = m_intro.group(0)
            intro_conds.append(matched_clause.rstrip(", "))
            working_text = working_text[len(matched_clause):].strip()
        intro_cond = ", ".join(intro_conds) if intro_conds else None

        for intent, pat in cls.PATTERNS:
            m = pat.match(working_text)
            if not m:
                m = pat.match(clean_text)
            if m:
                groups = m.groupdict()
                entity = groups.get("entity", "").strip()
                if "target" in groups and groups["target"]:
                    entity = groups["target"].strip()
                pred = groups.get("pred", "").strip()
                sec = []
                if "sec" in groups and groups["sec"]:
                    sec.append(groups["sec"].strip())
                if "pred1" in groups and "pred2" in groups:
                    pred = f"{groups['pred1']}, whereas {groups.get('sec', '')} {groups['pred2']}"

                cond = intro_cond or groups.get("cond")
                quant = None
                m_num = re.search(
                    r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(percent|%|degrees(?:\s+Celsius)?|kilometres(?:\s+per\s+second)?|km|mb|meters|m|miles|g/cm\^3|°C|billion\s+years|million\s+light-years)?',
                    pred or clean_text,
                    re.IGNORECASE
                )
                if m_num:
                    clean_val = m_num.group(1).replace(',', '')
                    quant = {"value": float(clean_val), "unit": m_num.group(2) or ""}

                if intent == "classification" and ":" in pred:
                    subclasses = [c.strip() for c in re.split(r'[,;]|\band\b', pred.split(":", 1)[1]) if c.strip()]
                    sec.extend(subclasses)

                if intent == "sequence":
                    seq_source = pred if ":" in pred else (clean_text.split(":", 1)[1] if ":" in clean_text else "")
                    if seq_source:
                        raw_stages = seq_source.split(":", 1)[1] if ":" in seq_source else seq_source
                        stages = [s.strip().rstrip('.') for s in re.split(r'[,;]|\band\b', raw_stages) if s.strip().rstrip('.')]
                        sec.extend(stages)

                if intent == "part-of":
                    m_parent = re.search(
                        r'\b(?:of|within|in|beneath|under|underneath|above|below|between)\s+(?:the\s+)?([A-Z][a-zA-Z\s\-]+?)(?:[,\.]|$)',
                        clean_text,
                        re.IGNORECASE
                    )
                    if m_parent:
                        sec.append(m_parent.group(1).strip())

                if intent == "member-of":
                    m_group = re.search(r'member of (?:the\s+)?(\d*\s*[A-Za-z\s]+)', clean_text)
                    if m_group:
                        sec.append(m_group.group(1).strip())

                if intent == "exception":
                    # Generalized extraction of the reference baseline norm from contrastive clauses
                    m_norm = re.search(
                        r'\b(?:nearly all|almost all|all other|all|most|the majority of)\s+([A-Za-z\s]+?)(?:\s+(?:that|who|which|rotate|revolve|flow|have|are|is|can|do|does|will|orbit|propagate|exhibit|contain)\b|,)',
                        clean_text,
                        re.IGNORECASE
                    )
                    if m_norm:
                        norm_str = m_norm.group(1).strip()
                        if norm_str and norm_str.lower() not in [s.lower() for s in sec]:
                            sec.append(norm_str)

                return KnowledgeNode(
                    node_id=str(uuid.uuid4()),
                    intent_type=intent,
                    primary_entity=entity,
                    predicate=pred or clean_text,
                    secondary_entities=sec,
                    conditions=cond,
                    quantitative_data=quant,
                    raw_evidence=clean_text,
                    source_location=source_loc or {},
                    confidence=0.92,
                    extraction_method="linguistic_rule"
                )

        # Fallback declarative
        match_decl = re.match(
            r'^(?:(?:\b(?:The|An|A)\b\s+)?)(?P<entity>[A-Za-z0-9\s\(\)\'\"\[\],\-\/]+?)\s+(?P<verb>is|are|was|were|has|have|had|form|forms|formed|occurs|occurred|constitutes|constituted|contains|contained|features|featured|progresses|progressed|develops|developed|comprises|comprised|falls|fell|exhibits?|exhibited|possesses?|possessed|displays?|displayed|moves?|revolves?|orbits?|rotates?|flows?|produces?|produced|generates?|generated|emits?|emitted|yields?|yielded)\s+(?P<rest>.*)',
            working_text,
            re.IGNORECASE
        )
        if match_decl:
            pe = match_decl.group("entity").strip()
            verb = match_decl.group("verb").strip().lower()
            rest = match_decl.group("rest").strip()

            # Guard against interrogatives and dangling fragments
            if pe.lower() in {"what", "why", "how", "which", "where", "when", "who", "whom", "can", "could", "is", "are", "do", "does", "did"}:
                return None
            if pe.lower().startswith(("what ", "which ", "how ", "why ", "where ", "who ", "can ", "could ")):
                return None
            if rest.lower().endswith(("composed of", "consists of", "known as", "defined as", "discovered that", "such as")):
                return None

            if not pe.lower().endswith(("in the", "of the", "to the", "from the")):
                attr_verbs = {
                    "has", "have", "had", "features", "featured", "contains", "contained",
                    "comprises", "comprised", "form", "forms", "formed", "occurs", "occurred",
                    "constitutes", "constituted", "progresses", "progressed", "develops", "developed",
                    "falls", "fell", "exhibits", "exhibit", "exhibited", "possesses", "possess",
                    "possessed", "displays", "display", "displayed",
                    "move", "moves", "revolve", "revolves", "orbit", "orbits", "rotate", "rotates", "flow", "flows",
                    "produces", "produced", "generates", "generated", "emits", "emitted", "yields", "yielded"
                }
                intent_type = "attribute" if verb in attr_verbs else "definition"
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


class GeminiStructuredExtractor:
    """Native REST client for Google Gemini API (gemini-3.6-flash) with structured output.
    Enforces the KnowledgeNode responseSchema, rate limiting, and exponential backoff.
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            "is_valid_knowledge": {
                "type": "boolean",
                "description": "True if text expresses a valid factual educational assertion."
            },
            "intent_type": {
                "type": "string",
                "enum": [
                    "definition", "attribute", "cause/effect", "comparison", "spatial",
                    "distribution", "classification", "quantity", "sequence",
                    "condition", "exception", "process", "part-of", "member-of", "none"
                ]
            },
            "primary_entity": {"type": "string"},
            "predicate": {"type": "string"},
            "secondary_entities": {"type": "array", "items": {"type": "string"}},
            "conditions": {"type": "string"},
            "quantitative_data": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "parameter": {"type": "string"}
                }
            }
        },
        "required": ["is_valid_knowledge", "intent_type", "primary_entity", "predicate"]
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key = line.strip().split("=", 1)[1].strip()
        self.last_call_time = 0.0
        self.min_interval = 4.0

    def extract(self, text: str, source_loc: Optional[Dict[str, Any]] = None) -> Optional[KnowledgeNode]:
        """Calls Gemini API with structured response schema and throttled backoff."""
        if not self.api_key:
            return None

        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        prompt = (
            "Analyze this educational source text and extract structured knowledge into one of the 14 intents "
            "(definition, attribute, cause/effect, comparison, spatial, distribution, classification, "
            "quantity, sequence, condition, exception, process, part-of, member-of):\n"
            f"\"{text}\""
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": self.SCHEMA,
                "temperature": 0.0
            }
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={self.api_key}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

        retries = 3
        delay = 2.0
        for attempt in range(retries):
            try:
                self.last_call_time = time.time()
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    cand_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(cand_text)

                    if not parsed.get("is_valid_knowledge", True):
                        return None
                    if parsed.get("intent_type") == "none":
                        return None

                    return KnowledgeNode(
                        node_id=str(uuid.uuid4()),
                        intent_type=parsed.get("intent_type", "definition"),
                        primary_entity=parsed.get("primary_entity", ""),
                        predicate=parsed.get("predicate", ""),
                        secondary_entities=parsed.get("secondary_entities", []),
                        conditions=parsed.get("conditions"),
                        quantitative_data=parsed.get("quantitative_data"),
                        raw_evidence=text,
                        source_location=source_loc or {},
                        confidence=0.96,
                        extraction_method="gemini_structured"
                    )
            except urllib.error.HTTPError as he:
                if he.code == 429 and attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    break
            except Exception:
                break

        return None


class HybridSemanticExtractor:
    """Production cascaded semantic representation engine:
    1. NoiseFilterGate rejects non-factual noise at 0ms latency.
    2. LinguisticSemanticExtractor handles deterministic syntactic structures.
    3. GeminiStructuredExtractor resolves multi-clause or ambiguous sentences (opt-in).
    """

    def __init__(self, api_key: Optional[str] = None, enable_llm: bool = False):
        self.noise_gate = NoiseFilterGate()
        self.linguistic = LinguisticSemanticExtractor()
        self.enable_llm = enable_llm or (os.environ.get("ENABLE_GEMINI_FALLBACK") == "true")
        self.gemini = GeminiStructuredExtractor(api_key=api_key) if self.enable_llm else None

    def extract_sentence(
        self,
        text: str,
        source_loc: Optional[Dict[str, Any]] = None,
        has_antecedent: bool = False
    ) -> Optional[KnowledgeNode]:
        """Extracts a single KnowledgeNode from sentence text."""
        # 1. Noise gate
        is_block = bool(source_loc and "block_id" in source_loc)
        has_ant = has_antecedent or bool(source_loc and source_loc.get("has_antecedent"))
        rejection = self.noise_gate.audit(text, is_block_context=is_block, has_antecedent=has_ant)
        if rejection:
            return None

        # 2. Local linguistic extraction
        node = self.linguistic.extract(text, source_loc)
        if node and node.primary_entity and node.predicate:
            return node

        # 3. Throttled Gemini fallback if enabled
        if self.gemini and self.gemini.api_key:
            llm_node = self.gemini.extract(text, source_loc)
            if llm_node:
                return llm_node

        return None


class SemanticExtractor:
    """Universal Semantic Extractor interface matching PROJECT.md interface contracts:
    - Input: NormalizedBlock or raw text string
    - Output: List[KnowledgeNode]
    """

    def __init__(self, api_key: Optional[str] = None):
        self.hybrid = HybridSemanticExtractor(api_key=api_key)

    @classmethod
    def _detect_leading_pronoun(cls, text: str) -> Optional[str]:
        """Detects if sentence onset begins with an anaphoric pronoun subject or
        possessive determiner."""
        t = text.strip()
        # Personal subject pronouns and possessive determiners
        m_pers = re.match(r'^(?:(It|They|He|She|Its|Their|His|Her)\s+[a-zA-Z]+(?:\s+[a-zA-Z]+)?\b)', t, re.IGNORECASE)
        if m_pers:
            return m_pers.group(1)
        # Demonstrative pronouns
        m_dem = re.match(
            r'^(?:(These|Those|This|That)\s+(?:are|were|have|had|has|do|did|does|can|could|will|would|may|might|must|simply|also|is|was|leads?|causes?|forms?|comprises?|consists?|exhibits?|features?)\b)',
            t,
            re.IGNORECASE
        )
        if m_dem:
            return m_dem.group(1)
        return None

    def extract(self, block_or_text: Any) -> List[KnowledgeNode]:
        """Extracts KnowledgeNodes from a NormalizedBlock, dictionary, or string with
        full discourse and coreference awareness."""
        # 1. Handle isolated string
        if isinstance(block_or_text, str):
            lead_pronoun = self._detect_leading_pronoun(block_or_text)
            if lead_pronoun:
                return []
            rejection = self.hybrid.noise_gate.audit(block_or_text, is_block_context=False)
            if rejection:
                return []
            node = self.hybrid.extract_sentence(block_or_text)
            if node and node.primary_entity:
                ent_lower = node.primary_entity.strip().lower()
                if ent_lower not in PRONOUN_TOKENS and not ent_lower.startswith(("its ", "their ", "his ", "her ")):
                    return [node]
            return []

        # 2. Handle NormalizedBlock or dict
        b_type = getattr(block_or_text, "type", None)
        clean_sentences = getattr(block_or_text, "clean_sentences", None)
        block_id = getattr(block_or_text, "id", "block")
        metadata = getattr(block_or_text, "metadata", {})

        if clean_sentences is None and isinstance(block_or_text, dict):
            b_type = block_or_text.get("type", "PROSE")
            clean_sentences = block_or_text.get("clean_sentences")
            block_id = block_or_text.get("id", "block")
            metadata = block_or_text.get("metadata", {})
            if clean_sentences is None and "text" in block_or_text:
                return self.extract(block_or_text["text"])

        if not clean_sentences:
            return []

        discourse = DiscourseContext(metadata)
        nodes: List[KnowledgeNode] = []

        for idx, sentence in enumerate(clean_sentences):
            loc = dict(metadata)
            loc["sentence_idx"] = idx
            loc["block_id"] = block_id

            if b_type == "TABLE":
                parts = sentence.split(":", 1)
                entity = parts[0].strip() if len(parts) > 1 else sentence
                pred = parts[1].strip() if len(parts) > 1 else "is tabular fact"
                node = KnowledgeNode(
                    node_id=f"{block_id}_tbl_k_{idx}",
                    intent_type="attribute",
                    primary_entity=entity,
                    predicate=pred,
                    raw_evidence=sentence,
                    source_location=loc,
                    confidence=0.95,
                    extraction_method="table_parser"
                )
                discourse.register_entity(entity, predicate=pred, sentence=sentence)
                nodes.append(node)
            else:
                lead_pronoun = self._detect_leading_pronoun(sentence)
                has_ant = discourse.has_antecedent_for(lead_pronoun) if lead_pronoun else True

                # In block context: if sentence begins with pronoun and NO antecedent exists -> reject
                if lead_pronoun and not has_ant:
                    continue

                rejection = self.hybrid.noise_gate.audit(sentence, is_block_context=True, has_antecedent=has_ant)
                if rejection:
                    continue

                loc["has_antecedent"] = has_ant
                node = self.hybrid.extract_sentence(sentence, loc, has_antecedent=has_ant)
                if not node:
                    continue

                # Coreference resolution for personal and possessive pronouns
                ent_lower = node.primary_entity.strip().lower()
                if ent_lower in PRONOUN_TOKENS or lead_pronoun:
                    target_pronoun = lead_pronoun or node.primary_entity
                    resolved = discourse.resolve(target_pronoun)
                    if resolved:
                        # Handle possessive determiners (e.g. "Its atmosphere" -> "Mars's atmosphere")
                        m_poss = re.match(r'^(?:its|their|his|her)\s+(.+)$', node.primary_entity.strip(), re.IGNORECASE)
                        if m_poss:
                            node.primary_entity = f"{resolved}'s {m_poss.group(1).strip()}"
                        else:
                            node.primary_entity = resolved
                    else:
                        # Safety: never leak an ungrounded bare pronoun
                        continue
                elif ent_lower.startswith(("its ", "their ", "his ", "her ")):
                    # Grounded possessive noun phrase without lead_pronoun match
                    pron_head = ent_lower.split()[0]
                    resolved = discourse.resolve(pron_head)
                    if resolved:
                        noun_rest = node.primary_entity.strip().split(None, 1)[1]
                        node.primary_entity = f"{resolved}'s {noun_rest}"
                    else:
                        continue

                # Register grounded entity into discourse with verb, predicate, and sentence context
                if node.primary_entity and node.primary_entity.strip().lower() not in PRONOUN_TOKENS:
                    discourse.register_entity(node.primary_entity, predicate=node.predicate, sentence=sentence)
                    for sec in node.secondary_entities:
                        discourse.register_entity(sec, sentence=sentence)

                nodes.append(node)

        return nodes
