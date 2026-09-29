corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

# Find the relevant sections
sections = [
    'circle part of the paper',
    'One of the most easily recognisable',
    'One orbit around sun - 687 days',
    'Venus is considered',
    'two Greek words',
    'Sol in Roman',
    'Rocket launch'
]

for s in sections:
    idx = corpus.find(s)
    if idx >= 0:
        print(f'FOUND: "{s}" at position {idx}')
        print(f'  Context: ...{corpus[max(0,idx-50):idx+150]}...')
    else:
        print(f'NOT FOUND: "{s}"')
    print()