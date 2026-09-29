with open('tests/test_v13_adversarial_m5_auditor_stress.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'options=' in line and ('"' in line or "'" in line) and ('{' in line or '[' in line):
            print(f'Line {i+1}: {line.strip()}')