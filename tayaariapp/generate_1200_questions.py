#!/usr/bin/env python3
"""
Generate 1200+ high-quality geography questions from all available corpus materials.
Uses NCERT textbooks, SSC PYQs, and other source materials.
"""

import json
import os
from v13_discovery.normalizer import DocumentNormalizer
from v13_discovery.semantic_extractor import SemanticExtractor
from v13_discovery.question_synthesizer import QuestionSynthesizer
from v13_discovery.provenance import ProvenanceTracker, audit_provenance_integrity

def load_all_corpus():
    """Load all corpus files with absolute paths."""
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
        try:
            with open(cf, 'rb') as f:
                content = f.read().decode('utf-8', errors='replace')
            corpus_dict[cf] = content
            print(f"Loaded: {cf} ({len(content)} chars)")
        except Exception as e:
            print(f"ERROR loading {cf}: {e}")
    return corpus_dict

def extract_all_nodes(corpus_dict):
    """Extract knowledge nodes from all corpus files."""
    normalizer = DocumentNormalizer()
    extractor = __import__('v13_discovery.semantic_extractor', fromlist=['SemanticExtractor']).SemanticExtractor()
    
    all_nodes = []
    for cf, content in corpus_dict.items():
        blocks = normalizer.normalize(cf, content)
        file_nodes = []
        for b in blocks:
            file_nodes.extend(extractor.extract(b))
        all_nodes.extend(file_nodes)
        print(f"  {cf}: {len(blocks)} blocks, {len(file_nodes)} nodes")
    
    print(f"Total nodes extracted: {len(all_nodes)}")
    return all_nodes

def generate_questions(nodes, target_count=1200):
    """Generate questions from nodes with diversity across intent types."""
    synth = __import__('v13_discovery.question_synthesizer', fromlist=['QuestionSynthesizer']).QuestionSynthesizer()
    tracker = ProvenanceTracker()
    
    valid_questions = []
    seen_stems = set()
    intent_counts = {}
    source_file_counts = {}
    
    # Shuffle nodes to get diverse coverage
    import random
    random.seed(42)
    shuffled_nodes = nodes[:]
    random.shuffle(shuffled_nodes)
    
    for i, node in enumerate(shuffled_nodes):
        if len(valid_questions) >= target_count:
            break
        
        # Quality filters
        if not node.primary_entity or len(node.primary_entity) < 3:
            continue
        if len(node.raw_evidence) < 25:
            continue
        
        try:
            cq = synth.synthesize(node)
            if not cq.valid:
                continue
            
            norm_stem = cq.stem.strip().lower()
            if norm_stem in seen_stems:
                continue
            
            seen_stems.add(norm_stem)
            tracker.bind_candidate_question(cq, node)
            valid_questions.append(cq)
            
            intent = cq.provenance.get('intentType', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            src = cq.provenance.get('sourceFile', 'unknown')
            source_file_counts[src] = source_file_counts.get(src, 0) + 1
            
        except Exception as e:
            pass
    
    print(f"\nGenerated {len(valid_questions)} valid questions")
    print(f"Intent distribution: {intent_counts}")
    print(f"Source file distribution: {len(source_file_counts)} files")
    return valid_questions, tracker

def verify_provenance(questions, corpus_dict):
    """Verify provenance integrity of generated questions."""
    batch_records = [cq.provenance for cq in questions]
    audit_res = audit_provenance_integrity(batch_records, source_corpus=corpus_dict)
    print(f"\nProvenance Audit:")
    print(f"  Total: {audit_res['total_records']}")
    print(f"  Valid: {audit_res['valid_records']}")
    print(f"  Invalid: {audit_res['invalid_records']}")
    print(f"  Tampered: {audit_res['tampered_records']}")
    print(f"  Verdict: {audit_res['audit_verdict']}")
    print(f"  Integrity Rate: {audit_res['integrity_rate']:.2%}")
    if audit_res['broken_links']:
        print(f"  Broken Links: {audit_res['broken_links']}")
    return audit_res

def export_questions(questions, output_path):
    """Export questions to JSON file."""
    export_data = []
    for cq in questions:
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
    print(f"\nExported {len(export_data)} questions to {output_path}")

def main():
    print("=" * 60)
    print("Generating 1200+ Geography Questions")
    print("=" * 60)
    
    # Load all corpus
    print("\n1. Loading corpus files...")
    corpus_dict = load_all_corpus()
    
    # Extract nodes
    print("\n2. Extracting knowledge nodes...")
    all_nodes = extract_all_nodes(corpus_dict)
    
    # Generate questions
    print(f"\n3. Generating questions (target: 1200)...")
    questions, tracker = generate_questions(all_nodes, target_count=1200)
    
    # Verify provenance
    print("\n4. Verifying provenance integrity...")
    audit_res = verify_provenance(questions, corpus_dict)
    
    # Export
    print("\n5. Exporting questions...")
    output_path = r'C:\Users\harsh\Downloads\tayaari\tayaariapp\generated_questions_1200.json'
    export_questions(questions, output_path)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    
    # Check if we meet the target
    if len(questions) >= 1200:
        print(f"SUCCESS: Generated {len(questions)} questions (target: 1200)")
    else:
        print(f"WARNING: Generated {len(questions)} questions (target: 1200)")
    
    if audit_res['audit_verdict'] == 'PASS':
        print("Provenance: PASS")
    else:
        print("Provenance: FAIL - needs fixing")

if __name__ == '__main__':
    main()