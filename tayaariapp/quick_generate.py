#!/usr/bin/env python3
"""
Quick test: Generate 200 questions to verify the pipeline works.
"""

import json
import random
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity

def main():
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
    for cf in corpus_files:
        with open(cf, 'rb') as f:
            corpus_dict[cf] = f.read().decode('utf-8', errors='replace')
    
    normalizer = DocumentNormalizer()
    extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
    
    all_nodes = []
    for cf, content in corpus_dict.items():
        blocks = normalizer.normalize(cf, content)
        for b in blocks:
            all_nodes.extend(extractor.extract(b))
    
    print(f"Total nodes: {len(all_nodes)}")
    
    # Use only first 1000 nodes for speed
    test_nodes = all_nodes[:1000]
    random.seed(42)
    random.shuffle(test_nodes)
    
    synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
    tracker = ProvenanceTracker()
    
    valid_questions = []
    seen_stems = set()
    intent_counts = {}
    
    for i, node in enumerate(test_nodes):
        if len(valid_questions) >= 200:
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
        except Exception as e:
            pass
    
    print(f"Generated {len(valid_questions)} questions")
    print(f"Intent distribution: {intent_counts}")
    
    # Verify provenance
    batch_records = [cq.provenance for cq in valid_questions]
    audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)
    print(f"Audit: {audit_res['audit_verdict']}, Invalid: {audit_res['invalid_records']}")

if __name__ == '__main__':
    main()