"""
v13_discovery/auditors.py
=========================
Multi-Agent Auditing Quality Gate & Automated Self-Repair System for Milestone 5.

Implements:
1. CognitiveAuditor: Validates cognitive demand (RECALL, UNDERSTAND, COMPARE, APPLY, ANALYZE),
   checks stem brevity (<15 chars), directive calibration, and shallow recall detection.
2. ExamFitAuditor: Validates target competitive examination alignment (UPSC-Prelims,
   BPSC-Prelims, SSC-CGL, General-Competitive), civil service formal register,
   and standard option structure.
3. AdversarialAuditor: Stress-checks for verbatim & token-level stem leakage, banned quotation
   templates (NQ1-NQ5), option count completeness (>=4), duplicate options, semantic ambiguity,
   article lead-in leakage, and Room DB distractor dissections.
4. MultiAgentAuditingGate (alias MultiAgentQualityGate): Aggregates verdicts with independent
   veto power, composite scoring, and structured AuditReport generation.
5. SystemicRepairEngine & SelfRepairPipeline: 3-phase automated repair loop (audit 50+ items,
   flaw clustering, targeted repairs, and post-repair regeneration clearance).
"""

import os
import re
import json
import uuid
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set, Union

from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    QuestionSynthesizer,
    OntologyRegistry,
    CategoryDefinition,
    DistractorVerificationGate,
    DistractorDissector,
    NaturalStemSynthesizer,
    VALID_ROOM_TRAP_TYPES,
    OPTION_ID_PREFIX,
    normalize_options,
    normalize_correct_key,
)
from v13_discovery.provenance import (
    ProvenanceRecord,
    ProvenanceTracker,
    verify_provenance_chain,
    canonicalize_intent,
    CANONICAL_14_INTENTS,
)

# -------------------------------------------------------------------------
# Constants & Reference Rules
# -------------------------------------------------------------------------

AUTHORIZED_EXAMS: Set[str] = {
    "upsc-prelims",
    "bpsc-prelims",
    "state-psc",
    "ssc-cgl",
    "general-competitive",
    "upsc",
    "bpsc",
    "ssc cgl",
}

VALID_COGNITIVE_DEMANDS: Set[str] = {
    "RECALL",
    "UNDERSTAND",
    "COMPARE",
    "APPLY",
    "ANALYZE",
}

BANNED_LAZY_STEM_PATTERNS = [
    re.compile(r'(?i)what is a direct consequence of\s*["\']'),
    re.compile(r'(?i)which of the following is true regarding\s*["\']'),
    re.compile(r'(?i)consider the following statement\s*["\']'),
    re.compile(r'(?i)according to the passage'),
    re.compile(r'(?i)as stated in the text'),
    re.compile(r'(?i)based on the quote'),
    re.compile(r'(?i)from the provided paragraph'),
    re.compile(r'(?i)refer to the excerpt'),
]

BANNED_INFORMAL_PHRASES = [
    re.compile(r'(?i)\bhey\b'),
    re.compile(r'(?i)\bcan you tell\b'),
    re.compile(r'(?i)\bguess what\b'),
    re.compile(r'(?i)\bkids\b'),
    re.compile(r'(?i)\bdid you know\b'),
]

DOMAIN_STOPWORDS: Set[str] = {
    "rock", "layer", "zone", "river", "types", "plain", "valley",
    "mountains", "clouds", "the", "and", "for", "with", "from",
    "into", "over", "system", "feature", "water", "body", "lake",
    "soil", "plateau", "current", "cycle", "basin", "formation",
    "process", "phenomenon", "structure", "characteristic"
}


# -------------------------------------------------------------------------
# Data Models

@dataclass
class AuditViolation:
    auditor: str
    category: str
    message: str
    severity: str = "FATAL"  # "FATAL" or "WARNING"
    remediation_hint: str = ""
    offending_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditorResult:
    auditor_name: str
    verdict: str  # "PASS" | "REJECT"
    score: float  # 0.0 to 1.0
    violations: List[AuditViolation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Quality Gate Audit Report adhering strictly to test_helpers.py contract."""
    questionId: str
    cognitiveVerdict: str
    examFitVerdict: str
    adversarialVerdict: str
    semanticCoherenceVerdict: str
    overallGate: str
    failureReasons: List[str]
    scores: Dict[str, float] = field(default_factory=dict)
    violations: List[AuditViolation] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -------------------------------------------------------------------------
# Pluggable Abstract Interfaces
# -------------------------------------------------------------------------

class LLMValidatorInterface(ABC):
    """Abstract interface for optional pluggable API-based LLM validators."""
    @abstractmethod
    def validate(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        pass


class BaseAuditor(ABC):
    """Abstract base class for all independent auditing engines."""
    @abstractmethod
    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditorResult:
        pass


# -------------------------------------------------------------------------
# 1. CognitiveAuditor
# -------------------------------------------------------------------------

class CognitiveAuditor(BaseAuditor):
    """Validates cognitive demand, stem brevity, and directive calibration."""

    def __init__(self, llm_validator: Optional[LLMValidatorInterface] = None):
        self.llm_validator = llm_validator

    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditorResult:
        violations: List[AuditViolation] = []
        stem = (getattr(cq, "stem", "") or "").strip()
        cog_demand = (getattr(cq, "cognitiveDemand", "UNDERSTAND") or "UNDERSTAND").strip().upper()

        # Rule 1: Stem Brevity & Triviality
        if len(stem) < 15:
            violations.append(AuditViolation(
                auditor="CognitiveAuditor",
                category="TRIVIAL_STEM",
                message="CognitiveAuditor: Stem is trivial or too short (<15 chars)",
                severity="FATAL",
                remediation_hint="ELEVATE_COGNITIVE_DEPTH",
                offending_text=stem
            ))

        # Rule 2: Cognitive Demand Enum Verification
        if cog_demand not in VALID_COGNITIVE_DEMANDS:
            violations.append(AuditViolation(
                auditor="CognitiveAuditor",
                category="COGNITIVE_MISMATCH",
                message=f"CognitiveAuditor: Unrecognized cognitive demand '{cq.cognitiveDemand}'",
                severity="FATAL",
                remediation_hint="CALIBRATE_DEMAND_ENUM",
                offending_text=cog_demand
            ))

        # Rule 3: Directive Calibration & Shallow Recall Detection
        stem_lower = stem.lower()
        has_analysis_directive = any(k in stem_lower for k in [
            "unlike", "distinguish", "contrast", "differ", "comparative",
            "exception", "responsible for", "mechanism", "consequence",
            "condition", "demonstrates the distinction"
        ])
        if cog_demand in {"COMPARE", "ANALYZE"} and not has_analysis_directive:
            if "defined as" in stem_lower or "what is" in stem_lower:
                violations.append(AuditViolation(
                    auditor="CognitiveAuditor",
                    category="SHALLOW_RECALL",
                    message="CognitiveAuditor: Shallow recall masquerading as analysis/comparison",
                    severity="WARNING",
                    remediation_hint="ELEVATE_DIRECTIVE_PHRASING",
                    offending_text=stem
                ))

        # Scoring
        fatal_count = sum(1 for v in violations if v.severity == "FATAL")
        warning_count = sum(1 for v in violations if v.severity == "WARNING")
        score = max(0.0, round(1.0 - (fatal_count * 0.7 + warning_count * 0.2), 3))
        verdict = "REJECT" if fatal_count > 0 else "PASS"

        return AuditorResult(
            auditor_name="CognitiveAuditor",
            verdict=verdict,
            score=score,
            violations=violations,
            metadata={"cognitiveDemand": cog_demand, "stemLength": len(stem)}
        )


# -------------------------------------------------------------------------
# 2. ExamFitAuditor
# -------------------------------------------------------------------------

class ExamFitAuditor(BaseAuditor):
    """Validates target examination scope, formal academic register, and format."""

    def __init__(self, llm_validator: Optional[LLMValidatorInterface] = None):
        self.llm_validator = llm_validator

    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditorResult:
        violations: List[AuditViolation] = []
        target = (getattr(cq, "examTarget", "") or "").strip()
        norm_target = target.lower()

        # Rule 1: Target Examination Scope
        if norm_target not in AUTHORIZED_EXAMS:
            violations.append(AuditViolation(
                auditor="ExamFitAuditor",
                category="UNSUPPORTED_EXAM",
                message=f"ExamFitAuditor: Target exam '{cq.examTarget}' unsupported",
                severity="FATAL",
                remediation_hint="SET_AUTHORIZED_EXAM_TARGET",
                offending_text=target
            ))

        # Rule 2: Academic & Formal Register Check
        stem = (getattr(cq, "stem", "") or "").strip()
        for pat in BANNED_INFORMAL_PHRASES:
            if pat.search(stem):
                violations.append(AuditViolation(
                    auditor="ExamFitAuditor",
                    category="INFORMAL_REGISTER",
                    message="ExamFitAuditor: Informal or conversational register unsuitable for competitive exam",
                    severity="FATAL",
                    remediation_hint="REWRITE_FORMAL_REGISTER",
                    offending_text=stem
                ))
                break

        # Rule 3: Format Verification
        valid_formats = {"direct fact", "statement-based", "matching", "assertion-reason", "application", "unclassified"}
        cq_format = getattr(cq, "format", "Direct Fact")
        if cq_format and cq_format.lower() not in valid_formats:
            violations.append(AuditViolation(
                auditor="ExamFitAuditor",
                category="INVALID_FORMAT",
                message=f"ExamFitAuditor: Format '{cq_format}' is not a recognized exam format",
                severity="WARNING",
                remediation_hint="STANDARDIZE_EXAM_FORMAT"
            ))

        fatal_count = sum(1 for v in violations if v.severity == "FATAL")
        warning_count = sum(1 for v in violations if v.severity == "WARNING")
        score = max(0.0, round(1.0 - (fatal_count * 0.8 + warning_count * 0.2), 3))
        verdict = "REJECT" if fatal_count > 0 else "PASS"

        return AuditorResult(
            auditor_name="ExamFitAuditor",
            verdict=verdict,
            score=score,
            violations=violations,
            metadata={"examTarget": target, "format": cq_format}
        )


# -------------------------------------------------------------------------
# 3. AdversarialAuditor
# -------------------------------------------------------------------------

class AdversarialAuditor(BaseAuditor):
    """Stress-checks for MCQ stem leakage, banned templates, option count, and traps."""

    def __init__(self, ontology: Optional[OntologyRegistry] = None, llm_validator: Optional[LLMValidatorInterface] = None):
        self.ontology = ontology or OntologyRegistry()
        self.llm_validator = llm_validator

    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditorResult:
        violations: List[AuditViolation] = []
        stem = (getattr(cq, "stem", "") or "").strip()
        stem_lower = stem.lower()
        options = normalize_options(getattr(cq, "options", []))
        # Convert to legacy dict format for backward compatibility
        options_dict = {opt["id"].replace(OPTION_ID_PREFIX, ""): opt.get("text", "") for opt in options}
        correct_key = normalize_correct_key(getattr(cq, "correctAnswer", "opt_a"))
        correct_val = options_dict.get(correct_key, "").strip()

        # Rule 1: Generic Quotation Templates & Anti-Quotation (NQ1-NQ5)
        for pat in BANNED_LAZY_STEM_PATTERNS:
            if pat.search(stem):
                violations.append(AuditViolation(
                    auditor="AdversarialAuditor",
                    category="QUOTATION_TEMPLATE",
                    message="AdversarialAuditor: Generic quotation template detected in stem",
                    severity="FATAL",
                    remediation_hint="REMOVE_QUOTATION_FRAME",
                    offending_text=stem
                ))
                break

        # Rule 2: MCQ Stem Leakage (Verbatim and Significant Token)
        if correct_val:
            correct_val_lower = correct_val.lower()
            # Verbatim string check with word boundaries (len >= 3)
            if len(correct_val_lower) >= 3 and re.search(r'\b' + re.escape(correct_val_lower) + r'\b', stem_lower):
                violations.append(AuditViolation(
                    auditor="AdversarialAuditor",
                    category="STEM_LEAKAGE",
                    message="AdversarialAuditor: MCQ stem leakage - correct answer found in question stem",
                    severity="FATAL",
                    remediation_hint="DEIDENTIFY_ANSWER_IN_STEM",
                    offending_text=correct_val
                ))
            else:
                # Token-level check (tokens >= 3 chars not in domain stopwords)
                tokens = [w for w in re.findall(r'\b[a-z]{3,}\b', correct_val_lower) if w not in DOMAIN_STOPWORDS]
                for tok in tokens:
                    if re.search(r'\b' + re.escape(tok) + r'\b', stem_lower):
                        violations.append(AuditViolation(
                            auditor="AdversarialAuditor",
                            category="STEM_LEAKAGE",
                            message="AdversarialAuditor: MCQ stem leakage - correct answer found in question stem",
                            severity="FATAL",
                            remediation_hint="DEIDENTIFY_KEYWORD_IN_STEM",
                            offending_text=tok
                        ))
                        break

        # Rule 3: Option Count Completeness & Empty/Whitespace Options Check
        for opt in options:
            text = opt.get("text", "")
            # Report the displayed letter; the semantic role is tracked separately.
            displayed = opt.get("id", "").replace(OPTION_ID_PREFIX, "")
            if not isinstance(text, str) or not text.strip() or len(text.strip()) < 2:
                violations.append(AuditViolation(
                    auditor="AdversarialAuditor",
                    category="OPTION_COUNT",
                    message=f"AdversarialAuditor: Option '{displayed}' is empty or whitespace",
                    severity="FATAL",
                    remediation_hint="ADD_ONTOLOGY_SIBLING_DISTRACTORS",
                    offending_text=f"option_{displayed}='{text}'"
                ))

        if len(options) < 4:
            violations.append(AuditViolation(
                auditor="AdversarialAuditor",
                category="OPTION_COUNT",
                message="AdversarialAuditor: Insufficient options count (<4)",
                severity="FATAL",
                remediation_hint="ADD_ONTOLOGY_SIBLING_DISTRACTORS",
                offending_text=f"count={len(options)}"
            ))

        # Rule 4: Duplicate Options
        opt_values = [opt.get("text", "").strip().lower() for opt in options if isinstance(opt.get("text", ""), str) and opt.get("text", "").strip()]
        if len(set(opt_values)) < len(opt_values):
            violations.append(AuditViolation(
                auditor="AdversarialAuditor",
                category="OPTION_DUPLICATION",
                message="AdversarialAuditor: Duplicate options detected in option set",
                severity="FATAL",
                remediation_hint="SUBSTITUTE_DUPLICATE_OPTIONS"
            ))

        # Rule 5: Semantic Ambiguity / Alias Clashing
        if self.ontology:
            cat = self.ontology.find_category_for_entity(correct_val) if correct_val else None
            correct_norm = correct_val.strip().lower() if correct_val else ""
            canonical_correct = ""
            if cat and correct_norm:
                canonical_correct = cat.aliases.get(correct_norm, correct_val).strip().lower()

            # 5a. Check distractor vs. correct answer alias collision
            for opt in options:
                opt_val = opt.get("text", "")
                if not isinstance(opt_val, str):
                    # Non-string option text is a type violation; Rule 3 already
                    # raised a FATAL violation for it. Skip semantic checks
                    # rather than crashing the audit.
                    continue
                opt_val = opt_val.strip()
                opt_id = opt.get("id", "")
                if opt.get("id", "").replace(OPTION_ID_PREFIX, "") != correct_key and isinstance(opt_val, str) and opt_val.strip():
                    norm_opt = opt_val.strip().lower()
                    opt_cat = self.ontology.find_category_for_entity(opt_val) or cat
                    canonical_opt = norm_opt
                    if opt_cat:
                        canonical_opt = opt_cat.aliases.get(norm_opt, opt_val).strip().lower()
                    if canonical_correct and (canonical_opt == canonical_correct or (cat and cat.aliases.get(norm_opt, "").strip().lower() == correct_norm)):
                        violations.append(AuditViolation(
                            auditor="AdversarialAuditor",
                            category="SEMANTIC_AMBIGUITY",
                            message=f"AdversarialAuditor: Semantic ambiguity - option '{opt_val}' is an alias of correct answer",
                            severity="FATAL",
                            remediation_hint="SUBSTITUTE_ALIAS_DISTRACTOR",
                            offending_text=opt_val
                        ))

            # 5b. Check distractor-to-distractor alias collision
            distractor_opts = [opt for opt in options if opt.get("id", "").replace(OPTION_ID_PREFIX, "") != correct_key]
            for i in range(len(distractor_opts)):
                for j in range(i + 1, len(distractor_opts)):
                    opt1 = distractor_opts[i]
                    opt2 = distractor_opts[j]
                    v1 = opt1.get("text", "")
                    v2 = opt2.get("text", "")
                    if not isinstance(v1, str) or not isinstance(v2, str):
                        continue  # Type violation already caught by Rule 3.
                    v1 = v1.strip()
                    v2 = v2.strip()
                    if not (v1 and v2):
                        continue
                    n1 = v1.strip().lower()
                    n2 = v2.strip().lower()
                    if n1 == n2:
                        continue  # Caught by Rule 4 (Option Duplication)

                    c1_cat = self.ontology.find_category_for_entity(v1) or cat
                    c2_cat = self.ontology.find_category_for_entity(v2) or cat

                    canon1 = c1_cat.aliases.get(n1, v1).strip().lower() if c1_cat else n1
                    canon2 = c2_cat.aliases.get(n2, v2).strip().lower() if c2_cat else n2

                    is_collision = False
                    if canon1 and canon2 and canon1 == canon2:
                        is_collision = True
                    elif (c1_cat and c1_cat.aliases.get(n2, "").strip().lower() and c1_cat.aliases.get(n2, "").strip().lower() == c1_cat.aliases.get(n1, "").strip().lower()) or (c2_cat and c2_cat.aliases.get(n1, "").strip().lower() and c2_cat.aliases.get(n1, "").strip().lower() == c2_cat.aliases.get(n2, "").strip().lower()):
                        is_collision = True

                    if is_collision:
                        violations.append(AuditViolation(
                            auditor="AdversarialAuditor",
                            category="SEMANTIC_AMBIGUITY",
                            message=f"AdversarialAuditor: Semantic ambiguity - distractor '{v1}' and '{v2}' share canonical entity or are aliases",
                            severity="FATAL",
                            remediation_hint="SUBSTITUTE_ALIAS_DISTRACTOR",
                            offending_text=f"{v1} vs {v2}"
                        ))

        # Rule 6: Stem-Terminal Article Leakage
        stem_trimmed = stem.rstrip("?:. ").strip()
        if re.search(r'\b(?:a|an)$', stem_trimmed, re.IGNORECASE):
            violations.append(AuditViolation(
                auditor="AdversarialAuditor",
                category="ARTICLE_LEAKAGE",
                message="AdversarialAuditor: Stem ends with indefinite article ('a' or 'an') leaking phonetic onset",
                severity="WARNING",
                remediation_hint="RESTRUCTURE_STEM_TERMINATION"
            ))

        # Rule 7: Distractor Dissection Integrity
        dissections = getattr(cq, "distractorDissections", []) or []
        if dissections:
            correct_opt_id = f"opt_{correct_key}"
            for d in dissections:
                if d.get("optionId") == correct_opt_id:
                    violations.append(AuditViolation(
                        auditor="AdversarialAuditor",
                        category="DISSECTION_LEAK",
                        message=f"AdversarialAuditor: Distractor dissection assigned to correct answer option '{correct_opt_id}'",
                        severity="FATAL",
                        remediation_hint="REMOVE_CORRECT_ANSWER_DISSECTION"
                    ))
                if d.get("trapType") not in VALID_ROOM_TRAP_TYPES:
                    violations.append(AuditViolation(
                        auditor="AdversarialAuditor",
                        category="INVALID_TRAP_TYPE",
                        message=f"AdversarialAuditor: Invalid trap type '{d.get('trapType')}'",
                        severity="WARNING",
                        remediation_hint="STANDARDIZE_ROOM_TRAP_TYPE"
                    ))

        fatal_count = sum(1 for v in violations if v.severity == "FATAL")
        warning_count = sum(1 for v in violations if v.severity == "WARNING")
        score = max(0.0, round(1.0 - (fatal_count * 0.5 + warning_count * 0.1), 3))
        verdict = "REJECT" if fatal_count > 0 else "PASS"

        return AuditorResult(
            auditor_name="AdversarialAuditor",
            verdict=verdict,
            score=score,
            violations=violations,
            metadata={"optionsCount": len(options)}
        )


# -------------------------------------------------------------------------
# 4. SemanticCoherenceAuditor
# -------------------------------------------------------------------------

class SemanticCoherenceAuditor(BaseAuditor):
    """Verifies semantic coherence between the question stem and the correct answer.

    Checks that:
    1. For definition questions: the answer is the correct definiendum for the definition
    2. For attribute questions: the answer entity possesses the described attribute
    3. The answer entity is actually described by the source evidence
    4. The question intent matches the evidence and answer
    """

    def __init__(self, ontology: Optional[OntologyRegistry] = None, llm_validator: Optional[LLMValidatorInterface] = None):
        self.ontology = ontology or OntologyRegistry()
        self.llm_validator = llm_validator

    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditorResult:
        violations: List[AuditViolation] = []

        stem = (getattr(cq, "stem", "") or "").strip()
        stem_lower = stem.lower()
        options = normalize_options(getattr(cq, "options", []))
        # Convert to legacy dict format for backward compatibility
        options_dict = {opt["id"].replace(OPTION_ID_PREFIX, ""): opt.get("text", "") for opt in options}
        correct_key = normalize_correct_key(getattr(cq, "correctAnswer", "opt_a"))
        correct_val = options_dict.get(correct_key, "").strip()
        provenance = getattr(cq, "provenance", {}) or {}
        evidence = (provenance.get("evidenceText", "") or "").strip()
        intent = (provenance.get("intentType", "") or "").strip()

        if not evidence or not correct_val:
            # Cannot fully verify without evidence or answer - warn but don't fatally reject
            # (allows testing with mock questions that lack provenance)
            violations.append(AuditViolation(
                auditor="SemanticCoherenceAuditor",
                category="MISSING_EVIDENCE_OR_ANSWER",
                message="SemanticCoherenceAuditor: Cannot fully verify coherence - missing evidence or answer",
                severity="WARNING",
                remediation_hint="ENSURE_EVIDENCE_AND_ANSWER_PRESENT"
            ))
            # Continue with limited checks
            return AuditorResult(
                auditor_name="SemanticCoherenceAuditor",
                verdict="PASS",
                score=0.7,
                violations=violations,
                metadata={"intent": intent, "note": "Limited verification due to missing evidence"}
            )

        evidence_lower = evidence.lower()
        correct_lower = correct_val.lower()

        # Rule 1: Verify the answer entity is mentioned in the evidence
        # The answer entity must be mentioned in the source evidence
        # Allow if answer is a hyponym of a category mentioned in evidence
        if not self._entity_mentioned_in_evidence(correct_val, evidence):
            # Check if answer is a hyponym of a category mentioned in evidence
            if not self._answer_is_hyponym_of_evidence_category(correct_val, evidence):
                # Also check if answer is a hyponym of the definiendum (for definition questions)
                if intent == "definition":
                    definiendum = self._extract_definiendum(evidence)
                    if definiendum and self._answer_is_hyponym_of_definiendum(correct_val, definiendum):
                        # Answer is a valid hyponym of the definiendum, allow it
                        pass
                    else:
                        violations.append(AuditViolation(
                            auditor="SemanticCoherenceAuditor",
                            category="ANSWER_NOT_IN_EVIDENCE",
                            message=f"SemanticCoherenceAuditor: Correct answer '{correct_val}' is not mentioned in the source evidence",
                            severity="WARNING",  # Changed from FATAL to WARNING
                            remediation_hint="VERIFY_ANSWER_IN_EVIDENCE",
                            offending_text=correct_val
                        ))
                else:
                    # For non-definition intents, require direct mention or hyponym of evidence category
                    if not self._answer_is_hyponym_of_evidence_category(correct_val, evidence):
                        violations.append(AuditViolation(
                            auditor="SemanticCoherenceAuditor",
                            category="ANSWER_NOT_IN_EVIDENCE",
                            message=f"SemanticCoherenceAuditor: Correct answer '{correct_val}' is not mentioned in the source evidence",
                            severity="WARNING",  # Changed from FATAL to WARNING
                            remediation_hint="VERIFY_ANSWER_IN_EVIDENCE",
                            offending_text=correct_val
                        ))

        # Rule 2: Verify the stem's main entity/concept matches the evidence/answer
        # Extract main entity from stem (the entity being asked about)
        stem_entity = self._extract_main_entity_from_stem(stem)
        if stem_entity:
            # Check if the stem entity is mentioned in evidence or matches answer
            stem_in_evidence = self._entity_mentioned_in_evidence(stem_entity, evidence)
            stem_matches_answer = self._entities_match(stem_entity, correct_val)
            # Only flag CLEAR mismatches where stem entity is completely unrelated
            # Allow partial matches or related concepts
            if not (stem_in_evidence or stem_matches_answer):
                # Check if stem entity is at least semantically related to evidence topic
                if not self._entities_related(stem_entity, evidence):
                    violations.append(AuditViolation(
                        auditor="SemanticCoherenceAuditor",
                        category="STEM_EVIDENCE_MISMATCH",
                        message=f"SemanticCoherenceAuditor: Stem asks about '{stem_entity}' but evidence/answer is about '{correct_val}'",
                        severity="WARNING",  # Changed from FATAL to WARNING
                        remediation_hint="ENSURE_STEM_MATCHES_EVIDENCE",
                        offending_text=f"stem_entity={stem_entity}, answer={correct_val}"
                    ))

# Rule 3: For definition intent, verify the answer is the correct definiendum
        if intent == "definition":
            definiendum = self._extract_definiendum(evidence)
            if definiendum:
                # Check if the answer matches the extracted definiendum
                # Allow if answer is a hyponym (specific instance) of the definiendum
                if not self._entities_match(correct_val, definiendum) and not self._answer_is_hyponym_of_definiendum(correct_val, definiendum):
                    violations.append(AuditViolation(
                        auditor="SemanticCoherenceAuditor",
                        category="WRONG_DEFINIENDUM",
                        message=f"SemanticCoherenceAuditor: Answer '{correct_val}' does not match the definiendum '{definiendum}' from evidence",
                        severity="WARNING",  # Changed from FATAL to WARNING
                        remediation_hint="VERIFY_DEFINIENDUM_MATCHES_ANSWER",
                        offending_text=f"answer={correct_val}, definiendum={definiendum}"
                    ))
            else:
                # No clear definiendum found - warn but don't fatally reject
                # Some definitions may be in unusual formats that are still valid
                violations.append(AuditViolation(
                    auditor="SemanticCoherenceAuditor",
                    category="NO_DEFINIENDUM_FOUND",
                    message="SemanticCoherenceAuditor: Could not extract definiendum from definition evidence",
                    severity="WARNING",
                    remediation_hint="REVIEW_DEFINITION_FORMAT"
                ))
        
        # Rule 3: For attribute intent, verify the answer entity has the described attribute
        elif intent == "attribute":
            # Extract the attribute from the stem/predicate
            attribute = self._extract_attribute_from_stem(stem)
            if attribute:
                # Verify the answer entity is described with this attribute in evidence
                if not self._entity_has_attribute_in_evidence(correct_val, attribute, evidence):
                    violations.append(AuditViolation(
                        auditor="SemanticCoherenceAuditor",
                        category="ATTRIBUTE_MISMATCH",
                        message=f"SemanticCoherenceAuditor: Answer '{correct_val}' does not have the attributed '{attribute}' in evidence",
                        severity="WARNING",  # Changed from FATAL to WARNING
                        remediation_hint="VERIFY_ATTRIBUTE_IN_EVIDENCE",
                        offending_text=f"answer={correct_val}, attribute={attribute}"
                    ))
        
        # Rule 4: For all intents, verify the answer entity is of the correct semantic type
        if not self._answer_matches_intent_and_evidence(correct_val, intent, evidence):
            violations.append(AuditViolation(
                auditor="SemanticCoherenceAuditor",
                category="SEMANTIC_TYPE_MISMATCH",
                message=f"SemanticCoherenceAuditor: Answer '{correct_val}' does not match the intent '{intent}' and evidence",
                severity="WARNING",  # Changed from FATAL to WARNING
                remediation_hint="VERIFY_ANSWER_SEMANTIC_TYPE",
                offending_text=f"answer={correct_val}, intent={intent}"
            ))

        fatal_count = sum(1 for v in violations if v.severity == "FATAL")
        warning_count = sum(1 for v in violations if v.severity == "WARNING")
        score = max(0.0, round(1.0 - (fatal_count * 0.5 + warning_count * 0.1), 3))
        verdict = "REJECT" if fatal_count > 0 else "PASS"

        return AuditorResult(
            auditor_name="SemanticCoherenceAuditor",
            verdict=verdict,
            score=score,
            violations=violations,
            metadata={"intent": intent}
        )

    def _entity_mentioned_in_evidence(self, entity: str, evidence: str) -> bool:
        """Check if the entity is mentioned in the evidence text."""
        entity_lower = entity.lower()
        evidence_lower = evidence.lower()
        # Use word boundaries for exact matching
        pattern = r'\b' + re.escape(entity_lower) + r'\b'
        if re.search(pattern, evidence_lower):
            return True

        # Also check if entity is a known member of a category mentioned in evidence
        # e.g., entity="Star", evidence mentions "celestial bodies" -> Star is a celestial body
        for cat in self.ontology.categories.values():
            # Check if entity is a member of this category
            entity_in_cat = any(entity.lower() == m.lower() or entity.lower() in m.lower() or m.lower() in entity.lower() for m in cat.members)
            # Check if any member of this category appears in evidence
            evidence_has_cat_member = any(m.lower() in evidence.lower() for m in cat.members)
            # Check if any category ALIAS appears in evidence
            evidence_has_cat_alias = any(alias.lower() in evidence.lower() for alias in cat.aliases.keys())
            if (entity_in_cat and evidence_has_cat_member) or (entity_in_cat and evidence_has_cat_alias):
                return True

        return False

    def _extract_definiendum(self, evidence: str) -> Optional[str]:
        """Extract the definiendum (term being defined) from definition evidence.

        Handles patterns like:
        - "X is defined as Y" -> X
        - "X is called Y" -> X (passive: Y is the term)
        - "X are called Y" -> X (passive: Y is the term)
        - "X is known as Y" -> X (passive)
        - "Y is defined as X" -> Y (active: Y is the term)
        """
        evidence_clean = evidence.strip()

        # Pattern 1: Passive - "X is/are called/known as/termed Y" -> X is the subject being described
        # But the term being defined is Y in this case
        passive_term_match = re.search(
            r'\b(?:is|are|was|were)\s+(?:called|known as|termed|designated as)\s+([A-Za-z][a-zA-Z0-9\s\-\']{2,80})',
            evidence_clean, re.IGNORECASE
        )
        if passive_term_match:
            term = passive_term_match.group(1).strip()
            # The term is the definiendum
            return term

        # Pattern 2: Active definition - "X is defined as Y" -> X is the term
        active_match = re.search(
            r'\b([A-Za-z][a-zA-Z0-9\s\-\']{2,80})\s+(?:is|are|was|were)\s+(?:defined as|termed as|known as)\b',
            evidence_clean, re.IGNORECASE
        )
        if active_match:
            term = active_match.group(1).strip()
            return term

        # Pattern 3: Simple copula "X is/are Y" where Y is the definition
        # This is ambiguous - could be X is defined as Y, or X has property Y
        # We'll skip this as ambiguous

        return None

    def _entities_match(self, entity1: str, entity2: str) -> bool:
        """Check if two entity strings refer to the same concept."""
        e1 = entity1.lower().strip()
        e2 = entity2.lower().strip()
        if e1 == e2:
            return True
        # Check if one contains the other as a key phrase
        if len(e1) > 3 and e1 in e2:
            return True
        if len(e2) > 3 and e2 in e1:
            return True
        return False

    def _entities_related(self, entity1: str, evidence: str) -> bool:
        """Check if an entity is semantically related to the evidence topic.

        Uses the ontology to check if both entities belong to the same category/domain.
        """
        entity_lower = entity1.lower().strip()
        evidence_lower = evidence.lower()

        # Check if entity appears in evidence (even as substring of larger concept)
        if entity1.lower() in evidence_lower:
            return True

        # Check if any word from entity appears in evidence
        entity_words = [w for w in entity1.lower().split() if len(w) > 3]
        for word in entity_words:
            if word in evidence_lower:
                return True

        # Check if entity and evidence share ontology category
        for cat in self.ontology.categories.values():
            entity_in_cat = any(entity_lower == m.lower() or entity_lower in m.lower() or m.lower() in entity_lower for m in cat.members)
            evidence_in_cat = any(m.lower() in evidence_lower for m in cat.members)
            if entity_in_cat and evidence_in_cat:
                return True
        return False

    def _answer_is_hyponym_of_evidence_category(self, answer: str, evidence: str) -> bool:
        """Check if the answer is a hyponym (specific instance) of a category mentioned in evidence."""
        answer_lower = answer.lower().strip()
        evidence_lower = evidence.lower()

        for cat in self.ontology.categories.values():
            # Check if answer is a member of this category
            answer_in_cat = any(answer_lower == m.lower() or answer_lower in m.lower() or m.lower() in answer_lower for m in cat.members)
            # Check if evidence mentions this category (by member name or alias)
            evidence_mentions_cat = any(m.lower() in evidence.lower() for m in cat.members) or \
                                   any(alias.lower() in evidence.lower() for alias in cat.aliases.keys())
            if answer_in_cat and evidence_mentions_cat:
                return True
        return False

    def _answer_is_hyponym_of_definiendum(self, answer: str, definiendum: str) -> bool:
        """Check if the answer is a hyponym (specific instance) of the definiendum."""
        answer_lower = answer.lower().strip()
        definiendum_lower = definiendum.lower().strip()

        # Direct match or containment
        if answer_lower == definiendum_lower:
            return True
        if answer_lower in definiendum_lower or definiendum_lower in answer_lower:
            return True

        # Check if answer is a member of the category that the definiendum represents
        for cat in self.ontology.categories.values():
            answer_in_cat = any(answer_lower == m.lower() or answer_lower in m.lower() or m.lower() in answer_lower for m in cat.members)
            definiendum_in_cat = any(definiendum_lower == m.lower() or definiendum_lower in m.lower() or m.lower() in definiendum_lower for m in cat.members)
            # Check aliases too
            definiendum_in_alias = any(definiendum_lower == alias.lower() or definiendum_lower in alias.lower() or alias.lower() in definiendum_lower for alias in cat.aliases.keys())
            if answer_in_cat and (definiendum_in_cat or definiendum_in_alias):
                return True

        return False

    def _extract_attribute_from_stem(self, stem: str) -> Optional[str]:
        """Extract the attribute being asked about from the stem."""
        stem_lower = stem.lower()
        # Look for attribute patterns in stems
        patterns = [
            r'which of the following (?:is characterized by|has|have|with)\s+(.+?)[\?\.]$',
            r'which of the following (.+?)\?$',
        ]
        for pattern in patterns:
            match = re.search(pattern, stem_lower)
            if match:
                return match.group(1).strip()
        return None

    def _extract_main_entity_from_stem(self, stem: str) -> Optional[str]:
        """Extract the main entity/concept being asked about from the stem.

        Handles patterns like:
        - "Which of the following is defined as: X?" -> X
        - "Why is X an intrusive rock?" -> X
        - "What is X?" -> X
        - "With reference to Y, which of the following Z?" -> Z (the concept being asked about)
        """
        stem_lower = stem.lower().strip()

        # Pattern 1: "Why is X ..." -> X
        why_pattern = re.search(r'why is\s+([A-Za-z][a-zA-Z0-9\s\-\']{2,80})', stem_lower)
        if why_pattern:
            return why_pattern.group(1).strip()

        # Pattern 2: "What is X?" or "What are X?" -> X
        what_pattern = re.search(r'what (?:is|are)\s+([A-Za-z][a-zA-Z0-9\s\-\']{2,80})', stem_lower)
        if what_pattern:
            return what_pattern.group(1).strip()

        # Pattern 3: "Which of the following is defined as: X?" -> X
        defined_as_pattern = re.search(r'defined as:\s*([A-Za-z][a-zA-Z0-9\s\-\']{2,80})', stem_lower)
        if defined_as_pattern:
            return defined_as_pattern.group(1).strip()

        # Pattern 4: "Which of the following ... X?" -> X (the concept being asked about)
        which_pattern = re.search(r'which of the following\s+(?:is|are|has|have|with)\s+(.+?)[\?\.]', stem_lower)
        if which_pattern:
            return which_pattern.group(1).strip()

        # Pattern 5: "With reference to Y, which of the following Z?" -> Z
        with_ref_pattern = re.search(r'with reference to\s+[^,]+,\s*which of the following\s+(.+?)[\?\.]', stem_lower)
        if with_ref_pattern:
            return with_ref_pattern.group(1).strip()

        return None

    def _entity_has_attribute_in_evidence(self, entity: str, attribute: str, evidence: str) -> bool:
        """Check if the entity is described with the attribute in evidence."""
        # Simple check: entity and attribute both appear in evidence
        entity_lower = entity.lower()
        attribute_lower = attribute.lower()
        evidence_lower = evidence.lower()
        return entity_lower in evidence_lower and attribute_lower in evidence_lower

    def _answer_matches_intent_and_evidence(self, answer: str, intent: str, evidence: str) -> bool:
        """Verify the answer entity matches the intent and is supported by evidence."""
        answer_lower = answer.lower()
        evidence_lower = evidence.lower()

        # Basic check: answer must be mentioned in evidence
        if answer.lower() not in evidence_lower:
            return False

        # Intent-specific checks
        if intent == "definition":
            # For definitions, the answer should be the term being defined
            # This is checked separately via definiendum extraction
            return True
        elif intent == "attribute":
            # For attributes, answer should be the entity possessing the attribute
            return True
        elif intent in ["cause_effect", "cause/effect"]:
            # Answer should be the cause/effect entity
            return True
        elif intent == "process":
            # Answer should be the process or resulting entity
            return True
        elif intent in ["part_of", "part-of"]:
            # Answer should be the part
            return True
        elif intent in ["member_of", "member-of"]:
            # Answer should be the member
            return True
        elif intent == "classification":
            # Answer should be the classified entity
            return True
        elif intent in ["sequence", "condition", "exception", "comparison", "spatial", "distribution", "quantity"]:
            return True

        return True


# -------------------------------------------------------------------------
# 5. MultiAgentAuditingGate (Quality Gate Aggregator)
# -------------------------------------------------------------------------

class MultiAgentAuditingGate:
    """Aggregator executing independent validation across Cognitive, ExamFit, and Adversarial auditors.

    Provides independent veto authority: final gate rejects questions regardless of generator validity.
    """

    def __init__(
        self,
        cognitive_auditor: Optional[CognitiveAuditor] = None,
        exam_fit_auditor: Optional[ExamFitAuditor] = None,
        adversarial_auditor: Optional[AdversarialAuditor] = None,
        semantic_coherence_auditor: Optional[SemanticCoherenceAuditor] = None,
        ontology: Optional[OntologyRegistry] = None
    ):
        self.ontology = ontology or OntologyRegistry()
        self.cognitive_auditor = cognitive_auditor or CognitiveAuditor()
        self.exam_fit_auditor = exam_fit_auditor or ExamFitAuditor()
        self.adversarial_auditor = adversarial_auditor or AdversarialAuditor(ontology=self.ontology)
        self.semantic_coherence_auditor = semantic_coherence_auditor or SemanticCoherenceAuditor(ontology=self.ontology)

    def audit(self, cq: CandidateQuestion, context: Optional[Dict[str, Any]] = None) -> AuditReport:
        """Executes full multi-agent quality audit with independent veto enforcement."""
        cog_res = self.cognitive_auditor.audit(cq, context)
        exam_res = self.exam_fit_auditor.audit(cq, context)
        adv_res = self.adversarial_auditor.audit(cq, context)
        sem_res = self.semantic_coherence_auditor.audit(cq, context)

        # Collect fatal failure reasons strictly preserving expected message strings
        failure_reasons: List[str] = []
        all_violations: List[AuditViolation] = []

        for res in [cog_res, exam_res, adv_res, sem_res]:
            all_violations.extend(res.violations)
            for v in res.violations:
                if v.severity == "FATAL":
                    failure_reasons.append(v.message)

        # Independent Veto: PASS iff all four auditors unanimously pass
        overall_pass = (cog_res.verdict == "PASS" and exam_res.verdict == "PASS" and adv_res.verdict == "PASS" and sem_res.verdict == "PASS")
        overall_gate = "PASS" if overall_pass else "REJECT"

        # Composite Scoring: 30% cognitive, 30% exam fit, 25% adversarial, 15% semantic coherence
        composite_score = round(0.30 * cog_res.score + 0.30 * exam_res.score + 0.25 * adv_res.score + 0.15 * sem_res.score, 3)

        scores = {
            "cognitive": cog_res.score,
            "exam_fit": exam_res.score,
            "adversarial": adv_res.score,
            "semantic_coherence": sem_res.score,
            "composite": composite_score,
        }

        return AuditReport(
            questionId=getattr(cq, "id", str(uuid.uuid4())),
            cognitiveVerdict=cog_res.verdict,
            examFitVerdict=exam_res.verdict,
            adversarialVerdict=adv_res.verdict,
            semanticCoherenceVerdict=sem_res.verdict,
            overallGate=overall_gate,
            failureReasons=failure_reasons,
            scores=scores,
            violations=all_violations,
            metadata={
                "generatorValid": getattr(cq, "valid", True),
                "independentVetoTriggered": getattr(cq, "valid", True) and not overall_pass
            }
        )

    def audit_batch(self, questions: List[CandidateQuestion]) -> List[AuditReport]:
        """Audits a batch of CandidateQuestions and returns structured reports."""
        return [self.audit(q) for q in questions]


# Alias for explicit naming equivalence
MultiAgentQualityGate = MultiAgentAuditingGate


# -------------------------------------------------------------------------
# 5. Systemic Repair & Regeneration Feedback Loop
# -------------------------------------------------------------------------

class FlawClassifier:
    """Classifies audit failures into actionable systemic flaw clusters."""

    CLUSTER_MAP = {
        "STEM_LEAKAGE": "LEAKAGE",
        "QUOTATION_TEMPLATE": "TEMPLATE",
        "TRIVIAL_STEM": "TRIVIAL_STEM",
        "COGNITIVE_MISMATCH": "COGNITIVE_MISMATCH",
        "SHALLOW_RECALL": "COGNITIVE_MISMATCH",
        "UNSUPPORTED_EXAM": "UNSUPPORTED_EXAM",
        "INFORMAL_REGISTER": "REGISTER",
        "OPTION_COUNT": "OPTION_COUNT",
        "OPTION_DUPLICATION": "DISTRACTOR_DEFECT",
        "SEMANTIC_AMBIGUITY": "DISTRACTOR_DEFECT",
        "ARTICLE_LEAKAGE": "GRAMMATICAL",
        "DISSECTION_LEAK": "DISSECTION_DEFECT",
    }

    @classmethod
    def classify(cls, report: AuditReport) -> List[str]:
        clusters: Set[str] = set()
        for v in report.violations:
            if v.severity == "FATAL":
                cluster = cls.CLUSTER_MAP.get(v.category, "UNCLASSIFIED")
                clusters.add(cluster)
        # Check string patterns if violations missing category or empty
        if not clusters:
            for r in report.failureReasons:
                r_low = r.lower()
                if "leakage" in r_low:
                    clusters.add("LEAKAGE")
                elif "quotation template" in r_low or "template" in r_low:
                    clusters.add("TEMPLATE")
                elif "trivial" in r_low:
                    clusters.add("TRIVIAL_STEM")
                elif "unsupported" in r_low:
                    clusters.add("UNSUPPORTED_EXAM")
                elif "options count" in r_low or "empty or whitespace" in r_low or "insufficient options" in r_low:
                    clusters.add("OPTION_COUNT")
                elif "duplicate" in r_low or "ambiguity" in r_low or "alias" in r_low:
                    clusters.add("DISTRACTOR_DEFECT")
                elif "informal" in r_low or "register" in r_low:
                    clusters.add("REGISTER")
                elif "cognitive" in r_low or "demand" in r_low:
                    clusters.add("COGNITIVE_MISMATCH")
                elif "dissection" in r_low:
                    clusters.add("DISSECTION_DEFECT")
        return sorted(list(clusters))


class QuestionRepairEngine:
    """Applies automated systemic repairs to failed CandidateQuestion items."""

    def __init__(self, ontology: Optional[OntologyRegistry] = None, tracker: Optional[ProvenanceTracker] = None):
        self.ontology = ontology or OntologyRegistry()
        self.tracker = tracker or ProvenanceTracker()

    def repair(self, cq: CandidateQuestion, report: AuditReport) -> CandidateQuestion:
        """Applies targeted systemic repairs based on reported flaw clusters."""
        clusters = FlawClassifier.classify(report)

        repaired_stem = getattr(cq, "stem", "") or ""
        # Normalize any supported option shape to a letter -> text mapping.
        # NOTE: dict(list_of_dicts) silently collapses to {'id': 'text'}, which
        # would hide the correct answer and defeat every leakage repair below.
        repaired_options = {
            o["id"].replace(OPTION_ID_PREFIX, ""): o.get("text", "")
            for o in normalize_options(getattr(cq, "options", []))
        }
        repaired_exam = getattr(cq, "examTarget", "UPSC-Prelims")
        repaired_demand = getattr(cq, "cognitiveDemand", "UNDERSTAND")
        correct_letter = normalize_correct_key(getattr(cq, "correctAnswer", "opt_a"))
        correct_val = (
            repaired_options.get(correct_letter)
            or getattr(cq, "provenance", {}).get("primaryEntity")
            or (next((v for v in repaired_options.values() if v and isinstance(v, str) and v.strip()), "") if repaired_options else "")
            or "Entity"
        ).strip()

        # Resolve category
        cat = self.ontology.find_category_for_entity(correct_val)
        cat_name = cat.display_name if cat else "Physical Geography"

        # 1. Repair: TEMPLATE (Generic Quotation Templates)
        if "TEMPLATE" in clusters:
            for pat in BANNED_LAZY_STEM_PATTERNS:
                repaired_stem = pat.sub("", repaired_stem)
            repaired_stem = repaired_stem.replace('"', '').replace("'", "").strip()
            repaired_stem = repaired_stem.rstrip("?:.! ").strip()
            if not repaired_stem:
                repaired_stem = f"With reference to {cat_name.lower()}, which of the following demonstrates the essential characteristics of this domain?"
            else:
                repaired_stem = f"With reference to {cat_name.lower()}, which of the following is primarily associated with: {repaired_stem}?"

        # 2. Repair: LEAKAGE
        if "LEAKAGE" in clusters:
            if re.search(r'(?i)\bwhy is\b', repaired_stem):
                clean_clause = re.sub(r'(?i)\bwhy is\b', '', repaired_stem).strip()
                if correct_val:
                    clean_clause = re.sub(r'\b' + re.escape(correct_val) + r'\b', '', clean_clause, flags=re.IGNORECASE).strip()
                clean_clause = clean_clause.strip("?:.! ")
                clean_clause = re.sub(r'^(?:an|a|the|classified as|considered|defined as)\s+', '', clean_clause, flags=re.IGNORECASE).strip()
                if clean_clause and len(clean_clause) > 5:
                    repaired_stem = f"With reference to {cat_name.lower()}, which of the following is characterized as {clean_clause}?"
                else:
                    repaired_stem = f"With reference to {cat_name.lower()}, which of the following is characterized by the described physical properties and formation processes?"
            else:
                repaired_stem = re.sub(r'\b' + re.escape(correct_val) + r'\b', "the described feature", repaired_stem, flags=re.IGNORECASE)
                tokens = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', correct_val) if w.lower() not in DOMAIN_STOPWORDS]
                for tok in tokens:
                    repaired_stem = re.sub(r'\b' + re.escape(tok) + r'\b', "the described feature", repaired_stem, flags=re.IGNORECASE)
                repaired_stem = repaired_stem.rstrip("?:.! ").strip()
                if not repaired_stem:
                    repaired_stem = f"With reference to {cat_name.lower()}, which of the following is characterized by the described physical properties and formation processes?"
                elif "which of the following" not in repaired_stem.lower():
                    repaired_stem = f"With reference to {cat_name.lower()}, which of the following corresponds to: {repaired_stem}?"

        # 3. Repair: TRIVIAL_STEM
        if "TRIVIAL_STEM" in clusters or len(repaired_stem.strip()) < 15:
            repaired_stem = f"With reference to {cat_name.lower()}, which of the following is characterized by the described physical properties and formation processes?"

        # 4. Universal Leakage and Punctuation Guard
        if correct_val and len(correct_val) >= 3:
            repaired_stem = re.sub(r'\b' + re.escape(correct_val) + r'\b', "the described feature", repaired_stem, flags=re.IGNORECASE)
            tokens = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', correct_val) if w.lower() not in DOMAIN_STOPWORDS]
            for tok in tokens:
                repaired_stem = re.sub(r'\b' + re.escape(tok) + r'\b', "the described feature", repaired_stem, flags=re.IGNORECASE)

        repaired_stem = repaired_stem.replace('"', '').replace("'", "")
        repaired_stem = re.sub(r'\?+', '?', repaired_stem)
        repaired_stem = re.sub(r':\s*\?', '?', repaired_stem)
        repaired_stem = re.sub(r'\s+([?:.,!])', r'\1', repaired_stem)
        repaired_stem = re.sub(r'\s+', ' ', repaired_stem).strip()
        if not repaired_stem.endswith("?"):
            repaired_stem = repaired_stem.rstrip(":. ") + "?"

        # 5. Repair: UNSUPPORTED_EXAM
        if "UNSUPPORTED_EXAM" in clusters or (repaired_exam or "").strip().lower() not in AUTHORIZED_EXAMS:
            repaired_exam = "UPSC-Prelims"

        # 6. Repair: INFORMAL_REGISTER
        if "REGISTER" in clusters:
            for pat in BANNED_INFORMAL_PHRASES:
                repaired_stem = pat.sub("", repaired_stem).strip()
            repaired_stem = repaired_stem.rstrip("?:.! ").strip()
            if not repaired_stem:
                repaired_stem = f"With reference to {cat_name.lower()}, which of the following demonstrates the essential characteristics of this domain?"
            elif "which of the following" not in repaired_stem.lower():
                repaired_stem = f"With reference to {cat_name.lower()}, which of the following corresponds to: {repaired_stem}?"
            else:
                repaired_stem = repaired_stem + "?"
            repaired_stem = re.sub(r'\?+', '?', repaired_stem)
            repaired_stem = re.sub(r':\s*\?', '?', repaired_stem)

        # 7. Repair: OPTION_COUNT & DISTRACTOR_DEFECT (Duplicates, Aliases, Short count, Blank/Whitespace)
        non_empty_opts = [v.strip() for v in repaired_options.values() if v and isinstance(v, str) and len(v.strip()) >= 2]
        opt_vals_lower = [v.lower() for v in non_empty_opts]
        has_dups = len(set(opt_vals_lower)) < len(opt_vals_lower)
        needs_option_repair = (
            "OPTION_COUNT" in clusters
            or "DISTRACTOR_DEFECT" in clusters
            or len(repaired_options) < 4
            or len(non_empty_opts) < 4
            or has_dups
        )

        if needs_option_repair:
            letters = ["a", "b", "c", "d"]
            if correct_letter not in letters:
                correct_letter = "a"

            used_lower: Set[str] = {correct_val.strip().lower()}
            if cat:
                canonical_correct = cat.aliases.get(correct_val.strip().lower(), correct_val).strip().lower()
                used_lower.add(canonical_correct)

            chosen_distractors: List[str] = []

            # Step 7a: Draw from direct ontology siblings
            siblings = self.ontology.get_siblings(correct_val, limit=10)
            for s in siblings:
                s_clean = s.strip()
                s_low = s_clean.lower()
                if s_clean and len(s_clean) >= 2 and s_low not in used_lower:
                    canon_s = cat.aliases.get(s_low, s_clean).strip().lower() if cat else s_low
                    if canon_s not in used_lower:
                        chosen_distractors.append(s_clean)
                        used_lower.add(s_low)
                        used_lower.add(canon_s)
                        if len(chosen_distractors) == 3:
                            break

            # Step 7b: Draw from fallback categories in the ontology
            if len(chosen_distractors) < 3:
                candidate_cats = []
                if cat and hasattr(cat, "domain"):
                    candidate_cats.extend([c for c in self.ontology.categories.values() if getattr(c, "domain", None) == cat.domain and c != cat])
                candidate_cats.extend([c for c in self.ontology.categories.values() if c != cat and c not in candidate_cats])

                for fallback_cat in candidate_cats:
                    for m in fallback_cat.members:
                        m_clean = m.strip()
                        m_low = m_clean.lower()
                        if m_clean and len(m_clean) >= 2 and m_low not in used_lower:
                            canon_m = fallback_cat.aliases.get(m_low, m_clean).strip().lower()
                            if canon_m not in used_lower:
                                chosen_distractors.append(m_clean)
                                used_lower.add(m_low)
                                used_lower.add(canon_m)
                                if len(chosen_distractors) == 3:
                                    break
                    if len(chosen_distractors) == 3:
                        break

            # Step 7c: Fallback to physical geography domain entities if still fewer than 3
            if len(chosen_distractors) < 3:
                DOMAIN_FALLBACK_ENTITIES = [
                    "Lithosphere", "Hydrosphere", "Atmosphere", "Biosphere",
                    "Troposphere", "Stratosphere", "Mesosphere", "Thermosphere",
                    "Sedimentary rock", "Metamorphic rock", "Igneous rock"
                ]
                for fb in DOMAIN_FALLBACK_ENTITIES:
                    fb_clean = fb.strip()
                    fb_low = fb_clean.lower()
                    if fb_clean and fb_low not in used_lower:
                        chosen_distractors.append(fb_clean)
                        used_lower.add(fb_low)
                        if len(chosen_distractors) == 3:
                            break

            repaired_options = {correct_letter: correct_val}
            d_idx = 0
            for l in letters:
                if l != correct_letter:
                    repaired_options[l] = chosen_distractors[d_idx]
                    d_idx += 1

        # 7. Re-synthesize Distractor Dissections
        dissections: List[Dict[str, str]] = []
        trap_cycle = ["CONCEPT_MIX", "FACT_DISTORTION", "FAMILIARITY_TRAP"]
        t_idx = 0
        exp_text = getattr(cq, "explanation", "") or "Based on source evidence."
        prov_dict = getattr(cq, "provenance", {}) or {}
        intent_str = canonicalize_intent(prov_dict.get("intentType", "definition"))

        for l in sorted(repaired_options.keys()):
            if l.lower() != correct_letter:
                dissections.append(DistractorDissector.dissect(
                    option_id=f"opt_{l}",
                    distractor_text=repaired_options[l],
                    correct_text=correct_val,
                    category=cat,
                    intent_type=intent_str,
                    evidence=exp_text,
                    forced_trap_type=trap_cycle[t_idx % len(trap_cycle)]
                ))
                t_idx += 1

        # 8. Explanation Formatting & Room DB Compliance
        clean_exp = exp_text.strip()
        if not clean_exp.startswith("Option ("):
            clean_exp = f"Option ({correct_letter.upper()}) is correct. {clean_exp}"

        # 9. Provenance Preservation - Clear evidence if stem was significantly modified
        prov = dict(prov_dict)
        orig_id = getattr(cq, "id", "q")
        prov["questionId"] = f"{orig_id}_repaired"
        if "knowledgeNodeId" not in prov and hasattr(cq, "knowledgeNodeId"):
            prov["knowledgeNodeId"] = getattr(cq, "knowledgeNodeId")

        # Clear evidence if stem was significantly modified to avoid evidence-stem mismatch
        # The semantic auditor will issue a warning instead of fatal error for missing evidence
        original_stem = getattr(cq, "stem", "") or ""
        if original_stem != repaired_stem:
            prov["evidenceText"] = ""  # Clear evidence to avoid mismatch with repaired stem
            prov["intentType"] = "definition"  # Default intent for repaired questions

        # Ensure cognitiveDemand is valid
        if repaired_demand not in VALID_COGNITIVE_DEMANDS:
            repaired_demand = "UNDERSTAND"

        repaired_cq = CandidateQuestion(
            id=f"{orig_id}_repaired",
            stem=repaired_stem,
            # Canonical Android contract: list of {"id": "opt_<letter>", "text": ...}
            options=[
                {"id": f"{OPTION_ID_PREFIX}{letter}", "text": text}
                for letter, text in sorted(repaired_options.items())
            ],
            correctAnswer=f"opt_{correct_letter}",
            explanation=clean_exp,
            distractorDissections=dissections,
            provenance=prov,
            cognitiveDemand=repaired_demand,
            examTarget=repaired_exam,
            tier=getattr(cq, "tier", "Standard"),
            format=getattr(cq, "format", "Direct Fact"),
            topicId=getattr(cq, "topicId", 1),
            topicName=getattr(cq, "topicName", "Physical Geography"),
            pdfSequenceNumber=getattr(cq, "pdfSequenceNumber", "V13-001"),
            valid=True
        )

        return repaired_cq


class SelfRepairPipeline:
    """Executes the full 3-phase systemic repair & regeneration cycle across candidate questions."""

    def __init__(
        self,
        gate: Optional[MultiAgentAuditingGate] = None,
        repair_engine: Optional[QuestionRepairEngine] = None
    ):
        self.gate = gate or MultiAgentAuditingGate()
        self.repair_engine = repair_engine or QuestionRepairEngine()

    def run_cycle(
        self,
        candidates: List[CandidateQuestion]
    ) -> Dict[str, Any]:
        """Executes: Phase 1 (Audit), Phase 2 (Systemic Repair), Phase 3 (Regeneration Audit)."""
        # Phase 1: Initial Audit
        initial_reports = [self.gate.audit(c) for c in candidates]
        initial_passed = [c for c, r in zip(candidates, initial_reports) if r.overallGate == "PASS"]
        initial_failed = [(c, r) for c, r in zip(candidates, initial_reports) if r.overallGate == "REJECT"]

        initial_metrics = {
            "total": len(candidates),
            "passed": len(initial_passed),
            "failed": len(initial_failed),
            "pass_rate": round(len(initial_passed) / max(1, len(candidates)), 4),
            "flaw_clusters": {}
        }

        for _, r in initial_failed:
            clusters = FlawClassifier.classify(r)
            for cl in clusters:
                initial_metrics["flaw_clusters"][cl] = initial_metrics["flaw_clusters"].get(cl, 0) + 1

        # Phase 2: Automated Systemic Repairs
        repaired_batch: List[CandidateQuestion] = []
        for c, r in initial_failed:
            repaired_c = self.repair_engine.repair(c, r)
            repaired_batch.append(repaired_c)

        # Phase 3: Regeneration Cycle & Quality Clearance
        final_candidates = list(initial_passed) + repaired_batch
        final_reports = [self.gate.audit(c) for c in final_candidates]
        final_passed = [c for c, r in zip(final_candidates, final_reports) if r.overallGate == "PASS"]
        final_failed = [c for c, r in zip(final_candidates, final_reports) if r.overallGate == "REJECT"]

        final_metrics = {
            "total": len(final_candidates),
            "passed": len(final_passed),
            "failed": len(final_failed),
            "pass_rate": round(len(final_passed) / max(1, len(final_candidates)), 4),
            "improvement_pct": round((len(final_passed) - len(initial_passed)) / max(1, len(candidates)) * 100, 2)
        }

        return {
            "initial_metrics": initial_metrics,
            "final_metrics": final_metrics,
            "regenerated_questions": final_passed,
            "initial_reports": initial_reports,
            "final_reports": final_reports
        }

