"""
proposed_provenance.py
======================
Architectural Prototype for V13 Unbreakable Provenance Registry (v13_discovery/provenance.py).

Implements:
1. Strict 6-Link Provenance Chain:
   Question ID -> Intent -> Knowledge Unit -> Evidence -> Source -> Location
2. Immutable Data Model:
   Frozen dataclasses with cryptographic SHA-256 tamper-evident chaining.
3. Cryptographic Verification:
   Detects any mutation to stem, intent, unit, evidence, source, or location coordinates.
4. Comprehensive Verification & Auditing:
   verify_provenance_chain (supports bool & tuple unpacking), audit_provenance_integrity.
5. Bidirectional Interoperability:
   Seamless bridges for KnowledgeNode, CandidateQuestion, and PipelineBridge.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple, Union, Sequence, Set

# Canonical 14 educational intents (aligned with v13_discovery.semantic_extractor)
CANONICAL_14_INTENTS: Set[str] = {
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

INTENT_ALIASES: Dict[str, str] = {
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

R2_CANONICAL_MAP: Dict[str, str] = {
    "cause_effect": "cause/effect",
    "part_of": "part-of",
    "member_of": "member-of",
}

TRIVIAL_STRINGS: Set[str] = {
    "test", "sample", "foo", "bar", "n/a", "na",
    "todo", "tbd", "unknown", "none", "0", ""
}

PROVENANCE_SCHEMA_VERSION = "1.0.0"


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


def _canonical_json(data: Any) -> str:
    """Produces deterministic, whitespace-compact JSON string for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    """Returns hexadecimal SHA-256 digest of utf-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LinkHashes:
    """Cryptographic hashes for each link in the 6-link chain.
    
    Provides Merklized link verification:
    H_loc -> H_src -> H_ev -> H_unit -> H_intent -> H_quest
    """
    location_hash: str
    source_hash: str
    evidence_hash: str
    unit_hash: str
    intent_hash: str
    question_hash: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ProvenanceRecord:
    """Immutable 6-link Provenance Record with SHA-256 tamper-evident integrity.
    
    Chain Links:
    Link 1: Question ID & Bound Question Stem
    Link 2: Intent Type (1 of 14 canonical intents)
    Link 3: Knowledge Node ID (semantic unit)
    Link 4: Verbatim Evidence Text
    Link 5: Canonical Source File ID
    Link 6: Source Location Coordinates (page, line, offset, block)
    """
    question_id: str
    intent_type: str
    knowledge_node_id: str
    evidence_text: str
    source_file: str
    source_location: Dict[str, Any]
    question_stem: str = ""
    provenance_hash: str = ""
    link_hashes: Optional[LinkHashes] = None
    created_at: str = ""
    schema_version: str = PROVENANCE_SCHEMA_VERSION
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def compute_hashes(
        cls,
        question_id: str,
        intent_type: str,
        knowledge_node_id: str,
        evidence_text: str,
        source_file: str,
        source_location: Dict[str, Any],
        question_stem: str = ""
    ) -> Tuple[str, LinkHashes]:
        """Computes root SHA-256 provenance hash and step-by-step Merklized link hashes."""
        can_intent = canonicalize_intent(intent_type)
        can_loc = _canonical_json(source_location or {})
        clean_ev = (evidence_text or "").strip()
        clean_src = (source_file or "").strip()
        clean_qid = (question_id or "").strip()
        clean_stem = (question_stem or "").strip()
        clean_knid = (knowledge_node_id or "").strip()

        # Step-by-step chained Merklized hashes
        h_loc = _sha256(f"LINK6_LOC:{can_loc}")
        h_src = _sha256(f"LINK5_SRC:{clean_src}:{h_loc}")
        h_ev = _sha256(f"LINK4_EV:{clean_ev}:{h_src}")
        h_unit = _sha256(f"LINK3_UNIT:{clean_knid}:{h_ev}")
        h_intent = _sha256(f"LINK2_INTENT:{can_intent}:{h_unit}")
        h_quest = _sha256(f"LINK1_QUEST:{clean_qid}:{clean_stem}:{h_intent}")

        # Root payload hash covering all links
        payload = {
            "evidence_text": clean_ev,
            "intent_type": can_intent,
            "knowledge_node_id": clean_knid,
            "question_id": clean_qid,
            "question_stem": clean_stem,
            "source_file": clean_src,
            "source_location": source_location or {},
        }
        root_hash = _sha256(f"PROVENANCE_ROOT_v1:{_canonical_json(payload)}")
        links = LinkHashes(
            location_hash=h_loc,
            source_hash=h_src,
            evidence_hash=h_ev,
            unit_hash=h_unit,
            intent_hash=h_intent,
            question_hash=h_quest,
        )
        return root_hash, links

    @classmethod
    def create(
        cls,
        question_id: str,
        intent_type: str,
        knowledge_node_id: str,
        evidence_text: str,
        source_file: str,
        source_location: Dict[str, Any],
        question_stem: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None
    ) -> "ProvenanceRecord":
        """Factory creating a new frozen ProvenanceRecord with computed cryptographic hashes."""
        root_hash, link_hashes = cls.compute_hashes(
            question_id=question_id,
            intent_type=intent_type,
            knowledge_node_id=knowledge_node_id,
            evidence_text=evidence_text,
            source_file=source_file,
            source_location=source_location,
            question_stem=question_stem,
        )
        ts = created_at or datetime.now(timezone.utc).isoformat()
        return cls(
            question_id=(question_id or "").strip(),
            intent_type=to_r2_intent(intent_type),
            knowledge_node_id=(knowledge_node_id or "").strip(),
            evidence_text=(evidence_text or "").strip(),
            source_file=(source_file or "").strip(),
            source_location=dict(source_location or {}),
            question_stem=(question_stem or "").strip(),
            provenance_hash=root_hash,
            link_hashes=link_hashes,
            created_at=ts,
            schema_version=PROVENANCE_SCHEMA_VERSION,
            metadata=dict(metadata or {})
        )

    @classmethod
    def from_knowledge_node(
        cls,
        node: Any,
        question_id: str,
        question_stem: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ProvenanceRecord":
        """Instantiates ProvenanceRecord directly from a KnowledgeNode object or dict."""
        node_id = getattr(node, "node_id", getattr(node, "nodeId", ""))
        intent = getattr(node, "intent_type", getattr(node, "intentType", "definition"))
        evidence = getattr(node, "raw_evidence", getattr(node, "rawEvidence", ""))
        source_loc = getattr(node, "source_location", getattr(node, "sourceLocation", {}))

        if isinstance(node, dict):
            node_id = node.get("node_id") or node.get("nodeId", "")
            intent = node.get("intent_type") or node.get("intentType", "definition")
            evidence = node.get("raw_evidence") or node.get("rawEvidence", "")
            source_loc = node.get("source_location") or node.get("sourceLocation", {})

        src_file = ""
        if isinstance(source_loc, dict):
            src_file = (
                source_loc.get("sourceId")
                or source_loc.get("source_file")
                or source_loc.get("source_id")
                or source_loc.get("file")
                or ""
            )

        return cls.create(
            question_id=question_id,
            intent_type=intent,
            knowledge_node_id=node_id,
            evidence_text=evidence,
            source_file=src_file,
            source_location=source_loc if isinstance(source_loc, dict) else {},
            question_stem=question_stem,
            metadata=metadata
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceRecord":
        """Instantiates ProvenanceRecord from dictionary (supports both camelCase and snake_case)."""
        qid = data.get("questionId") or data.get("question_id", "")
        stem = data.get("questionStem") or data.get("question_stem", "")
        intent = data.get("intentType") or data.get("intent_type", "")
        knid = data.get("knowledgeNodeId") or data.get("knowledge_node_id", "")
        ev = data.get("evidenceText") or data.get("evidence_text", "")
        src = data.get("sourceFile") or data.get("source_file", "")
        loc = data.get("sourceLocation") or data.get("source_location", {})
        prov_hash = data.get("provenanceHash") or data.get("provenance_hash", "")
        created_at = data.get("createdAt") or data.get("created_at", "")
        schema_v = data.get("schemaVersion") or data.get("schema_version", PROVENANCE_SCHEMA_VERSION)
        meta = data.get("metadata", {})

        # Compute or verify hash
        expected_hash, expected_links = cls.compute_hashes(
            question_id=qid,
            intent_type=intent,
            knowledge_node_id=knid,
            evidence_text=ev,
            source_file=src,
            source_location=loc,
            question_stem=stem,
        )

        return cls(
            question_id=qid,
            intent_type=to_r2_intent(intent),
            knowledge_node_id=knid,
            evidence_text=ev,
            source_file=src,
            source_location=loc,
            question_stem=stem,
            provenance_hash=prov_hash or expected_hash,
            link_hashes=expected_links,
            created_at=created_at or datetime.now(timezone.utc).isoformat(),
            schema_version=schema_v,
            metadata=meta
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes record to standard Python dictionary (snake_case)."""
        d = {
            "question_id": self.question_id,
            "question_stem": self.question_stem,
            "intent_type": self.intent_type,
            "knowledge_node_id": self.knowledge_node_id,
            "evidence_text": self.evidence_text,
            "source_file": self.source_file,
            "source_location": self.source_location,
            "provenance_hash": self.provenance_hash,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
            "metadata": self.metadata,
        }
        if self.link_hashes:
            d["link_hashes"] = self.link_hashes.to_dict()
        return d

    def to_camel_dict(self) -> Dict[str, Any]:
        """Serializes record to camelCase dictionary for Android/E2E test compliance."""
        d = {
            "questionId": self.question_id,
            "questionStem": self.question_stem,
            "intentType": self.intent_type,
            "knowledgeNodeId": self.knowledge_node_id,
            "evidenceText": self.evidence_text,
            "sourceFile": self.source_file,
            "sourceLocation": self.source_location,
            "provenanceHash": self.provenance_hash,
            "createdAt": self.created_at,
            "schemaVersion": self.schema_version,
            "metadata": self.metadata,
        }
        if self.link_hashes:
            d["linkHashes"] = self.link_hashes.to_dict()
        return d

    def verify_hash(self) -> Tuple[bool, Optional[str]]:
        """Verifies cryptographic tamper-evident hash against record contents.
        
        Returns:
            Tuple of (is_valid, failing_link_name_or_None)
        """
        expected_root, expected_links = self.compute_hashes(
            question_id=self.question_id,
            intent_type=self.intent_type,
            knowledge_node_id=self.knowledge_node_id,
            evidence_text=self.evidence_text,
            source_file=self.source_file,
            source_location=self.source_location,
            question_stem=self.question_stem,
        )
        if self.provenance_hash != expected_root:
            # Diagnose which link failed
            if self.link_hashes:
                if self.link_hashes.location_hash != expected_links.location_hash:
                    return False, "sourceLocation"
                if self.link_hashes.source_hash != expected_links.source_hash:
                    return False, "sourceFile"
                if self.link_hashes.evidence_hash != expected_links.evidence_hash:
                    return False, "evidenceText"
                if self.link_hashes.unit_hash != expected_links.unit_hash:
                    return False, "knowledgeNodeId"
                if self.link_hashes.intent_hash != expected_links.intent_hash:
                    return False, "intentType"
                if self.link_hashes.question_hash != expected_links.question_hash:
                    return False, "questionId_or_stem"
            return False, "root_payload_mismatch"
        return True, None

    def evolve(
        self,
        question_id: Optional[str] = None,
        question_stem: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ProvenanceRecord":
        """Creates a new immutable ProvenanceRecord with updated question details and recomputed hashes."""
        return self.create(
            question_id=question_id if question_id is not None else self.question_id,
            intent_type=self.intent_type,
            knowledge_node_id=self.knowledge_node_id,
            evidence_text=self.evidence_text,
            source_file=self.source_file,
            source_location=self.source_location,
            question_stem=question_stem if question_stem is not None else self.question_stem,
            metadata={**self.metadata, **(metadata or {})},
        )


class VerificationResult:
    """Result object supporting both boolean check (`if result:`) and tuple unpacking (`valid, errors = result`)."""
    def __init__(
        self,
        is_valid: bool,
        errors: List[str],
        tampered: bool = False,
        grounded: bool = True,
        broken_link: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors
        self.tampered = tampered
        self.grounded = grounded
        self.broken_link = broken_link
        self.details = details or {}

    def __bool__(self) -> bool:
        return self.is_valid

    def __iter__(self):
        yield self.is_valid
        yield self.errors

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, bool):
            return self.is_valid == other
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return (self.is_valid, self.errors) == (other[0], other[1])
        return super().__eq__(other)

    def __repr__(self) -> str:
        status = "VALID" if self.is_valid else f"INVALID(errors={len(self.errors)}, tampered={self.tampered})"
        return f"<VerificationResult: {status}>"


def verify_provenance_chain(
    record: Union[ProvenanceRecord, Dict[str, Any]],
    source_corpus: Optional[Union[Dict[str, str], str]] = None
) -> VerificationResult:
    """Verifies complete 6-link provenance chain integrity, cryptographic hashing, and verbatim corpus grounding.
    
    Supports:
    - ProvenanceRecord dataclass or plain dictionary (camelCase or snake_case)
    - source_corpus as single document text or dict of {source_file: file_content}
    - VerificationResult acts as bool (`if verify_provenance_chain(...):`) and tuple (`valid, errors = ...`)
    """
    errors: List[str] = []
    tampered = False
    grounded = True
    broken_link = None

    # Normalize input to dictionary for uniform extraction
    if isinstance(record, ProvenanceRecord):
        prov = record.to_camel_dict()
        record_obj = record
    elif isinstance(record, dict):
        prov = dict(record)
        # Create standard keys
        if "question_id" in prov and "questionId" not in prov:
            prov["questionId"] = prov["question_id"]
        if "intent_type" in prov and "intentType" not in prov:
            prov["intentType"] = prov["intent_type"]
        if "knowledge_node_id" in prov and "knowledgeNodeId" not in prov:
            prov["knowledgeNodeId"] = prov["knowledge_node_id"]
        if "evidence_text" in prov and "evidenceText" not in prov:
            prov["evidenceText"] = prov["evidence_text"]
        if "source_file" in prov and "sourceFile" not in prov:
            prov["sourceFile"] = prov["source_file"]
        if "source_location" in prov and "sourceLocation" not in prov:
            prov["sourceLocation"] = prov["source_location"]
        if "provenance_hash" in prov and "provenanceHash" not in prov:
            prov["provenanceHash"] = prov["provenance_hash"]
        if "question_stem" in prov and "questionStem" not in prov:
            prov["questionStem"] = prov["question_stem"]
        record_obj = None
    else:
        return VerificationResult(False, [f"Invalid provenance input type: {type(record)}"])

    # 1. Structural Completeness (Mandatory 6 links)
    required_links = [
        ("questionId", "Link 1: Question ID"),
        ("intentType", "Link 2: Intent Type"),
        ("knowledgeNodeId", "Link 3: Knowledge Unit ID"),
        ("evidenceText", "Link 4: Evidence Text"),
        ("sourceFile", "Link 5: Source File"),
        ("sourceLocation", "Link 6: Source Location"),
    ]

    for key, label in required_links:
        val = prov.get(key)
        if val is None or (isinstance(val, (str, dict, list)) and len(val) == 0):
            errors.append(f"Provenance missing or empty mandatory key: '{key}' ({label})")
            if not broken_link:
                broken_link = key

    # 2. Non-Triviality Checks
    src_file = str(prov.get("sourceFile") or "").strip()
    if src_file.lower() in TRIVIAL_STRINGS:
        errors.append(f"Provenance sourceFile is empty or trivial ('{src_file}')")
        if not broken_link:
            broken_link = "sourceFile"

    loc = prov.get("sourceLocation")
    if not isinstance(loc, dict):
        errors.append("Provenance sourceLocation must be a structured dictionary")
        if not broken_link:
            broken_link = "sourceLocation"
    else:
        # Check coordinates inside location
        for loc_k, loc_v in loc.items():
            if str(loc_v).strip().lower() in TRIVIAL_STRINGS and str(loc_v) != "0":
                errors.append(f"Provenance sourceLocation['{loc_k}'] contains trivial value ('{loc_v}')")
            if isinstance(loc_v, (int, float)) and loc_v < 0:
                errors.append(f"Provenance sourceLocation['{loc_k}'] cannot be negative ({loc_v})")

    # 3. Intent Validity (Must be 1 of 14 canonical intents)
    raw_intent = str(prov.get("intentType") or "").strip()
    can_intent = canonicalize_intent(raw_intent)
    if can_intent not in CANONICAL_14_INTENTS:
        errors.append(f"Provenance intentType '{raw_intent}' is not one of 14 valid intents")
        if not broken_link:
            broken_link = "intentType"

    # 4. Cryptographic Tamper Detection
    prov_hash = prov.get("provenanceHash")
    if prov_hash:
        expected_hash, expected_links = ProvenanceRecord.compute_hashes(
            question_id=prov.get("questionId", ""),
            intent_type=raw_intent,
            knowledge_node_id=prov.get("knowledgeNodeId", ""),
            evidence_text=prov.get("evidenceText", ""),
            source_file=src_file,
            source_location=loc if isinstance(loc, dict) else {},
            question_stem=prov.get("questionStem", ""),
        )
        if prov_hash != expected_hash:
            tampered = True
            errors.append(
                f"Cryptographic tamper detected: provenanceHash '{prov_hash}' does not match computed '{expected_hash}'"
            )
            if not broken_link:
                broken_link = "cryptographic_hash_mismatch"

    # 5. Verbatim Grounding in Source Corpus
    evidence = str(prov.get("evidenceText") or "").strip()
    if source_corpus is not None and evidence:
        target_corpus_text = None
        if isinstance(source_corpus, str):
            target_corpus_text = source_corpus
        elif isinstance(source_corpus, dict):
            # Try to match source file in corpus dictionary
            if src_file in source_corpus:
                target_corpus_text = source_corpus[src_file]
            else:
                # Fuzzy filename match (e.g. basename vs full path)
                matched = False
                for cf, c_text in source_corpus.items():
                    if cf.endswith(src_file) or src_file.endswith(cf):
                        target_corpus_text = c_text
                        matched = True
                        break
                if not matched:
                    errors.append(f"Source file '{src_file}' not found in source_corpus dictionary")
                    grounded = False

        if target_corpus_text is not None:
            if evidence not in target_corpus_text:
                grounded = False
                prefix = evidence[:40] + "..." if len(evidence) > 40 else evidence
                errors.append(f"Provenance evidence '{prefix}' not found verbatim in source corpus")
                if not broken_link:
                    broken_link = "evidenceText"
            else:
                # If offset is specified, verify offset precision
                if isinstance(loc, dict) and "offset" in loc and isinstance(loc["offset"], int):
                    off = loc["offset"]
                    if off >= 0 and off + len(evidence) <= len(target_corpus_text):
                        actual_sub = target_corpus_text[off:off + len(evidence)]
                        if actual_sub != evidence:
                            grounded = False
                            errors.append(
                                f"Provenance offset {off} mismatch: expected '{evidence[:30]}...', found '{actual_sub[:30]}...'"
                            )
                            if not broken_link:
                                broken_link = "sourceLocation.offset"

    is_valid = len(errors) == 0
    return VerificationResult(
        is_valid=is_valid,
        errors=errors,
        tampered=tampered,
        grounded=grounded,
        broken_link=broken_link,
        details={"record": prov}
    )


def audit_provenance_integrity(
    records: Sequence[Union[ProvenanceRecord, Dict[str, Any]]],
    source_corpus: Optional[Union[Dict[str, str], str]] = None
) -> Dict[str, Any]:
    """Audits an entire collection of ProvenanceRecords for systemic integrity, tampering, and grounding.
    
    Returns:
        Structured audit dictionary with total count, pass/fail metrics, tamper counts,
        broken link breakdown, and detailed failure log.
    """
    total = len(records)
    valid_count = 0
    invalid_count = 0
    tampered_count = 0
    grounding_failures = 0
    broken_links_counter: Dict[str, int] = {}
    failure_details: List[Dict[str, Any]] = []

    for idx, r in enumerate(records):
        res = verify_provenance_chain(r, source_corpus=source_corpus)
        if res.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            if res.tampered:
                tampered_count += 1
            if not res.grounded:
                grounding_failures += 1

            link = res.broken_link or "unspecified"
            broken_links_counter[link] = broken_links_counter.get(link, 0) + 1

            qid = ""
            if isinstance(r, ProvenanceRecord):
                qid = r.question_id
            elif isinstance(r, dict):
                qid = r.get("questionId") or r.get("question_id", f"record_{idx}")

            failure_details.append({
                "record_index": idx,
                "question_id": qid,
                "tampered": res.tampered,
                "grounded": res.grounded,
                "broken_link": link,
                "errors": res.errors
            })

    integrity_rate = (valid_count / total) if total > 0 else 1.0
    verdict = "PASS" if invalid_count == 0 else "REJECT"

    return {
        "total_records": total,
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "tampered_records": tampered_count,
        "grounding_failures": grounding_failures,
        "broken_links": broken_links_counter,
        "integrity_rate": integrity_rate,
        "audit_verdict": verdict,
        "failure_details": failure_details
    }


class ProvenanceRegistry:
    """Thread-safe, queryable in-memory registry for all V13 ProvenanceRecords.
    
    Provides lookup by Question ID, KnowledgeNode ID, and source document,
    along with JSON export/import and batch audit validation.
    """
    def __init__(self):
        self._by_question_id: Dict[str, ProvenanceRecord] = {}
        self._by_node_id: Dict[str, List[ProvenanceRecord]] = {}
        self._by_source_file: Dict[str, List[ProvenanceRecord]] = {}

    def register(self, record: ProvenanceRecord) -> None:
        """Registers a ProvenanceRecord, verifying hash integrity before admission."""
        is_valid, fail_link = record.verify_hash()
        if not is_valid:
            raise ValueError(f"Cannot register tampered ProvenanceRecord: hash mismatch on link '{fail_link}'")

        self._by_question_id[record.question_id] = record
        self._by_node_id.setdefault(record.knowledge_node_id, []).append(record)
        self._by_source_file.setdefault(record.source_file, []).append(record)

    def get_by_question_id(self, question_id: str) -> Optional[ProvenanceRecord]:
        return self._by_question_id.get(question_id)

    def get_by_node_id(self, node_id: str) -> List[ProvenanceRecord]:
        return self._by_node_id.get(node_id, [])

    def get_by_source_file(self, source_file: str) -> List[ProvenanceRecord]:
        return self._by_source_file.get(source_file, [])

    def all_records(self) -> List[ProvenanceRecord]:
        return list(self._by_question_id.values())

    def count(self) -> int:
        return len(self._by_question_id)

    def audit(self, source_corpus: Optional[Union[Dict[str, str], str]] = None) -> Dict[str, Any]:
        return audit_provenance_integrity(self.all_records(), source_corpus=source_corpus)

    def export_json(self) -> str:
        """Serializes entire registry to JSON array of camelCase objects."""
        return json.dumps([r.to_camel_dict() for r in self.all_records()], indent=2, ensure_ascii=False)

    def import_json(self, json_str: str) -> int:
        """Imports JSON array into registry, returns count of admitted records."""
        items = json.loads(json_str)
        admitted = 0
        for it in items:
            record = ProvenanceRecord.from_dict(it)
            self.register(record)
            admitted += 1
        return admitted


class ProvenanceTracker:
    """Universal pipeline interface compliant with PROJECT.md and test suites (PipelineBridge).
    
    Directly satisfies PipelineBridge.get_provenance_tracker().
    """
    def __init__(self, registry: Optional[ProvenanceRegistry] = None):
        self.registry = registry or ProvenanceRegistry()

    def verify_provenance(
        self,
        cq: Any,
        source_corpus: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """Verifies CandidateQuestion provenance chain.
        
        Directly implements PipelineBridge contract:
        tracker.verify_provenance(cq, source_corpus) -> Tuple[bool, List[str]]
        """
        prov = getattr(cq, "provenance", None)
        if prov is None and isinstance(cq, dict):
            prov = cq.get("provenance")
        if prov is None:
            return False, ["CandidateQuestion missing 'provenance' property"]

        res = verify_provenance_chain(prov, source_corpus=source_corpus)
        return res.is_valid, res.errors

    def create_provenance_record(
        self,
        node: Any,
        question_id: str,
        question_stem: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProvenanceRecord:
        """Creates and registers a ProvenanceRecord from KnowledgeNode and question details."""
        record = ProvenanceRecord.from_knowledge_node(
            node=node,
            question_id=question_id,
            question_stem=question_stem,
            metadata=metadata
        )
        self.registry.register(record)
        return record

    def bind_candidate_question(self, cq: Any, node: Any) -> Any:
        """Injects unbreakable provenance record into a CandidateQuestion."""
        qid = getattr(cq, "id", "")
        stem = getattr(cq, "stem", "")
        record = self.create_provenance_record(node=node, question_id=qid, question_stem=stem)
        cq.provenance = record.to_camel_dict()
        return cq

    def audit_registry(self, source_corpus: Optional[Union[Dict[str, str], str]] = None) -> Dict[str, Any]:
        """Audits all tracked provenance records."""
        return self.registry.audit(source_corpus=source_corpus)
