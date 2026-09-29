#!/usr/bin/env python3
"""
Generate 1200+ geography questions from all corpus materials.
Filters out nodes with known problematic evidence patterns.
"""

import json
import random
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity

# Patterns indicating problematic evidence that won't match corpus
PROBLEMATIC_EVIDENCE_PATTERNS = [
    # Boilerplate/copyright text
    'this book is sold subject to',
    'sold subject to the condition',
    'by way of trade',
    'publisher',
    'copyright',
    'isbn',
    'ncert',
    # Truncated sentences that won't match
    'fundamentals of physical geography (',
    'causes of earthquakes in your book',
    'coed efforts',
    'concerted efforts are on',
]

def is_problematic_evidence(evidence: str) -> bool:
    """Check if evidence text has known issues that prevent corpus matching."""
    ev_lower = evidence.lower()
    for pattern in PROBLEMATIC_EVIDENCE_PATTERNS:
        if pattern in ev_lower:
            return True
    return False

def main():
    print("=" * 60)
    print("Generating 1200+ Geography Questions (Clean Provenance)")
    print("=" * 60)
    
    corpus_files = [
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted_2.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_physical_geo.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_india_env.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_human_geo.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xii_india_economy.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_x_geo.txt',
        r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_ix_geo.txt',
    ]
    
    corpus_dict = {}
    print("\n1. Loading corpus files...")
    for cf in corpus_files:
        with open(cf, 'rb') as f:
            corpus_dict[cf] = f.read().decode('utf-8', errors='replace')
        print(f"  Loaded: {cf}")
    
    normalizer = DocumentNormalizer()
    extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
    
    print("\n2. Extracting knowledge nodes...")
    all_nodes = []
    for cf, content in corpus_dict.items():
        blocks = normalizer.normalize(cf, content)
        file_nodes = []
        for b in blocks:
            file_nodes.extend(extractor.extract(b))
        all_nodes.extend(file_nodes)
        print(f"  {cf}: {len(file_nodes)} nodes")
    
    print(f"\nTotal nodes: {len(all_nodes)}")
    
    # Filter out nodes with problematic evidence
    filtered_nodes = [n for n in all_nodes if not is_problematic_evidence(getattr(n, 'raw_evidence', ''))]
    print(f"Nodes after filtering problematic evidence: {len(filtered_nodes)}")
    
    # Shuffle for diversity
    random.seed(42)
    random.shuffle(filtered_nodes)
    
    synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
    tracker = ProvenanceTracker()
    
    print("\n3. Generating questions (target: 1200)...")
    valid_questions = []
    seen_stems = set()
    intent_counts = {}
    source_counts = {}
    
    for i, node in enumerate(filtered_nodes):
        if len(valid_questions) >= 1200:
            break
        if not node.primary_entity or len(node.primary_entity) < 3:
            continue
        if len(node.raw_evidence) < 25:
            continue
        try:
            cq = synth.synthesize(node)
            if cq.valid:
                norm_stem = cq.stem.strip().lower()
                if norm_stem in seen_stems:
                    continue
                seen_stems.add(norm_stem)
                tracker.bind_candidate_question(cq, node)
                valid_questions.append(cq)
                
                intent = cq.provenance.get('intentType', 'unknown')
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
                src = cq.provenance.get('sourceFile', 'unknown')
                source_counts[src] = source_counts.get(src, 0) + 1
                
                if len(valid_questions) % 100 == 0:
                    print(f"  Generated {len(valid_questions)} questions...")
        except Exception as e:
            pass
    
    print(f"\nGenerated {len(valid_questions)} questions")
    print(f"Intent distribution: {intent_counts}")
    print(f"Source files covered: {len(source_counts)}")
    
    # Verify provenance
    print("\n4. Verifying provenance integrity...")
    batch_records = [cq.provenance for cq in valid_questions]
    audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)
    print(f"  Total: {audit_res['total_records']}")
    print(f"  Valid: {audit_res['valid_records']}")
    print(f"  Invalid: {audit_res['invalid_records']}")
    print(f"  Verdict: {audit_res['audit_verdict']}")
    print(f"  Integrity Rate: {audit_res['integrity_rate']:.2%}")
    
    # Export
    print("\n5. Exporting questions...")
    output_path = r'C:\Users\harsh\Downloads\tayaari\tayaariapp\generated_questions_1200_clean.json'
    export_data = []
    for cq in valid_questions:
        export_data.append({
            'id': cq.id,
            'stem': cq.stem,
            'options': cq.options,
            'correctAnswer': cq.correctAnswer,
            'explanation': cq.explanation,
            'distractorDissections': cq.distractorDissections,
            'provenance': cq.provenance,
            'cognitiveDemand': cq.cognitiveDemand,
            'examTarget': cq.examTarget,
            'tier': cq.tier,
            'format': cq.format,
            'topicId': cq.topicId,
            'topicName': cq.topicName,
            'pdfSequenceNumber': cq.pdfSequenceNumber,
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(export_data)} questions to {output_path}")
    
    print("\n" + "=" * 60)
    if len(valid_questions) >= 1200:
        print(f"SUCCESS: Generated {len(valid_questions)} questions (target: 1200)")
    else:
        print(f"PARTIAL: Generated {len(valid_questions)} questions (target: 1200)")
    if audit_res['audit_verdict'] == 'PASS':
        print("Provenance: PASS")
    else:
        print("Provenance: NEEDS FIXING")
    print("=" * 60)

if __name__ == '__main__':
    main()