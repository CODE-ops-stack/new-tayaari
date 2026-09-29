from v13_discovery.question_synthesizer import NaturalStemSynthesizer

# Test the _deidentify_entity function directly
test_cases = [
    ('Full moon night or Poornima', 'Moon'),
    ('New moon night or Amavasya', 'Moon'),
    ('is also called the Pole Star', 'Star'),
    ('is our nearest star', 'Star'),
]

for text, entity in test_cases:
    result = NaturalStemSynthesizer._deidentify_entity(text, entity)
    print(f'Input: "{text}" | Entity: "{entity}"')
    print(f'Output: "{result}"')
    print()