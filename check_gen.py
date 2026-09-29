with open('tayaariapp/generate_1200_final.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[100:150], start=100):
        print(f'{i}: {line.rstrip()}')