from v13_discovery.question_synthesizer import NaturalStemSynthesizer

text = 'the lowest layer'
entity = 'Troposphere'
result = NaturalStemSynthesizer._deidentify_entity(text, entity)
print(f'Input: "{text}" | Entity: "{entity}"')
print(f'Output: "{result}"')