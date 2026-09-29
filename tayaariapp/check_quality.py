import json
import random

with open('generated_questions_1200_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sample 20 questions to check quality
random.seed(42)
sample = random.sample(data, 20)

for q in sample:
    print('ID:', q['id'])
    print('  Topic:', q['topicName'])
    print('  Intent:', q['provenance'].get('intentType', 'unknown'))
    stem = q['stem']
    print('  Stem:', stem[:120] + '...' if len(stem) > 120 else stem)
    print('  Correct:', q['options'].get(q['correctAnswer'], 'NOT FOUND'))
    opts = q.get('options', {})
    correct_letter = q['correctAnswer'].replace('opt_', '')
    for k, v in opts.items():
        marker = ' <-- CORRECT' if k == correct_letter else ''
        print('    {}: {}{}'.format(k, v[:80], marker))
    exp = q['explanation']
    print('  Explanation:', exp[:100] + '...' if len(exp) > 100 else exp)
    print()