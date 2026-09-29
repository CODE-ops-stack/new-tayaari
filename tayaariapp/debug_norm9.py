import unicodedata
import re

text = "Sapta-\nseven, rishi-sages)."

print('Original:', repr(text))

# Step 1: NFKC
t = unicodedata.normalize('NFKC', text)
print('After NFKC:', repr(t))

# Step 2: smart quotes (none)
t = t.replace('\u2018', "'").replace('\u2019', "'")
t = t.replace('\u201c', '"').replace('\u201d', '"')
print('After smart quotes:', repr(t))

# Step 3: remove quotes
t = t.replace("'", "").replace('"', '')
print('After remove quotes:', repr(t))

# Step 4: ampersand (none)
t = t.replace('&', ' and ')
print('After ampersand:', repr(t))

# Step 5: J&K (none)
t = t.replace('J&K', 'J and K')
print('After J&K:', repr(t))

# Step 6: soft hyphens
t = re.sub(r'-\s*\n\s*', '-', t)
print('After soft hyphens:', repr(t))

# Step 7: newlines between words
t = re.sub(r'\s*\n\s*', ' ', t)
print('After newlines:', repr(t))

# Step 8: underscores (none)
t = re.sub(r'_{3,}', '', t)
print('After underscores:', repr(t))

# Step 9: merged words (none)
t = t.replace('humaninduced', 'human induced')
t = t.replace('shoeshaped', 'shoe shaped')
t = t.replace('GodwinAusten', 'Godwin Austen')
t = t.replace('NorthWest', 'North West')
t = t.replace('SouthWest', 'South West')
t = t.replace('SouthEast', 'South East')
t = t.replace('NorthEast', 'North East')
t = t.replace('twentyone', 'twenty one')
t = t.replace('snowcapped', 'snow capped')
t = t.replace('seafloor', 'sea floor')
t = t.replace('midnight', 'mid night')
t = t.replace('Saptaseven', 'Sapta seven')
print('After merged words:', repr(t))

# Step 10: run-together words
t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
t = re.sub(r'(\d)([A-Za-z])', r'\1 \2', t)
t = re.sub(r'([a-z])(\d)', r'\1 \2', t)
print('After run-together:', repr(t))

# Step 11: common merged
t = t.replace('Sungod', 'Sun god')
t = t.replace('Earthsatellite', 'Earth satellite')
t = t.replace('Rocketlaunch', 'Rocket launch')
t = t.replace('Earths-twin', 'Earths twin')
print('After common merged:', repr(t))

# Step 12: meaning artifact
t = re.sub(r"meaning'\s*'", 'meaning', t)
print('After meaning:', repr(t))

# Step 13: hyphens to spaces
t = t.replace('-', ' ')
print('After hyphens to spaces:', repr(t))

# Step 14: whitespace
t = re.sub(r'\s+', ' ', t).strip()
print('Final:', repr(t))