with open('tayaariapp/v13_discovery/provenance.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[855:890], start=855):
        print(f'{i}: {line.rstrip()}')