evidence = 'You have already learnt the causes of earthquakes in your book Fundamentals of Physical Geography ('
corpus = ' plates in the book Fundamentals of Physical Geography (NCERT, 2006). Do you know that the Indian plate was to the south'

# Check character by character
ev_sub = 'Fundamentals of Physical Geography ('
corpus_sub = corpus[corpus.find('Fundamentals'):corpus.find('Fundamentals')+40]

print('Evidence sub:', repr(ev_sub))
print('Corpus sub:  ', repr(corpus_sub))
print('Equal:', ev_sub == corpus_sub[:len(ev_sub)])
print('In:', ev_sub in corpus_sub)