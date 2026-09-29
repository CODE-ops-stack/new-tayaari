corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\geography_extracted.txt', 'r', encoding='utf-8', errors='ignore').read()

evidences = [
    'circle part of the paper on the glass front and wrap the with a rubber band.',
    'One of the most easily recognisable constellation is the Saptarishi (Saptaseven,',
    'One orbit around sun - 687 days.',
    "Venus is considered as Earths-twin' because its size and shape are very much sim",
    "It is made of two Greek words, ge meaning earth and graphia meaning writing'.",
    'Sol in Roman mythology is the Sungod.',
    'Rocket launch Rocket falls back to the Earth Satellite enters orbit'
]

for ev in evidences:
    norm_ev = ' '.join(ev.split())
    norm_corpus = ' '.join(corpus.split())
    if norm_ev in norm_corpus:
        print('FOUND (normalized):', ev[:60])
    else:
        print('NOT FOUND:', ev[:60])
        # Try to find similar text
        words = ev.split()[:8]
        found = False
        for i in range(len(words)-2):
            substr = ' '.join(words[i:i+3])
            if substr in corpus:
                print('  Substring found:', substr)
                found = True
                break
        if not found:
            # Try smaller substrings
            for i in range(len(words)-1):
                substr = ' '.join(words[i:i+2])
                if substr in corpus:
                    print('  Substring found:', substr)
                    found = True
                    break
        if not found:
            print('  No substrings found')