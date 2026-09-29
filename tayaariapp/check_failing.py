#!/usr/bin/env python3
"""
Check failing provenance record.
"""

import json
import random
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity, verify_provenance_chain

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
    
    test_nodes = all_nodes[:1000]
    random.seed(42)
    random.shuffle(test_nodes)
    
    synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
    tracker = ProvenanceTracker()
    
    valid_questions = []
    seen_stems = set()
    
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
        except Exception as e:
            pass
    
    print(f"Generated {len(valid_questions)} questions")
    
    # Check each provenance
    for i, cq in enumerate(valid_questions):
        res = verify_provenance_chain(cq.provenance, source_corpus=corpus_dict)
        if not res.is_valid:
            print(f"FAILED record {i}:")
            print(f"  Evidence: {cq.provenance.get('evidenceText', '')[:100]}")
            print(f"  Errors: {res.errors}")
            print(f"  Broken link: {res.broken_link}")
            print()

if __name__ == '__main__':
    main()