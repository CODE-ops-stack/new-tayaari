import re

with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'r', encoding='utf-8') as f:
    content = f.read()

matches = list(re.finditer(r'options\s*=\s*[\'"]', content))
for m in matches:
    idx = m.start()
    line_num = content[:idx].count('\n') + 1
    next_chars = content[m.end():m.end()+5]
    if '{' not in next_chars and '[' not in next_chars:
        print(f'Line {line_num}: Found options= with string')
        start = max(0, m.start()-50)
        end = min(len(content), m.end()+50)
        print(f'Context: ...{content[m.start():m.end()+50]}...')
        print('---')