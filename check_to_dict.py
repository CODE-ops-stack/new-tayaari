with open('tayaariapp/v13_discovery/question_synthesizer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[80:130], start=80):
        print(f'{i}: {line.rstrip()}')