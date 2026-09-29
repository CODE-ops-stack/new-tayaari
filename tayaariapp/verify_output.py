import json
with open('generated_questions_1200_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('Total questions:', len(data))
print('First question:')
q = data[0]
print('  ID:', q['id'])
print('  Stem:', q['stem'][:100])
print('  Options:', list(q['options'].keys()))
print('  Correct:', q['correctAnswer'])
print('  Intent:', q['provenance'].get('intentType', 'unknown'))
print('  Source:', q['provenance'].get('sourceFile', 'unknown'))