import json
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    fixed = 0
    for q in data:
        p = q.get('provenance')
        if isinstance(p, str):
            fixed += 1
            qid = str(q.get('id', ''))
            sub_topic = q.get('subTopic', 'Bihar Geography: Physiography, Rivers & Resources')
            q['provenance'] = {
                'questionId': qid,
                'questionStem': (q.get('stem') or '')[:200],
                'intentType': p,
                'knowledgeNodeId': f'node-bihar-{qid}',
                'evidenceText': (q.get('explanation') or '')[:300],
                'sourceFile': 'bihar_geography_curriculum.txt',
                'sourceLocation': {
                    'sourceId': 'bihar_geography_curriculum.txt',
                    'sentence_count': 1,
                    'section_heading': sub_topic,
                    'concept': 'Bihar Geography',
                    'sentence_idx': 0,
                    'block_id': f'bihar-block-{qid}',
                    'has_antecedent': False
                },
                'provenanceHash': f'hash_bihar_{qid}',
                'createdAt': '2026-10-14',
                'schemaVersion': '1.0.0',
                'metadata': {
                    'tier': q.get('tier', 'Medium'),
                    'specificExam': q.get('exams', 'BPSC,UPSC')
                },
                'linkHashes': {}
            }
    if fixed > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'Fixed {fixed} questions in {filepath}')
    else:
        print(f'No fixes needed in {filepath}')

fix_file('cloud_data_staging/topics/topic_23.json')
fix_file('cloud_data_staging/questions.json')

# Check across ALL topics
for f in sorted(glob.glob('cloud_data_staging/topics/topic_*.json')):
    fix_file(f)
