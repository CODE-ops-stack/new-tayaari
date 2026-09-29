corpus = open(r'C:\Users\harsh\Downloads\tayaari\tayaariapp\source-material\ncert_xi_india_env.txt', 'r', encoding='utf-8', errors='ignore').read()

# Check record 1133
ev = 'You have already learnt the causes of earthquakes in your book Fundamentals of Physical Geography ('
idx = corpus.find('causes of earthquakes')
if idx >= 0:
    print('Found at', idx)
    print(repr(corpus[max(0,idx-20):idx+200]))
else:
    print('NOT FOUND')

# Check record 1190
ev2 = 'q This book is sold subject to the condition that it shall not, by way of trade, be lent, resold, hi'
idx2 = corpus.find('This book is sold')
if idx2 >= 0:
    print('Found at', idx2)
    print(repr(corpus[max(0,idx2-20):idx2+200]))
else:
    print('NOT FOUND')