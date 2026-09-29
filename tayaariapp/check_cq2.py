import re

with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'r', encoding='utf-8') as f:
    content = f.read()

matches = list(re.finditer(r'CandidateQuestion\([^)]*\)', content, re.DOTALL))
for m in re.finditer(r'CandidateQuestion\([^)]*\)', content, re.DOTALL):
    call = m.group(0)
    if 'options=' in call:
        options_part = call[call.find('options='):]
        if call.startswith('options=', call.find('options=')) and ':' in call[call.find('options='):call.find('options=')+20] and '{' not in call[call.find('options='):call.find('options=')+20]:
            line_num = content[:m.start()].count('\n') + 1
            print(f'OLD FORMAT at line {content[:m.start()].count(chr(10)) + 1}')
            print(call[:200])
            print('---')