with open('tayaariapp/v13_discovery/question_synthesizer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[995:1030], start=995):
        print(f'{i}: {line.rstrip()}')