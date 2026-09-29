with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = list(re.finditer(r'CandidateQuestion\([^)]*\)', content, re.DOTALL))
for m in re.finditer(r'CandidateQuestion\([^)]*\)', content, re.DOTALL):
    call = m.group(0)
    if 'options=' in call and '{' in call and ':' in call and ('"' in call or "'" in call):
        line_num = content[:m.start()].count('\n') + 1
        print(f'Line {line_num}: {call[:200]}...')
        print('---')