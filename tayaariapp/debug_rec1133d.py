evidence = 'You have already learnt the causes of earthquakes in your book Fundamentals of Physical Geography ('
corpus = ' plates in the book Fundamentals of Physical Geography (NCERT, 2006). Do you know that the Indian plate was to the south'

print('Full evidence in corpus:', evidence in corpus)
print('Evidence length:', len(evidence))
print('Corpus length:', len(corpus))

# Find the evidence in corpus
idx = corpus.find(evidence[:50])
if idx >= 0:
    print('Found prefix at', idx)
    print('Corpus from idx:', repr(corpus[idx:idx+len(evidence)]))
    print('Match:', corpus[idx:idx+len(evidence)] == evidence)
else:
    print('Prefix not found')
    
# Check last 30 chars of evidence
print('Evidence end:', repr(evidence[-30:]))
print('Corpus at match:', repr(corpus[corpus.find('Fundamentals'):corpus.find('Fundamentals')+len(evidence)-corpus.find('Fundamentals')+100]))