import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

def print_function(lines):
    in_func = False
    for i, line in enumerate(lines):
        if 'fun PremiumOptionsList' in line:
            in_func = True
            print(f'{i}: {line}', end='')
        elif in_func:
            print(f'{i}: {line}', end='')
            if line.strip() == '}' and i > 650:
                return

print_function(lines)
