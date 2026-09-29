corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_physical_geo.txt', 'r', encoding='utf-8', errors='ignore').read()

# Check record 1010
ev = 'However, it was Alfred Wegener - a German meteorologist who put forth a comprehensive argument in th'
idx = corpus.find('Alfred Wegener')
if idx >= 0:
    print('Found at', idx)
    print(repr(corpus[max(0,idx-20):idx+200]))
else:
    print('NOT FOUND')