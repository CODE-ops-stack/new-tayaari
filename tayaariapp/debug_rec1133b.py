evidence = 'You have already learnt the causes of earthquakes in your book Fundamentals of Physical Geography ('
corpus = ' plates in the book Fundamentals of Physical Geography (NCERT, 2006). Do you know that the Indian plate was to the south'

# Check if evidence is in corpus
print('Evidence in corpus:', evidence in corpus)
print('Evidence[-20:]:', repr(evidence[-20:]))
idx = corpus.find('Fundamentals')
print('Corpus snippet:', repr(corpus[idx:idx+60]))