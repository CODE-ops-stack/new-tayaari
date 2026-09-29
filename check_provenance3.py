with open('tayaariapp/v13_discovery/provenance.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[235:280], start=235):
        print(f'{i}: {line.rstrip()}')